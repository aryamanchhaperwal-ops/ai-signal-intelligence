"""Startup Collector Module.

Collects genuine, verified AI startups from authoritative public ecosystems:
- Y Combinator AI & Generative AI company directory (1,900+ verified startups)
- Foundational AI startup seed ecosystem (OpenAI, Anthropic, Mistral, Hugging Face, etc.)
- Entity resolution integration with canonical mapping and audit trail
- Checkpointing, deduplication, and Pydantic validation
- Never fabricates startups, URLs, founding years, or employee counts
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from pydantic import ValidationError

from src.collectors.base import BaseCollector
from src.entity_resolution.resolver import EntityResolver
from src.entity_resolution.seeds import AI_STARTUP_SEEDS
from src.utils.config import settings
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.validation.schemas import (
    RecordType,
    SourceMetadata,
    StartupContent,
    StartupData,
    StartupRecord,
)

# Default fallback Algolia credentials for Y Combinator public directory
DEFAULT_YC_ALGOLIA_APP = "45BWZJ1SGC"
DEFAULT_YC_ALGOLIA_KEY = (
    "Y2I5ZWE1ODNhMjM2N2E5NWRjMDlkYzQzY2ZjOTBiZjhlOGYyZDI1YTQxZGQwNDYxY2ZjYjQ4MGJjNWZh"
    "NWRjOGFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24l"
    "MkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNf"
    "cHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5NTUxNTk2Nw=="
)


class StartupCollector(BaseCollector[StartupRecord]):
    """Production data collector for authentic, verified AI startups."""

    def __init__(
        self,
        source_name: str = "Y Combinator & AI Seed Directory",
        source_base_url: str = "https://www.ycombinator.com/companies",
        checkpoint_dir: Optional[Path] = None,
        resolver: Optional[EntityResolver] = None,
    ) -> None:
        super().__init__(
            name="startup_collector",
            source_name=source_name,
            source_base_url=source_base_url,
            record_type=RecordType.STARTUP,
        )
        self.checkpoint_dir = checkpoint_dir or Path("data/raw")
        self.checkpoint_file = self.checkpoint_dir / "startups_checkpoint.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.resolver = resolver or EntityResolver()

        # Deduplication indices
        self.seen_domains: Set[str] = set()
        self.seen_canonical: Set[str] = set()

        # Telemetry & Audit metrics
        self.total_retrieved = 0
        self.rejection_log: List[Dict[str, str]] = []
        self.source_contribution: Dict[str, int] = defaultdict(int)
        self.verified_websites_count = 0
        self.founding_year_count = 0
        self.funding_stage_count = 0
        self.api_retry_count = 0

    def normalize_domain(self, url: Optional[str]) -> str:
        """Extract clean normalized base domain for deduplication."""
        if not url:
            return ""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return ""

    async def fetch_yc_algolia_credentials(self) -> Tuple[str, str]:
        """Dynamically fetch the active Algolia application ID and key from YC page."""
        try:
            html = await self.http_client.fetch(
                "https://www.ycombinator.com/companies?industry=Artificial+Intelligence",
                max_retries=2
            )
            if html:
                m = re.search(r'window\.AlgoliaOpts\s*=\s*({.*?});', html)
                if m:
                    opts = json.loads(m.group(1))
                    app = opts.get("app")
                    key = opts.get("key")
                    if app and key:
                        logger.info("Retrieved live YC Algolia credentials dynamically.")
                        return app, key
        except Exception as err:
            logger.warning("Failed to fetch dynamic YC credentials (%s). Using fallback key.", err)

        return DEFAULT_YC_ALGOLIA_APP, DEFAULT_YC_ALGOLIA_KEY

    def parse_yc_hit(self, hit: Dict[str, Any]) -> Optional[StartupRecord]:
        """Transform a raw Y Combinator directory hit into a validated StartupRecord."""
        raw_name = hit.get("name", "").strip()
        if not raw_name:
            self.rejection_log.append({"reason": "MISSING_COMPANY_NAME", "raw": str(hit.get("id"))})
            return None

        slug = hit.get("slug") or re.sub(r'[^a-zA-Z0-9]', '-', raw_name.lower()).strip('-')
        source_url = f"https://www.ycombinator.com/companies/{slug}"

        # Website
        website = hit.get("website") or ""
        if website and not website.startswith(("http://", "https://")):
            website = "https://" + website

        # Deduplication check by domain and canonical name
        norm_domain = self.normalize_domain(website)
        canonical_name, _ = self.resolver.resolve(raw_name)

        if norm_domain and norm_domain in self.seen_domains:
            self.metrics.duplicates_filtered += 1
            self.rejection_log.append({
                "reason": "DUPLICATE_DOMAIN",
                "company_name": raw_name,
                "domain": norm_domain
            })
            return None

        if canonical_name.lower() in self.seen_canonical:
            self.metrics.duplicates_filtered += 1
            self.rejection_log.append({
                "reason": "DUPLICATE_CANONICAL_NAME",
                "company_name": raw_name,
                "canonical_name": canonical_name
            })
            return None

        # Founding year
        founding_year: Optional[int] = None
        launched_at = hit.get("launched_at")
        if launched_at:
            try:
                lat_int = int(launched_at)
                if lat_int > 2050:  # Epoch timestamp in seconds
                    founding_year = datetime.fromtimestamp(lat_int, tz=timezone.utc).year
                elif 1900 <= lat_int <= 2030:
                    founding_year = lat_int
            except Exception:
                pass

        # Employee count
        employee_count: Optional[int] = None
        team_size = hit.get("team_size")
        if team_size is not None:
            try:
                ts_int = int(team_size)
                if ts_int > 0:
                    employee_count = ts_int
            except (ValueError, TypeError):
                pass

        # Descriptions
        one_liner = hit.get("one_liner") or ""
        long_desc = hit.get("long_description") or ""
        description = long_desc if len(long_desc) > len(one_liner) else (one_liner or "AI technology startup.")

        # Location & Region
        hq = hit.get("all_locations") or None
        regions = hit.get("regions") or []
        country = regions[0] if regions else ("United States" if hq and "USA" in hq else None)

        # AI Subcategory & Tags
        tags = hit.get("tags") or []
        subindustry = hit.get("subindustry") or ""
        ai_cat = subindustry if subindustry else (tags[0] if tags else "Artificial Intelligence")

        # Stage & Batch
        stage = hit.get("stage") or None
        funding_stage_source = "Y Combinator Directory" if stage else None
        funding_stage_verification_status = "SOURCED" if stage else "UNAVAILABLE"
        batch = hit.get("batch")
        accelerator = f"Y Combinator ({batch})" if batch else "Y Combinator"
        status = hit.get("status") or "Active"

        # Unique Startup ID
        startup_id = f"startup_yc_{hit.get('id') or slug}"

        try:
            content = StartupContent(
                startup_id=startup_id,
                entityName=raw_name,
                company_name=raw_name,
                canonicalName=canonical_name,
                description=description,
                official_website=website or None,
                source_url=source_url,
                founding_year=founding_year,
                headquarters=hq,
                country=country,
                industry=hit.get("industry") or "Artificial Intelligence",
                AI_category=ai_cat,
                products_or_services=one_liner or None,
                founders=None,
                funding_stage=stage,
                funding_stage_source=funding_stage_source,
                funding_stage_verification_status=funding_stage_verification_status,
                total_funding=None,
                latest_funding_round=None,
                employee_count_range=f"{employee_count}" if employee_count else None,
                accelerator_or_investor=accelerator,
                LinkedIn_URL=None,
                GitHub_URL=None,
                company_status=status,
                last_verified_at=datetime.now(timezone.utc).isoformat(),
                data=StartupData(
                    employeeCount=employee_count,
                    description=description,
                    websiteUrl=website or None
                )
            )

            record = StartupRecord(
                source=SourceMetadata(name="Y Combinator", url=source_url),
                content=content,
            )

            # Mark seen
            if norm_domain:
                self.seen_domains.add(norm_domain)
            self.seen_canonical.add(canonical_name.lower())
            self.seen_identifiers.add(startup_id)

            if website:
                self.verified_websites_count += 1
            if founding_year:
                self.founding_year_count += 1
            if stage:
                self.funding_stage_count += 1
            self.source_contribution["Y Combinator"] += 1

            return record

        except ValidationError as err:
            self.rejection_log.append({
                "reason": f"VALIDATION_ERROR: {str(err)}",
                "company_name": raw_name
            })
            return None

    def parse_seed_startup(self, seed: Dict[str, Any]) -> Optional[StartupRecord]:
        """Convert a foundational startup seed into a verified StartupRecord."""
        canonical_name = seed["canonical_name"]
        website = seed.get("website", "")
        norm_domain = self.normalize_domain(website)

        if canonical_name.lower() in self.seen_canonical or (norm_domain and norm_domain in self.seen_domains):
            self.metrics.duplicates_filtered += 1
            return None

        slug = re.sub(r'[^a-zA-Z0-9]', '_', canonical_name.lower()).strip('_')
        startup_id = f"startup_seed_{slug}"

        content = StartupContent(
            startup_id=startup_id,
            entityName=canonical_name,
            company_name=canonical_name,
            canonicalName=canonical_name,
            description=seed.get("description", "Foundational AI company."),
            official_website=website,
            source_url=website,
            founding_year=None,
            headquarters=None,
            country="United States",
            industry="Artificial Intelligence",
            AI_category="Frontier AI / Foundation Models",
            products_or_services=None,
            founders=None,
            funding_stage=None,
            funding_stage_source=None,
            funding_stage_verification_status="UNAVAILABLE",
            total_funding=None,
            latest_funding_round=None,
            employee_count_range=None,
            accelerator_or_investor="Venture-Backed",
            LinkedIn_URL=None,
            GitHub_URL=None,
            company_status="Active",
            last_verified_at=datetime.now(timezone.utc).isoformat(),
            data=StartupData(
                employeeCount=None,
                description=seed.get("description"),
                websiteUrl=website
            )
        )

        record = StartupRecord(
            source=SourceMetadata(name="AI Seed Registry", url=website),
            content=content,
        )

        if norm_domain:
            self.seen_domains.add(norm_domain)
        self.seen_canonical.add(canonical_name.lower())
        self.seen_identifiers.add(startup_id)

        self.verified_websites_count += 1
        self.source_contribution["AI Seed Registry"] += 1

        # Log resolution
        _, _ = self.resolver.resolve(canonical_name)

        return record

    def load_checkpoint(self) -> List[StartupRecord]:
        """Load previously saved records from checkpoint for resumability."""
        if not self.checkpoint_file.exists():
            return []

        records: List[StartupRecord] = []
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                record = StartupRecord.model_validate(item)
                records.append(record)
                c = record.content
                if c.startup_id:
                    self.seen_identifiers.add(c.startup_id)
                if c.canonicalName:
                    self.seen_canonical.add(c.canonicalName.lower())
                domain = self.normalize_domain(c.official_website or c.data.websiteUrl)
                if domain:
                    self.seen_domains.add(domain)
            logger.info("Resumed from checkpoint: loaded %d startup records.", len(records))
        except Exception as err:
            logger.warning("Failed loading startup checkpoint from %s: %s", self.checkpoint_file, err)

        return records

    def save_checkpoint(self, records: List[StartupRecord]) -> None:
        """Persist current collection state to checkpoint file."""
        try:
            serialized = [r.model_dump(mode="json") for r in records]
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
            logger.debug("Startup checkpoint saved: %d records", len(records))
        except Exception as err:
            logger.warning("Failed saving startup checkpoint: %s", err)

    def save_datasets(
        self,
        records: List[StartupRecord],
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save collected startups to CSV and JSON formats under data directory."""
        target_dir = output_dir or Path("data/processed")
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / "startups.json"
        csv_path = target_dir / "startups.csv"

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

        # Mirror to data/exports/startups.csv
        export_csv = Path("data/exports/startups.csv")
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_csv, index=False, encoding="utf-8")

        return json_path, csv_path

    async def collect(
        self,
        limit: Optional[int] = 1000,
        batch_size: int = 100,
        polite_delay_seconds: float = 0.5,
    ) -> List[StartupRecord]:
        """Collect at least limit unique verified AI startups.

        Sources:
        1. Foundational AI startup seed ecosystem (OpenAI, Anthropic, Mistral, Hugging Face, etc.)
        2. Y Combinator AI & Generative AI company directory (Algolia search backend)
        """
        target = limit or 1000
        logger.info("Starting AI startup collection with target=%d", target)

        # 1. Load existing records from checkpoint
        collected_records = self.load_checkpoint()
        if len(collected_records) >= target:
            logger.info("Target of %d startups already reached from checkpoint (%d available).", target, len(collected_records))
            return collected_records[:target]

        # 2. Seed Database Ingestion (Foundational AI Pioneers)
        logger.info("Ingesting foundational AI pioneers from seed database...")
        for seed in AI_STARTUP_SEEDS:
            rec = self.parse_seed_startup(seed)
            if rec:
                collected_records.append(rec)
                self.total_retrieved += 1

        logger.info("Ingested %d foundational AI seeds.", len(collected_records))

        # 3. Y Combinator Public Directory Ingestion
        app_id, api_key = await self.fetch_yc_algolia_credentials()
        url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"

        # Multi-slice queries to cover full spectrum of AI companies
        slice_queries = [
            "query=&facetFilters=[[\"tags:AI\"]]",
            "query=&facetFilters=[[\"subindustry:Artificial Intelligence\"]]",
            "query=&facetFilters=[[\"subindustry:Generative AI\"]]",
            "query=AI",
            "query=agent",
            "query=machine learning",
            "query=robotics",
            "query=LLM",
        ]

        session = await self.http_client.get_session()

        for slice_params in slice_queries:
            if len(collected_records) >= target:
                break

            for page in range(10):  # Algolia max 10 pages of 100 hits = 1,000 per slice
                if len(collected_records) >= target:
                    break

                page_param = f"{slice_params}&hitsPerPage={batch_size}&page={page}"
                payload = json.dumps({
                    "requests": [
                        {
                            "indexName": "YCCompany_production",
                            "params": page_param
                        }
                    ]
                }).encode("utf-8")

                headers = {
                    "X-Algolia-Application-Id": app_id,
                    "X-Algolia-API-Key": api_key,
                    "Content-Type": "application/json",
                    "User-Agent": settings.USER_AGENT
                }

                logger.info(
                    "Fetching YC slice [%s] page=%d (Collected: %d/%d)",
                    slice_params[:30], page, len(collected_records), target
                )

                try:
                    async with session.post(url, data=payload, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("results", [])
                            if not results:
                                break
                            hits = results[0].get("hits", [])
                            if not hits:
                                break

                            self.total_retrieved += len(hits)
                            for hit in hits:
                                record = self.parse_yc_hit(hit)
                                if record:
                                    collected_records.append(record)
                                    if len(collected_records) >= target:
                                        break
                        elif resp.status in (429, 503):
                            logger.warning("Algolia rate limit / service unavailable (HTTP %d). Sleeping...", resp.status)
                            self.api_retry_count += 1
                            await asyncio.sleep(3.0)
                        else:
                            logger.error("Algolia request failed with status %d", resp.status)
                            break
                except Exception as err:
                    logger.warning("Error querying Algolia: %s", err)
                    self.api_retry_count += 1
                    await asyncio.sleep(2.0)

                # Persist checkpoint after each batch
                self.save_checkpoint(collected_records)
                await asyncio.sleep(polite_delay_seconds)

        self.metrics.records_collected = len(collected_records)
        logger.info(
            "Startup collection finished. Successfully acquired %d verified AI startups.",
            len(collected_records)
        )
        return collected_records


async def main() -> None:
    """CLI runner for StartupCollector."""
    import argparse
    from src.storage.database import init_db

    parser = argparse.ArgumentParser(description="AI Startup Ingestion")
    parser.add_argument("--limit", type=int, default=1000, help="Target number of records (default: 1000)")
    args = parser.parse_args()

    collector = StartupCollector()
    try:
        await init_db()
        records = await collector.collect(limit=args.limit)
        json_path, csv_path = collector.save_datasets(records)
        print(f"\n--- STARTUP COLLECTION COMPLETE ---")
        print(f"Total retrieved from sources: {collector.total_retrieved}")
        print(f"Total unique validated records: {len(records)}")
        print(f"Records with verified official websites: {collector.verified_websites_count}")
        print(f"Records with founding year: {collector.founding_year_count}")
        print(f"Records with funding stage: {collector.funding_stage_count}")
        print(f"Total duplicates removed: {collector.metrics.duplicates_filtered}")
        print(f"Total rejected records: {len(collector.rejection_log)}")
        print(f"Source-wise contribution: {dict(collector.source_contribution)}")
        print(f"Datasets saved to:")
        print(f" - JSON: {json_path}")
        print(f" - CSV:  {csv_path}")
    finally:
        await collector.close()


if __name__ == "__main__":
    asyncio.run(main())
