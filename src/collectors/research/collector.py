"""Research Paper Collector Module.

Collects genuine AI research papers from the official arXiv API:
- Query categories: cs.AI, cs.LG, cs.CL, cs.CV, stat.ML, cs.RO, cs.IR, cs.NE
- Full pagination, request throttling, and retry handling
- Authentic GitHub repository link extraction and GitHub REST API metric enrichment
- Checkpointing for resumable collection
- Strict Pydantic validation and audit rejection logging
- Never fabricates authors, URLs, papers, or GitHub metrics
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET
from pydantic import ValidationError

from src.collectors.base import BaseCollector
from src.utils.config import settings
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.validation.schemas import (
    RecordType,
    ResearchPaperContent,
    ResearchPaperRecord,
    SourceMetadata,
)

# Standard XML namespaces in arXiv Atom feed
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

# Regex for extracting GitHub repository URLs from abstracts, comments, and notes
GITHUB_REPO_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)",
    re.IGNORECASE
)

# Reserved GitHub paths that do not represent valid user repositories
RESERVED_GITHUB_NAMES = {
    "about", "features", "pricing", "security", "login", "join", "topics",
    "collections", "events", "readme", "site", "explore", "trending", "stars"
}
RESERVED_REPO_NAMES = {
    "issues", "pulls", "releases", "commit", "blob", "tree", "branches", "wiki"
}


class ResearchPaperCollector(BaseCollector[ResearchPaperRecord]):
    """Production-grade collector for authentic arXiv AI research papers."""

    def __init__(
        self,
        source_name: str = "arXiv AI",
        source_base_url: str = "https://export.arxiv.org/api/query",
        checkpoint_dir: Optional[Path] = None,
        github_token: Optional[str] = None,
    ) -> None:
        super().__init__(
            name="research_paper_collector",
            source_name=source_name,
            source_base_url=source_base_url,
            record_type=RecordType.RESEARCH_PAPER,
        )
        self.checkpoint_dir = checkpoint_dir or Path("data/raw")
        self.checkpoint_file = self.checkpoint_dir / "arxiv_checkpoint.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.github_token = github_token or settings.GITHUB_TOKEN
        self.github_rate_limited = False

        # Telemetry & Rejection Tracking
        self.total_retrieved = 0
        self.rejection_log: List[Dict[str, str]] = []
        self.github_links_found = 0
        self.github_metrics_verified = 0
        self.api_retry_count = 0

    def clean_text(self, text: Optional[str]) -> str:
        """Normalize line breaks and redundant spaces in extracted text."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def extract_clean_arxiv_id(self, raw_id_url: str) -> str:
        """Extract clean canonical arXiv accession ID from atom:id URL.

        e.g., 'http://arxiv.org/abs/2401.01234v2' -> '2401.01234'
        e.g., 'https://arxiv.org/abs/hep-th/9901001' -> 'hep-th/9901001'
        """
        if "/abs/" in raw_id_url:
            raw = raw_id_url.split("/abs/")[-1].strip()
        else:
            raw = raw_id_url.strip()
        # Remove version suffix like 'v1', 'v2' to ensure canonical uniqueness
        clean_id = re.sub(r"v\d+$", "", raw)
        return clean_id

    def extract_github_url(self, text: str) -> Optional[str]:
        """Extract and sanitize a valid GitHub repository URL from text."""
        if not text:
            return None

        matches = GITHUB_REPO_REGEX.findall(text)
        for owner, repo in matches:
            owner = owner.strip(".,;:)'\"`>/[]")
            repo = repo.strip(".,;:)'\"`>/[]")

            # Remove .git suffix
            if repo.endswith(".git"):
                repo = repo[:-4]

            if not owner or not repo:
                continue

            # Skip reserved GitHub system endpoints
            if owner.lower() in RESERVED_GITHUB_NAMES or repo.lower() in RESERVED_REPO_NAMES:
                continue

            return f"https://github.com/{owner}/{repo}"

        return None

    async def fetch_github_metrics(self, repo_url: str) -> Tuple[Optional[int], Optional[int]]:
        """Fetch verified stars and forks from GitHub REST API.

        Never invents metrics. Returns (None, None) if repo is missing, private, or rate limited.
        """
        if self.github_rate_limited or not repo_url or "github.com" not in repo_url:
            return None, None

        parts = repo_url.rstrip("/").split("github.com/")[-1].split("/")
        if len(parts) < 2:
            return None, None
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": settings.USER_AGENT
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        session = await self.http_client.get_session()
        try:
            async with session.get(api_url, headers=headers) as resp:
                remaining = resp.headers.get("X-RateLimit-Remaining")
                if remaining and int(remaining) == 0:
                    logger.warning("GitHub REST API rate limit reached. Remaining=0. Pausing GitHub queries.")
                    self.github_rate_limited = True
                    return None, None

                if resp.status == 200:
                    data = await resp.json()
                    stars = data.get("stargazers_count")
                    forks = data.get("forks_count")
                    self.github_metrics_verified += 1
                    return stars, forks
                elif resp.status in (403, 429):
                    logger.warning("GitHub API rate limit (HTTP %d). Pausing GitHub queries.", resp.status)
                    self.github_rate_limited = True
                    return None, None
                elif resp.status == 404:
                    logger.debug("GitHub repository not found or private: %s", repo_url)
                    return None, None
        except Exception as err:
            logger.debug("GitHub metrics fetch error for %s: %s", repo_url, str(err))

        return None, None

    def parse_entry(self, entry: ET.Element) -> Optional[ResearchPaperRecord]:
        """Parse an arXiv Atom entry into a validated ResearchPaperRecord."""
        raw_id = entry.find("atom:id", ATOM_NS)
        if raw_id is None or not raw_id.text:
            self.rejection_log.append({"reason": "MISSING_ATOM_ID", "raw": ""})
            return None

        arxiv_id = self.extract_clean_arxiv_id(raw_id.text)
        if not arxiv_id:
            self.rejection_log.append({"reason": "INVALID_ARXIV_ID", "raw": raw_id.text})
            return None

        # Title
        title_elem = entry.find("atom:title", ATOM_NS)
        raw_title = title_elem.text if title_elem is not None else ""
        clean_title = self.clean_text(raw_title)
        if not clean_title:
            self.rejection_log.append({"reason": "EMPTY_TITLE", "arxiv_id": arxiv_id})
            return None

        # Abstract / Summary
        summary_elem = entry.find("atom:summary", ATOM_NS)
        abstract = self.clean_text(summary_elem.text if summary_elem is not None else "")

        # Authors
        authors: List[str] = []
        for author_elem in entry.findall("atom:author", ATOM_NS):
            name_elem = author_elem.find("atom:name", ATOM_NS)
            if name_elem is not None and name_elem.text:
                authors.append(self.clean_text(name_elem.text))

        # Publication date
        published_elem = entry.find("atom:published", ATOM_NS)
        published_date = published_elem.text.strip() if published_elem is not None and published_elem.text else ""

        # Categories
        primary_cat_elem = entry.find("arxiv:primary_category", ATOM_NS)
        primary_category = primary_cat_elem.attrib.get("term", "cs.AI") if primary_cat_elem is not None else "cs.AI"

        categories: List[str] = []
        for cat_elem in entry.findall("atom:category", ATOM_NS):
            term = cat_elem.attrib.get("term")
            if term and term not in categories:
                categories.append(term)

        # Links (Official paper URL and PDF URL)
        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        for link_elem in entry.findall("atom:link", ATOM_NS):
            rel = link_elem.attrib.get("rel")
            title = link_elem.attrib.get("title")
            href = link_elem.attrib.get("href")
            if rel == "alternate" and href:
                paper_url = href.replace("http://", "https://")
            elif (title == "pdf" or link_elem.attrib.get("type") == "application/pdf") and href:
                pdf_url = href.replace("http://", "https://")

        # DOI
        doi_elem = entry.find("arxiv:doi", ATOM_NS)
        doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

        # Comments
        comment_elem = entry.find("arxiv:comment", ATOM_NS)
        comment = self.clean_text(comment_elem.text if comment_elem is not None else "")

        # GitHub URL Discovery
        combined_text = f"{abstract} {comment}"
        github_url = self.extract_github_url(combined_text)

        # Build Domain Object
        try:
            content = ResearchPaperContent(
                record_id=f"arxiv_{arxiv_id}",
                arxiv_id=arxiv_id,
                title=clean_title,
                authors=authors,
                paper_url=paper_url,
                pdf_url=pdf_url,
                primary_category=primary_category,
                categories=categories,
                doi=doi,
                github_url=github_url,
                github_stars=None,
                github_forks=None,
                published_date=published_date,
                abstract=abstract,
                comment=comment or None,
            )
            record = ResearchPaperRecord(
                source=SourceMetadata(name="arXiv", url=paper_url),
                content=content,
            )
            return record
        except ValidationError as err:
            self.rejection_log.append({
                "reason": f"VALIDATION_ERROR: {str(err)}",
                "arxiv_id": arxiv_id
            })
            return None

    def load_checkpoint(self) -> List[ResearchPaperRecord]:
        """Load previously saved records from checkpoint for resumability."""
        if not self.checkpoint_file.exists():
            return []

        records: List[ResearchPaperRecord] = []
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                record = ResearchPaperRecord.model_validate(item)
                records.append(record)
                self.seen_identifiers.add(record.content.arxiv_id or "")
            logger.info("Resumed from checkpoint: loaded %d records from %s", len(records), self.checkpoint_file)
        except Exception as err:
            logger.warning("Failed loading checkpoint from %s: %s", self.checkpoint_file, err)

        return records

    def save_checkpoint(self, records: List[ResearchPaperRecord]) -> None:
        """Persist current collection state to checkpoint file."""
        try:
            serialized = [r.model_dump(mode="json") for r in records]
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2)
            logger.debug("Checkpoint saved: %d records", len(records))
        except Exception as err:
            logger.warning("Failed saving checkpoint: %s", err)

    async def collect(
        self,
        limit: Optional[int] = 1000,
        batch_size: int = 100,
        polite_delay_seconds: float = 2.0,
    ) -> List[ResearchPaperRecord]:
        """Execute complete arXiv data collection with pagination, deduplication, and GitHub enrichment.

        Args:
            limit: Target number of unique validated records to acquire (default 1000).
            batch_size: Number of records per arXiv API query (default 100).
            polite_delay_seconds: Sleep duration between arXiv requests to prevent throttling.

        Returns:
            List of strictly validated, unique ResearchPaperRecord instances.
        """
        target = limit or 1000
        logger.info("Starting arXiv research paper collection with target=%d", target)

        # 1. Load existing records from checkpoint
        collected_records = self.load_checkpoint()
        if len(collected_records) >= target:
            logger.info("Target of %d papers already reached from checkpoint (%d available).", target, len(collected_records))
            return collected_records[:target]

        # 2. Comprehensive AI search query covering all mandatory topics
        # cs.AI (Artificial Intelligence), cs.LG (Machine Learning), cs.CL (NLP),
        # cs.CV (Computer Vision), stat.ML (ML Stats), cs.RO (Robotics), cs.IR (Info Retrieval), cs.NE (Neural/Deep Learning)
        search_query = (
            "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV OR "
            "cat:stat.ML OR cat:cs.RO OR cat:cs.IR OR cat:cs.NE"
        )

        start_index = len(collected_records)
        max_results = batch_size

        while len(collected_records) < target:
            params = {
                "search_query": search_query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "start": start_index,
                "max_results": max_results,
            }

            logger.info(
                "Fetching arXiv batch: start=%d, max_results=%d (Collected: %d/%d)",
                start_index, max_results, len(collected_records), target
            )

            response_xml = await self.http_client.fetch(
                url=self.source_base_url,
                params=params,
                max_retries=4,
                backoff_factor=2.0
            )

            if not response_xml:
                logger.error("Failed to receive response from arXiv at start=%d. Retrying...", start_index)
                self.api_retry_count += 1
                await asyncio.sleep(5.0)
                continue

            try:
                tree = ET.fromstring(response_xml)
            except ET.ParseError as err:
                logger.error("Failed to parse arXiv XML at start=%d: %s", start_index, err)
                self.api_retry_count += 1
                await asyncio.sleep(3.0)
                continue

            entries = tree.findall("atom:entry", ATOM_NS)
            if not entries:
                logger.warning("No entries returned in batch at start=%d. Concluding pagination.", start_index)
                break

            self.total_retrieved += len(entries)
            new_records_in_batch = 0

            for entry in entries:
                record = self.parse_entry(entry)
                if record is None:
                    continue

                arxiv_id = record.content.arxiv_id or ""
                # Strict deduplication check
                if self.is_duplicate(arxiv_id):
                    self.rejection_log.append({
                        "reason": "DUPLICATE_ARXIV_ID",
                        "arxiv_id": arxiv_id
                    })
                    continue

                # GitHub Link Metric Enrichment
                if record.content.github_url:
                    self.github_links_found += 1
                    stars, forks = await self.fetch_github_metrics(record.content.github_url)
                    record.content.github_stars = stars
                    record.content.github_forks = forks

                collected_records.append(record)
                new_records_in_batch += 1

                if len(collected_records) >= target:
                    break

            logger.info(
                "Batch processed: added %d valid records. Total collected: %d/%d",
                new_records_in_batch, len(collected_records), target
            )

            # Persist checkpoint
            self.save_checkpoint(collected_records)

            start_index += len(entries)

            # Polite delay between page requests
            if len(collected_records) < target:
                await asyncio.sleep(polite_delay_seconds)

        self.metrics.records_collected = len(collected_records)
        logger.info(
            "Collection finished. Successfully acquired %d genuine research papers.",
            len(collected_records)
        )
        return collected_records

    def save_datasets(
        self,
        records: List[ResearchPaperRecord],
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save collected research papers to CSV and JSON formats under data directory."""
        target_dir = output_dir or Path("data/processed")
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / "research_papers.json"
        csv_path = target_dir / "research_papers.csv"

        # 1. Save full JSON
        serialized = [r.model_dump(mode="json") for r in records]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)
        logger.info("Saved JSON dataset to %s (%d records)", str(json_path), len(records))

        # 2. Save CSV
        import pandas as pd
        rows = [r.to_export_dict() for r in records]
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info("Saved CSV dataset to %s (%d rows)", str(csv_path), len(df))

        # Also mirror to data/exports/research_papers.csv
        export_csv = Path("data/exports/research_papers.csv")
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_csv, index=False, encoding="utf-8")

        return json_path, csv_path


async def main() -> None:
    """CLI runner for ResearchPaperCollector."""
    import argparse
    from src.storage.database import init_db

    parser = argparse.ArgumentParser(description="arXiv Research Paper Ingestion")
    parser.add_argument("--limit", type=int, default=1000, help="Target number of records (default: 1000)")
    parser.add_argument("--batch-size", type=int, default=100, help="arXiv batch size (default: 100)")
    args = parser.parse_args()

    collector = ResearchPaperCollector()
    try:
        await init_db()
        records = await collector.collect(limit=args.limit, batch_size=args.batch_size)
        json_path, csv_path = collector.save_datasets(records)
        print(f"\n--- COLLECTION COMPLETE ---")
        print(f"Total retrieved from API: {collector.total_retrieved}")
        print(f"Total unique validated records: {len(records)}")
        print(f"Records with GitHub repository links: {collector.github_links_found}")
        print(f"Records with verified GitHub metrics: {collector.github_metrics_verified}")
        print(f"Total rejected records: {len(collector.rejection_log)}")
        print(f"Datasets saved to:")
        print(f" - JSON: {json_path}")
        print(f" - CSV:  {csv_path}")
    finally:
        await collector.close()


if __name__ == "__main__":
    asyncio.run(main())

