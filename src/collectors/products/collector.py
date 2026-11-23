"""AI Product Collector Module.

Collects and validates genuine AI products from verified ecosystems:
- Authoritative foundational AI products registry (OpenAI, Anthropic, Mistral, etc.)
- Hugging Face Spaces interactive application ecosystem (thousands of live AI tools)
- Normalizes pricing models into FREE, FREEMIUM, PAID, ENTERPRISE
- Integrates with Entity Resolution engine for canonical startup mapping
- Checkpointing, resumability, and Pydantic validation
- Traceable source metadata and zero fabricated records
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
from src.collectors.products.seeds import FOUNDATIONAL_AI_PRODUCTS
from src.entity_resolution.resolver import EntityResolver
from src.utils.config import settings
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.validation.schemas import (
    PricingModel,
    ProductContent,
    ProductRecord,
    RecordType,
    SourceMetadata,
)

# Diverse category queries to capture complete spectrum of AI products
DEFAULT_HF_QUERIES = [
    "agent", "chat", "code", "image", "audio", "video", "search", "vision",
    "automation", "assistant", "diffusion", "rag", "summarization", "translation",
    "voice", "transcription", "multimodal", "robotics", "generation", "nlp",
    "embedding", "classification", "detector", "workflow", "reasoning",
    "medical-ai", "fintech", "analytics", "security", "data-cleaning"
]


class ProductCollector(BaseCollector[ProductRecord]):
    """Collector for genuine AI products from software registries and marketplaces."""

    def __init__(
        self,
        source_name: str = "Hugging Face Spaces & AI Product Registry",
        source_base_url: str = "https://huggingface.co/spaces",
        checkpoint_dir: Optional[Path] = None,
        resolver: Optional[EntityResolver] = None,
    ) -> None:
        super().__init__(
            name="product_collector",
            source_name=source_name,
            source_base_url=source_base_url,
            record_type=RecordType.PRODUCT,
        )
        self.checkpoint_dir = checkpoint_dir or Path("data/raw")
        self.checkpoint_file = self.checkpoint_dir / "products_checkpoint.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.resolver = resolver or EntityResolver()

        # Deduplication indices
        self.seen_urls: Set[str] = set()
        self.seen_products: Set[Tuple[str, str]] = set()

        # Telemetry & Audit metrics
        self.total_retrieved = 0
        self.rejection_log: List[Dict[str, str]] = []
        self.source_contribution: Dict[str, int] = defaultdict(int)
        self.pricing_distribution: Dict[str, int] = defaultdict(int)
        self.api_retry_count = 0

    def normalize_pricing(self, raw_pricing: Optional[str]) -> PricingModel:
        """Normalize freeform pricing text into standard PricingModel enum."""
        if not raw_pricing:
            return PricingModel.FREEMIUM
        cleaned = raw_pricing.upper().strip()
        if any(k in cleaned for k in ["ENTERPRISE", "CUSTOM", "TALK TO SALES", "CONTACT SALES"]):
            return PricingModel.ENTERPRISE
        elif any(k in cleaned for k in ["PAID", "SUBSCRIPTION", "$", "MONTHLY", "ANNUAL", "COMMERCIAL"]):
            return PricingModel.PAID
        elif "FREEMIUM" in cleaned:
            return PricingModel.FREEMIUM
        elif "FREE" in cleaned or "OPEN SOURCE" in cleaned:
            return PricingModel.FREE
        return PricingModel.FREEMIUM

    def clean_product_name(self, raw_title: Optional[str], space_id: str) -> str:
        """Strip emojis, decorators, and redundant punctuation from product titles."""
        repo_name = space_id.split("/")[-1].replace("-", " ").replace("_", " ").title()
        if not raw_title:
            return repo_name

        # Strip emojis and leading/trailing special symbols
        cleaned = re.sub(r"[^\w\s\-\.\,\(\)\/]", "", raw_title).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)

        # If stripping leaves nothing or very short string, fallback to repo name
        if len(cleaned) < 2:
            return repo_name
        return cleaned

    def parse_seed_product(self, seed: Dict[str, Any]) -> Optional[ProductRecord]:
        """Convert a foundational startup product into a verified ProductRecord."""
        raw_name = seed["product_name"]
        startup_name = seed["startup_name"]
        product_url = seed["product_url"]

        if product_url in self.seen_urls:
            self.metrics.duplicates_filtered += 1
            return None

        canonical_startup, _ = self.resolver.resolve(startup_name)
        product_key = (canonical_startup.lower(), raw_name.lower())
        if product_key in self.seen_products:
            self.metrics.duplicates_filtered += 1
            return None

        pricing_model = seed.get("pricing_model")
        if isinstance(pricing_model, str):
            pricing_model = self.normalize_pricing(pricing_model)
        elif not isinstance(pricing_model, PricingModel):
            pricing_model = PricingModel.FREEMIUM

        try:
            content = ProductContent(
                productName=raw_name,
                startupName=startup_name,
                canonicalStartupName=canonical_startup,
                pricingModel=pricing_model,
                description=seed.get("description", f"{raw_name} developed by {startup_name}."),
                productUrl=product_url,
            )

            record = ProductRecord(
                source=SourceMetadata(name="Verified Product Registry", url=product_url),
                content=content,
            )

            self.seen_urls.add(product_url)
            self.seen_products.add(product_key)
            self.source_contribution["Verified Product Registry"] += 1
            self.pricing_distribution[pricing_model.value] += 1
            return record

        except ValidationError as err:
            self.rejection_log.append({
                "reason": f"SEED_VALIDATION_ERROR: {str(err)}",
                "product_name": raw_name
            })
            return None

    def parse_hf_space(self, space: Dict[str, Any]) -> Optional[ProductRecord]:
        """Transform a Hugging Face Space object into a validated ProductRecord."""
        space_id = space.get("id", "")
        if not space_id or "/" not in space_id:
            self.rejection_log.append({"reason": "INVALID_SPACE_ID", "raw": str(space_id)})
            return None

        author, repo = space_id.split("/", 1)
        card_data = space.get("cardData") or {}
        raw_title = card_data.get("title") or repo.replace("-", " ").title()
        product_name = self.clean_product_name(raw_title, space_id)

        product_url = f"https://huggingface.co/spaces/{space_id}"

        if product_url in self.seen_urls:
            self.metrics.duplicates_filtered += 1
            return None

        canonical_startup, _ = self.resolver.resolve(author)
        product_key = (canonical_startup.lower(), product_name.lower())
        if product_key in self.seen_products:
            self.metrics.duplicates_filtered += 1
            return None

        # Build informative description
        sdk = space.get("sdk", "gradio")
        tags = space.get("tags") or []
        tag_summary = ", ".join(t for t in tags[:4] if not t.startswith("region:"))
        likes = space.get("likes", 0)

        desc = (
            f"{product_name} is an interactive AI application by {author} built with {sdk}. "
            f"Capabilities include: {tag_summary or 'machine learning inference'}. "
            f"Community appreciation: {likes} likes."
        )

        # Pricing Model determination:
        # HF Spaces provide free community tier with optional paid GPU upgrades -> FREEMIUM
        # If open-source license explicitly specified without proprietary tags -> FREE / FREEMIUM
        tags_str = " ".join(tags).lower()
        if "enterprise" in tags_str:
            pricing = PricingModel.ENTERPRISE
        elif "commercial" in tags_str or "paid" in tags_str:
            pricing = PricingModel.PAID
        elif any(lic in tags_str for lic in ["license:apache-2.0", "license:mit", "license:bsd"]):
            pricing = PricingModel.FREE
        else:
            pricing = PricingModel.FREEMIUM

        try:
            content = ProductContent(
                productName=product_name,
                startupName=author,
                canonicalStartupName=canonical_startup,
                pricingModel=pricing,
                description=desc,
                productUrl=product_url,
            )

            record = ProductRecord(
                source=SourceMetadata(name="Hugging Face Spaces", url=product_url),
                content=content,
            )

            self.seen_urls.add(product_url)
            self.seen_products.add(product_key)
            self.source_contribution["Hugging Face Spaces"] += 1
            self.pricing_distribution[pricing.value] += 1
            return record

        except ValidationError as err:
            self.rejection_log.append({
                "reason": f"VALIDATION_ERROR: {str(err)}",
                "product_name": product_name
            })
            return None

    def load_checkpoint(self) -> List[ProductRecord]:
        """Load previously saved records from checkpoint for resumability."""
        if not self.checkpoint_file.exists():
            return []

        records: List[ProductRecord] = []
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                record = ProductRecord.model_validate(item)
                records.append(record)
                c = record.content
                if c.productUrl:
                    self.seen_urls.add(c.productUrl)
                key = (c.canonicalStartupName.lower() if c.canonicalStartupName else c.startupName.lower(), c.productName.lower())
                self.seen_products.add(key)
                self.pricing_distribution[c.pricingModel.value] += 1
                self.source_contribution[record.source.name] += 1
            logger.info("Resumed from checkpoint: loaded %d product records.", len(records))
        except Exception as err:
            logger.warning("Failed loading product checkpoint: %s", err)

        return records

    def save_checkpoint(self, records: List[ProductRecord]) -> None:
        """Persist current collection state to checkpoint file."""
        try:
            serialized = [r.model_dump(mode="json") for r in records]
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
            logger.debug("Product checkpoint saved: %d records", len(records))
        except Exception as err:
            logger.warning("Failed saving product checkpoint: %s", err)

    def save_datasets(
        self,
        records: List[ProductRecord],
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save collected products to CSV and JSON formats under data directory."""
        target_dir = output_dir or Path("data/processed")
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / "products.json"
        csv_path = target_dir / "products.csv"

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

        # Mirror to data/exports/products.csv
        export_csv = Path("data/exports/products.csv")
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_csv, index=False, encoding="utf-8")

        return json_path, csv_path

    async def collect(
        self,
        limit: Optional[int] = 1000,
        batch_size: int = 100,
        polite_delay_seconds: float = 0.3,
    ) -> List[ProductRecord]:
        """Collect at least limit unique genuine AI products."""
        target = limit or 1000
        logger.info("Starting AI product collection with target=%d", target)

        # 1. Load checkpoint
        collected_records = self.load_checkpoint()
        if len(collected_records) >= target:
            logger.info("Target of %d products already reached from checkpoint (%d available).", target, len(collected_records))
            return collected_records[:target]

        # 2. Ingest foundational AI products
        logger.info("Ingesting foundational AI products from verified registry...")
        for seed in FOUNDATIONAL_AI_PRODUCTS:
            rec = self.parse_seed_product(seed)
            if rec:
                collected_records.append(rec)
                self.total_retrieved += 1

        logger.info("Ingested %d foundational AI products.", len(collected_records))

        # 3. Query Hugging Face Spaces API across diverse AI categories
        session = await self.http_client.get_session()

        # Phase A: Top-liked and trending spaces
        popular_endpoints = [
            f"https://huggingface.co/api/spaces?limit={batch_size}&sort=likes&direction=-1&full=false",
            f"https://huggingface.co/api/spaces?limit={batch_size}&sort=trendingScore&direction=-1&full=false",
            f"https://huggingface.co/api/spaces?limit={batch_size}&sort=downloads&direction=-1&full=false",
        ]

        for ep in popular_endpoints:
            if len(collected_records) >= target:
                break
            try:
                headers = {"User-Agent": settings.USER_AGENT}
                async with session.get(ep, headers=headers) as resp:
                    if resp.status == 200:
                        spaces = await resp.json()
                        self.total_retrieved += len(spaces)
                        for s in spaces:
                            rec = self.parse_hf_space(s)
                            if rec:
                                collected_records.append(rec)
                                if len(collected_records) >= target:
                                    break
                    elif resp.status in (429, 503):
                        logger.warning("HF rate limit / busy (status %d). Backing off...", resp.status)
                        self.api_retry_count += 1
                        await asyncio.sleep(2.0)
            except Exception as err:
                logger.warning("Error querying HF Spaces (%s): %s", ep, err)
                self.api_retry_count += 1

            self.save_checkpoint(collected_records)
            await asyncio.sleep(polite_delay_seconds)

        # Phase B: Category slices
        for cat in DEFAULT_HF_QUERIES:
            if len(collected_records) >= target:
                break

            url = f"https://huggingface.co/api/spaces?search={cat}&limit={batch_size}&full=false"
            logger.info("Fetching HF Spaces slice [%s] (Collected: %d/%d)", cat, len(collected_records), target)

            try:
                headers = {"User-Agent": settings.USER_AGENT}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        spaces = await resp.json()
                        self.total_retrieved += len(spaces)
                        for s in spaces:
                            rec = self.parse_hf_space(s)
                            if rec:
                                collected_records.append(rec)
                                if len(collected_records) >= target:
                                    break
                    elif resp.status in (429, 503):
                        logger.warning("HF rate limit / busy (status %d). Backing off...", resp.status)
                        self.api_retry_count += 1
                        await asyncio.sleep(2.0)
                    else:
                        logger.warning("HF request failed with status %d", resp.status)
            except Exception as err:
                logger.warning("Error querying HF Spaces for [%s]: %s", cat, err)
                self.api_retry_count += 1

            # Checkpoint progress
            self.save_checkpoint(collected_records)
            await asyncio.sleep(polite_delay_seconds)

        self.metrics.records_collected = len(collected_records)
        logger.info(
            "Product collection finished. Successfully acquired %d verified AI products.",
            len(collected_records)
        )
        return collected_records


async def main() -> None:
    """CLI runner for ProductCollector."""
    import argparse
    from src.storage.database import init_db

    parser = argparse.ArgumentParser(description="AI Product Ingestion")
    parser.add_argument("--limit", type=int, default=1000, help="Target number of records (default: 1000)")
    args = parser.parse_args()

    collector = ProductCollector()
    try:
        await init_db()
        records = await collector.collect(limit=args.limit)
        json_path, csv_path = collector.save_datasets(records)
        print(f"\n--- PRODUCT COLLECTION COMPLETE ---")
        print(f"Total retrieved from sources: {collector.total_retrieved}")
        print(f"Total unique validated records: {len(records)}")
        print(f"Pricing breakdown: {dict(collector.pricing_distribution)}")
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
