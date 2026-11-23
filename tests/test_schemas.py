"""Unit tests for Pydantic domain schemas and export adapters."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from src.validation.schemas import (
    EntityResolutionLog,
    JobContent,
    JobRecord,
    NewsContent,
    NewsRecord,
    PricingModel,
    ProductContent,
    ProductRecord,
    RecordType,
    ResearchPaperContent,
    ResearchPaperRecord,
    RoleFamily,
    SourceMetadata,
    StartupContent,
    StartupData,
    StartupRecord,
)


@pytest.mark.schemas
class TestStartupRecord:
    """Test Startup schema validation and serialization."""

    def test_valid_startup_record(self):
        record = StartupRecord(
            source=SourceMetadata(name="YC Directory", url="https://ycombinator.com/companies"),
            content=StartupContent(
                entityName="OpenAI, Inc.",
                canonicalName="OpenAI",
                data=StartupData(employeeCount=1200, websiteUrl="https://openai.com", description="AI Research")
            )
        )
        assert record.recordType == RecordType.STARTUP
        assert record.content.entityName == "OpenAI, Inc."
        assert record.content.data.employeeCount == 1200

        export_dict = record.to_export_dict()
        assert export_dict["entityName"] == "OpenAI, Inc."
        assert export_dict["canonicalName"] == "OpenAI"
        assert export_dict["employeeCount"] == 1200
        assert "collectedAt" in export_dict

    def test_startup_record_null_employee_count(self):
        """Null employee count must be preserved without error."""
        record = StartupRecord(
            source=SourceMetadata(name="Registry", url="https://example.com"),
            content=StartupContent(
                entityName="Stealth AI",
                data=StartupData(employeeCount=None)
            )
        )
        assert record.content.data.employeeCount is None
        export_dict = record.to_export_dict()
        assert export_dict["employeeCount"] is None

    def test_invalid_negative_employee_count(self):
        """Negative employee counts must raise validation error."""
        with pytest.raises(ValidationError):
            StartupRecord(
                source=SourceMetadata(name="Registry", url="https://example.com"),
                content=StartupContent(
                    entityName="Bad Count AI",
                    data=StartupData(employeeCount=-5)
                )
            )


@pytest.mark.schemas
class TestProductRecord:
    """Test Product schema validation and pricing models."""

    @pytest.mark.parametrize("pricing", [
        PricingModel.FREE,
        PricingModel.FREEMIUM,
        PricingModel.PAID,
        PricingModel.ENTERPRISE,
    ])
    def test_product_pricing_models(self, pricing: PricingModel):
        record = ProductRecord(
            source=SourceMetadata(name="ProductHunt", url="https://producthunt.com"),
            content=ProductContent(
                productName="Claude Artifacts",
                startupName="Anthropic",
                pricingModel=pricing,
                description="Interactive artifacts in Claude"
            )
        )
        assert record.content.pricingModel == pricing
        export_dict = record.to_export_dict()
        assert export_dict["pricingModel"] == pricing.value

    def test_invalid_pricing_model(self):
        with pytest.raises(ValidationError):
            ProductRecord(
                source=SourceMetadata(name="ProductHunt", url="https://producthunt.com"),
                content=ProductContent(
                    productName="Invalid Product",
                    startupName="Anthropic",
                    pricingModel="NON_EXISTENT_TIER"  # type: ignore
                )
            )


@pytest.mark.schemas
class TestResearchPaperRecord:
    """Test Research Paper schema validation and GitHub star metrics."""

    def test_valid_paper_with_github_stars(self):
        record = ResearchPaperRecord(
            source=SourceMetadata(name="Arxiv", url="https://export.arxiv.org/api/query"),
            content=ResearchPaperContent(
                title="Attention Is All You Need",
                authors=["Vaswani et al."],
                paper_url="https://arxiv.org/abs/1706.03762",
                github_url="https://github.com/tensorflow/tensor2tensor",
                github_stars=12500,
                published_date="2017-06-12"
            )
        )
        assert record.content.github_stars == 12500
        export_dict = record.to_export_dict()
        assert export_dict["github_stars"] == 12500
        assert export_dict["github_url"] == "https://github.com/tensorflow/tensor2tensor"

    def test_paper_without_github_metrics(self):
        """Papers without repository must store None/empty without inventing values."""
        record = ResearchPaperRecord(
            source=SourceMetadata(name="Arxiv", url="https://export.arxiv.org/api/query"),
            content=ResearchPaperContent(
                title="Theoretical Convergence of SGD",
                authors=["Jane Doe"],
                paper_url="https://arxiv.org/abs/2401.00001",
                github_url=None,
                github_stars=None,
                published_date="2024-01-01"
            )
        )
        assert record.content.github_url is None
        assert record.content.github_stars is None
        export_dict = record.to_export_dict()
        assert export_dict["github_stars"] == ""


@pytest.mark.schemas
class TestJobRecord:
    """Test Job posting schema validation."""

    def test_valid_job_record(self):
        record = JobRecord(
            source=SourceMetadata(name="AIJobs.net", url="https://aijobs.net"),
            content=JobContent(
                company="Mistral AI",
                role="Senior LLM Optimization Engineer",
                date=datetime.now(timezone.utc).isoformat(),
                is_remote=True,
                role_family=RoleFamily.ENGINEERING,
                location="Paris, France / Remote"
            )
        )
        assert record.content.is_remote is True
        assert record.content.role_family == RoleFamily.ENGINEERING
        export_dict = record.to_export_dict()
        assert export_dict["role_family"] == "ENGINEERING"
        assert export_dict["is_remote"] is True


@pytest.mark.schemas
class TestNewsRecord:
    """Test News article schema validation."""

    def test_valid_news_record(self):
        record = NewsRecord(
            source=SourceMetadata(name="TechCrunch AI", url="https://techcrunch.com/category/artificial-intelligence/"),
            content=NewsContent(
                title="New Frontier LLM Benchmark Released",
                url="https://techcrunch.com/2026/11/23/new-frontier-llm-benchmark/",
                full_text="Artificial intelligence labs have announced...",
                summary="New benchmark measures reasoning performance.",
                published_date="2026-11-23T10:00:00Z"
            )
        )
        assert record.content.title == "New Frontier LLM Benchmark Released"
        export_dict = record.to_export_dict()
        assert export_dict["full_text_length"] > 0
