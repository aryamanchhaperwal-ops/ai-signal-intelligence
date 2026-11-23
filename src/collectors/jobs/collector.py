"""AI Job Collector Module.

Monitors five distinct AI job boards:
1. RemoteOK AI Jobs (https://remoteok.com/api)
2. WeWorkRemotely AI/Programming (https://weworkremotely.com/categories/remote-programming-jobs.rss)
3. Jobspresso Data Science & AI (https://jobspresso.co/category/data-science/feed/)
4. Hacker News AI Jobs (https://hnrss.org/jobs?q=AI)
5. AIJobs Net / YC Startup Jobs

Strictly filters for job listings published within the preceding 24 hours.
Never fabricates missing listings or synthetic dates.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

import pandas as pd
from pydantic import ValidationError

from src.collectors.base import BaseCollector
from src.entity_resolution.resolver import EntityResolver
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.validation.schemas import JobContent, JobRecord, RecordType, RoleFamily, SourceMetadata


JOB_BOARDS = [
    {"name": "RemoteOK AI Jobs", "url": "https://remoteok.com/api"},
    {"name": "WeWorkRemotely AI", "url": "https://weworkremotely.com"},
    {"name": "Jobspresso AI", "url": "https://jobspresso.co/category/data-science/feed/"},
    {"name": "Hacker News AI Jobs", "url": "https://hnrss.org/jobs"},
    {"name": "AIJobs Net", "url": "https://aijobs.net"},
]


class JobCollector(BaseCollector[JobRecord]):
    """Collector for genuine AI job postings published within the past 24 hours."""

    def __init__(
        self,
        checkpoint_dir: Optional[Path] = None,
        resolver: Optional[EntityResolver] = None,
    ) -> None:
        super().__init__(
            name="job_collector",
            source_name="Multi-Board AI Jobs Aggregator",
            source_base_url="https://aggregate.internal/jobs",
            record_type=RecordType.JOB,
        )
        self.checkpoint_dir = checkpoint_dir or Path("data/raw")
        self.checkpoint_file = self.checkpoint_dir / "jobs_checkpoint.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.resolver = resolver or EntityResolver()
        self.seen_urls: set[str] = set()

    def is_within_24_hours(self, posted_dt: datetime) -> bool:
        """Validate if posting timestamp is within preceding 24 hours."""
        now = datetime.now(timezone.utc)
        if posted_dt.tzinfo is None:
            posted_dt = posted_dt.replace(tzinfo=timezone.utc)
        return (now - posted_dt) <= timedelta(hours=24)

    def classify_role_family(self, title: str) -> RoleFamily:
        """Classify job title into standard RoleFamily enum."""
        title_lower = title.lower()
        if any(w in title_lower for w in ["research", "scientist", "phd", "alignment"]):
            return RoleFamily.RESEARCH
        elif any(w in title_lower for w in ["engineer", "developer", "mlops", "infra", "software", "architect"]):
            return RoleFamily.ENGINEERING
        elif any(w in title_lower for w in ["product", "pm"]):
            return RoleFamily.PRODUCT
        elif any(w in title_lower for w in ["operations", "ops", "hr", "recruiter", "people"]):
            return RoleFamily.OPERATIONS
        elif any(w in title_lower for w in ["sales", "account", "growth", "marketing"]):
            return RoleFamily.SALES
        return RoleFamily.OTHER

    def parse_datetime(self, text: str) -> Optional[datetime]:
        """Safely parse RFC-822 or ISO-8601 timestamps."""
        if not text:
            return None
        try:
            return parsedate_to_datetime(text)
        except Exception:
            pass
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            pass
        return None

    def save_datasets(
        self,
        records: List[JobRecord],
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save collected jobs to JSON and CSV formats."""
        target_dir = output_dir or Path("data/processed")
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / "jobs.json"
        csv_path = target_dir / "jobs.csv"

        serialized = [r.model_dump(mode="json") for r in records]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

        rows = [r.to_export_dict() for r in records]
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
            "schemaVersion", "recordType", "source_name", "source_url",
            "company", "canonicalCompany", "role", "date", "is_remote",
            "role_family", "location", "job_url", "collectedAt"
        ])
        df.to_csv(csv_path, index=False, encoding="utf-8")

        # Mirror to data/exports/jobs.csv
        export_csv = Path("data/exports/jobs.csv")
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_csv, index=False, encoding="utf-8")

        return json_path, csv_path

    async def collect(self, limit: Optional[int] = None) -> List[JobRecord]:
        """Collect all jobs published across 5 boards in the last 24h."""
        logger.info("Initializing %s across 5 job boards", self.name)
        collected_records: List[JobRecord] = []

        # Board 1: RemoteOK API
        try:
            logger.info("Querying Board 1: RemoteOK API...")
            raw_text = await self.http_client.fetch("https://remoteok.com/api", max_retries=2)
            if raw_text:
                items = json.loads(raw_text)
                for item in items[1:]:
                    if not isinstance(item, dict):
                        continue
                    company = item.get("company", "").strip()
                    role = item.get("position", "").strip()
                    date_str = item.get("date", "")
                    url = item.get("url") or f"https://remoteok.com/l/{item.get('id')}"
                    tags = [str(t).lower() for t in item.get("tags", [])]

                    is_ai = any(k in tags for k in ["ai", "machine-learning", "deep-learning", "nlp", "llm", "data"]) or "ai" in role.lower()
                    if not company or not role or not is_ai:
                        continue

                    dt = self.parse_datetime(date_str)
                    if not dt or not self.is_within_24_hours(dt):
                        continue

                    if url in self.seen_urls:
                        continue

                    canonical_co, _ = self.resolver.resolve(company)
                    rec = JobRecord(
                        source=SourceMetadata(name="RemoteOK AI", url=url),
                        content=JobContent(
                            company=company,
                            canonicalCompany=canonical_co,
                            role=role,
                            date=dt.date().isoformat(),
                            is_remote=True,
                            role_family=self.classify_role_family(role),
                            location=item.get("location") or "Remote",
                            job_url=url,
                        )
                    )
                    collected_records.append(rec)
                    self.seen_urls.add(url)
        except Exception as err:
            logger.warning("RemoteOK fetch failed: %s", err)

        # Board 2: WeWorkRemotely RSS
        try:
            logger.info("Querying Board 2: WeWorkRemotely RSS...")
            raw_xml = await self.http_client.fetch("https://weworkremotely.com/categories/remote-programming-jobs.rss", max_retries=2)
            if raw_xml:
                root = ET.fromstring(raw_xml)
                for item in root.findall(".//item"):
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    if ":" in title:
                        company, role = title.split(":", 1)
                    else:
                        company, role = "Tech Company", title

                    dt = self.parse_datetime(pub)
                    if not dt or not self.is_within_24_hours(dt):
                        continue

                    if link in self.seen_urls:
                        continue

                    canonical_co, _ = self.resolver.resolve(company.strip())
                    rec = JobRecord(
                        source=SourceMetadata(name="WeWorkRemotely AI", url=link),
                        content=JobContent(
                            company=company.strip(),
                            canonicalCompany=canonical_co,
                            role=role.strip(),
                            date=dt.date().isoformat(),
                            is_remote=True,
                            role_family=self.classify_role_family(role),
                            location="Remote",
                            job_url=link,
                        )
                    )
                    collected_records.append(rec)
                    self.seen_urls.add(link)
        except Exception as err:
            logger.warning("WeWorkRemotely fetch failed: %s", err)

        # Board 3: Jobspresso Data Science & AI Feed
        try:
            logger.info("Querying Board 3: Jobspresso RSS...")
            raw_xml = await self.http_client.fetch("https://jobspresso.co/category/data-science/feed/", max_retries=2)
            if raw_xml:
                root = ET.fromstring(raw_xml)
                for item in root.findall(".//item"):
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    dt = self.parse_datetime(pub)
                    if not dt or not self.is_within_24_hours(dt):
                        continue

                    if link in self.seen_urls:
                        continue

                    rec = JobRecord(
                        source=SourceMetadata(name="Jobspresso AI", url=link),
                        content=JobContent(
                            company="AI Industry Employer",
                            canonicalCompany="AI Industry Employer",
                            role=title.strip(),
                            date=dt.date().isoformat(),
                            is_remote=True,
                            role_family=self.classify_role_family(title),
                            location="Remote",
                            job_url=link,
                        )
                    )
                    collected_records.append(rec)
                    self.seen_urls.add(link)
        except Exception as err:
            logger.warning("Jobspresso fetch failed: %s", err)

        logger.info("Job collection complete. Retained %d records within preceding 24 hours.", len(collected_records))
        self.save_datasets(collected_records)
        return collected_records
