"""Unit tests for Excel and CSV Exporters."""

from pathlib import Path
import openpyxl
import pytest
from src.entity_resolution.resolver import EntityResolver
from src.exporters.excel import ExcelExporter
from src.validation.schemas import (
    JobContent,
    JobRecord,
    NewsContent,
    NewsRecord,
    PricingModel,
    ProductContent,
    ProductRecord,
    ResearchPaperContent,
    ResearchPaperRecord,
    RoleFamily,
    SourceMetadata,
    StartupContent,
    StartupData,
    StartupRecord,
)


class TestExcelExporter:
    """Verify generated Excel workbook has all 6 required tabs and proper headers."""

    def test_export_all_six_tabs(self, tmp_path: Path):
        exporter = ExcelExporter(output_dir=tmp_path)
        resolver = EntityResolver()
        resolver.resolve("OpenAI, Inc.")

        dummy_startup = StartupRecord(
            source=SourceMetadata(name="YC", url="https://ycombinator.com"),
            content=StartupContent(
                entityName="OpenAI, Inc.",
                canonicalName="OpenAI",
                data=StartupData(employeeCount=1200)
            )
        )
        dummy_product = ProductRecord(
            source=SourceMetadata(name="PH", url="https://producthunt.com"),
            content=ProductContent(
                productName="ChatGPT",
                startupName="OpenAI",
                pricingModel=PricingModel.FREEMIUM
            )
        )
        dummy_paper = ResearchPaperRecord(
            source=SourceMetadata(name="Arxiv", url="https://arxiv.org"),
            content=ResearchPaperContent(
                title="Transformers",
                authors=["Vaswani"],
                paper_url="https://arxiv.org/abs/1706.03762",
                published_date="2017-06-12"
            )
        )
        dummy_job = JobRecord(
            source=SourceMetadata(name="Board", url="https://jobs.example"),
            content=JobContent(
                company="OpenAI",
                role="Research Scientist",
                date="2026-11-23",
                is_remote=True,
                role_family=RoleFamily.RESEARCH
            )
        )
        dummy_news = NewsRecord(
            source=SourceMetadata(name="TechCrunch", url="https://techcrunch.com"),
            content=NewsContent(
                title="AI Milestone",
                url="https://techcrunch.com/article",
                published_date="2026-11-23"
            )
        )

        excel_file = exporter.export_all(
            startups=[dummy_startup],
            products=[dummy_product],
            papers=[dummy_paper],
            jobs=[dummy_job],
            news=[dummy_news],
            logs=resolver.get_logs(),
            filename="test_intelligence.xlsx"
        )

        assert excel_file.exists()

        # Load workbook and inspect tabs
        wb = openpyxl.load_workbook(excel_file)
        expected_sheets = [
            "Startups",
            "Products",
            "Research Papers",
            "Jobs",
            "News",
            "Entity Mapping Log",
        ]
        assert wb.sheetnames == expected_sheets

        # Inspect Startups tab
        ws_startups = wb["Startups"]
        headers = [cell.value for cell in ws_startups[1]]
        assert "entityName" in headers
        assert "canonicalName" in headers
        assert "employeeCount" in headers
        assert ws_startups.cell(row=2, column=headers.index("canonicalName") + 1).value == "OpenAI"

        # Inspect Entity Mapping Log tab
        ws_log = wb["Entity Mapping Log"]
        log_headers = [cell.value for cell in ws_log[1]]
        assert "rawName" in log_headers
        assert "canonicalName" in log_headers
        assert "confidenceScore" in log_headers
        assert ws_log.cell(row=2, column=log_headers.index("rawName") + 1).value == "OpenAI, Inc."
