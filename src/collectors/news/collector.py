"""AI News Collector Module.

Monitors five distinct AI news sources:
1. VentureBeat AI (https://venturebeat.com/category/ai/feed/)
2. TechCrunch AI (https://techcrunch.com/category/artificial-intelligence/feed/)
3. MIT Technology Review AI (https://www.technologyreview.com/topic/artificial-intelligence/feed/)
4. The Verge AI (https://www.theverge.com/rss/ai-artificial-intelligence/index.xml)
5. Ars Technica AI (https://feeds.arstechnica.com/arstechnica/technology-lab)

Strictly filters for articles published within the preceding 24 hours.
Never fabricates missing records or synthetic publication dates.
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
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.validation.schemas import NewsContent, NewsRecord, RecordType, SourceMetadata

NEWS_SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "site": "https://techcrunch.com"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "site": "https://venturebeat.com"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "site": "https://theverge.com"},
    {"name": "Ars Technica AI", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "site": "https://arstechnica.com"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "site": "https://technologyreview.com"},
]


class NewsCollector(BaseCollector[NewsRecord]):
    """Collector for genuine AI news published within the past 24 hours."""

    def __init__(
        self,
        checkpoint_dir: Optional[Path] = None,
    ) -> None:
        super().__init__(
            name="news_collector",
            source_name="Multi-Source AI News Hub",
            source_base_url="https://aggregate.internal/news",
            record_type=RecordType.NEWS,
        )
        self.checkpoint_dir = checkpoint_dir or Path("data/raw")
        self.checkpoint_file = self.checkpoint_dir / "news_checkpoint.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.seen_urls: set[str] = set()

    def is_within_24_hours(self, published_dt: datetime) -> bool:
        """Validate if timestamp is within preceding 24 hours."""
        now = datetime.now(timezone.utc)
        if published_dt.tzinfo is None:
            published_dt = published_dt.replace(tzinfo=timezone.utc)
        return (now - published_dt) <= timedelta(hours=24)

    def parse_datetime(self, text: str) -> Optional[datetime]:
        """Safely parse RFC-822 or ISO-8601 publication dates."""
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
        records: List[NewsRecord],
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save collected news to JSON and CSV formats."""
        target_dir = output_dir or Path("data/processed")
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / "news.json"
        csv_path = target_dir / "news.csv"

        serialized = [r.model_dump(mode="json") for r in records]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

        rows = [r.to_export_dict() for r in records]
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
            "schemaVersion", "recordType", "source_name", "source_url",
            "title", "url", "published_date", "summary", "full_text_length", "collectedAt"
        ])
        df.to_csv(csv_path, index=False, encoding="utf-8")

        # Mirror to data/exports/news.csv
        export_csv = Path("data/exports/news.csv")
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_csv, index=False, encoding="utf-8")

        return json_path, csv_path

    async def collect(self, limit: Optional[int] = None) -> List[NewsRecord]:
        """Collect all news articles published across 5 sources in the last 24h."""
        logger.info("Initializing %s across %d news sources", self.name, len(NEWS_SOURCES))
        collected_records: List[NewsRecord] = []

        for src in NEWS_SOURCES:
            name = src["name"]
            url = src["url"]
            logger.info("Querying news feed: %s (%s)", name, url)
            try:
                xml_data = await self.http_client.fetch(url, max_retries=2)
                if not xml_data:
                    logger.warning("Empty response from %s", name)
                    continue

                root = ET.fromstring(xml_data)
                items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for item in items:
                    title_elem = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

                    link_elem = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
                    link = ""
                    if link_elem is not None:
                        link = link_elem.attrib.get("href") or link_elem.text or ""

                    pub_elem = (
                        item.find("pubDate")
                        or item.find("{http://www.w3.org/2005/Atom}published")
                        or item.find("{http://www.w3.org/2005/Atom}updated")
                    )
                    pub_str = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""
                    pub_dt = self.parse_datetime(pub_str)

                    desc_elem = (
                        item.find("description")
                        or item.find("{http://www.w3.org/2005/Atom}summary")
                        or item.find("{http://www.w3.org/2005/Atom}content")
                    )
                    summary = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                    if not title or not link or not pub_dt:
                        continue

                    if link in self.seen_urls:
                        continue

                    # Strict 24-hour window filter
                    if not self.is_within_24_hours(pub_dt):
                        continue

                    try:
                        rec = NewsRecord(
                            source=SourceMetadata(name=name, url=url),
                            content=NewsContent(
                                title=title,
                                url=link,
                                published_date=pub_dt.isoformat(),
                                summary=summary[:1000] if summary else "AI news coverage.",
                                full_text_length=len(summary),
                            ),
                        )
                        collected_records.append(rec)
                        self.seen_urls.add(link)
                    except ValidationError:
                        pass

            except Exception as err:
                logger.warning("Failed parsing feed %s: %s", name, err)

        logger.info("News collection complete. Retained %d records within preceding 24 hours.", len(collected_records))
        self.save_datasets(collected_records)
        return collected_records
