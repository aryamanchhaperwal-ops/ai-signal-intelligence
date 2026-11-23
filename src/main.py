"""AI Signal Intelligence Engine Entrypoint.

CLI command center for orchestrating data collection, entity resolution,
validation, storage, and automated workbook generation.
"""

import argparse
import asyncio
from pathlib import Path
import sys
from typing import Optional
from src.collectors.jobs.collector import JobCollector
from src.collectors.news.collector import NewsCollector
from src.collectors.products.collector import ProductCollector
from src.collectors.research.collector import ResearchPaperCollector
from src.collectors.startups.collector import StartupCollector
from src.entity_resolution.resolver import EntityResolver
from src.exporters.excel import ExcelExporter
from src.storage.database import init_db
from src.utils.config import settings
from src.utils.logging import logger, setup_logging


async def run_pipeline(
    limit: Optional[int] = None,
    export_excel: bool = True,
    dry_run: bool = False,
    collect_research: bool = False,
    collect_startups: bool = False,
) -> None:
    """Execute end-to-end intelligence collection pipeline."""
    logger.info("Starting AI Signal Intelligence Pipeline in env=%s", settings.APP_ENV)

    # 1. Initialize Database
    try:
        await init_db()
    except Exception as err:
        logger.error("Database initialization failed: %s", err)

    # 2. Initialize Entity Resolver
    resolver = EntityResolver()
    logger.info("Entity Resolver initialized with %d canonical seeds", len(resolver.canonical_names))

    # 3. Instantiate Collectors
    collectors = {
        "startups": StartupCollector(),
        "products": ProductCollector(),
        "research": ResearchPaperCollector(),
        "news": NewsCollector(),
        "jobs": JobCollector(),
    }

    if dry_run:
        logger.info("Dry run requested. Collectors initialized and validated successfully.")
        return

    papers = []
    if collect_research:
        research_limit = limit or 1000
        logger.info("Executing Research Paper Collector targeting %d records...", research_limit)
        papers = await collectors["research"].collect(limit=research_limit)
        collectors["research"].save_datasets(papers)
        logger.info("Research paper collection completed. Total records: %d", len(papers))
    elif Path("data/processed/research_papers.json").exists():
        import json
        from src.validation.schemas import ResearchPaperRecord
        try:
            with open("data/processed/research_papers.json", "r", encoding="utf-8") as f:
                papers = [ResearchPaperRecord.model_validate(p) for p in json.load(f)]
            logger.info("Loaded %d existing research papers for workbook export.", len(papers))
        except Exception as err:
            logger.warning("Failed loading research papers: %s", err)

    startups = []
    if collect_startups:
        startup_limit = limit or 1000
        logger.info("Executing Startup Collector targeting %d records...", startup_limit)
        startups = await collectors["startups"].collect(limit=startup_limit)
        collectors["startups"].save_datasets(startups)
        logger.info("Startup collection completed. Total records: %d", len(startups))
    elif Path("data/processed/startups.json").exists():
        import json
        from src.validation.schemas import StartupRecord
        try:
            with open("data/processed/startups.json", "r", encoding="utf-8") as f:
                startups = [StartupRecord.model_validate(s) for s in json.load(f)]
            logger.info("Loaded %d existing startups for workbook export.", len(startups))
        except Exception as err:
            logger.warning("Failed loading startups: %s", err)

    # 4. Generate Initial or Updated Workbook
    if export_excel:
        exporter = ExcelExporter()
        output_file = exporter.export_all(
            startups=startups,
            products=[],
            papers=papers,
            jobs=[],
            news=[],
            logs=resolver.get_logs(),
            filename="ai_signal_intelligence.xlsx"
        )
        logger.info("Export completed: %s", str(output_file))


def main() -> None:
    """CLI Parser."""
    parser = argparse.ArgumentParser(description="AI Signal Intelligence Engine CLI")
    parser.add_argument("--limit", type=int, default=None, help="Record limit per collector")
    parser.add_argument("--collect-research", action="store_true", help="Execute arXiv research paper collection")
    parser.add_argument("--collect-startups", action="store_true", help="Execute AI startup collection")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration and exit")
    parser.add_argument("--no-export", action="store_true", help="Disable Excel export generation")
    args = parser.parse_args()

    setup_logging(level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    asyncio.run(
        run_pipeline(
            limit=args.limit,
            export_excel=not args.no_export,
            dry_run=args.dry_run,
            collect_research=args.collect_research,
            collect_startups=args.collect_startups,
        )
    )


if __name__ == "__main__":
    main()
