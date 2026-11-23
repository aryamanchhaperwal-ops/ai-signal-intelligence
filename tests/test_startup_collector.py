"""Unit tests for StartupCollector, domain normalization, hit parsing, and deduplication."""

from pathlib import Path
import pytest
from src.collectors.startups.collector import StartupCollector
from src.validation.schemas import StartupRecord


SAMPLE_YC_HIT = {
    "id": 12345,
    "name": "Cognitive Robotics Inc",
    "slug": "cognitive-robotics",
    "website": "https://cognitiverobotics.ai",
    "all_locations": "Boston, MA, USA",
    "one_liner": "Autonomous robotic manipulation powered by foundation models.",
    "long_description": "Building end-to-end vision-language-action neural networks for commercial warehouse robotics.",
    "team_size": 35,
    "industry": "Artificial Intelligence",
    "subindustry": "Robotics -> Autonomous Systems",
    "launched_at": 1640995200,  # 2022-01-01
    "tags": ["AI", "Robotics", "Computer Vision", "Machine Learning"],
    "batch": "Winter 2022",
    "stage": "Early",
    "status": "Active",
    "regions": ["United States of America"],
}


class TestStartupCollector:
    """Test suite for StartupCollector parsing, resolution, and deduplication."""

    @pytest.fixture
    def collector(self, tmp_path: Path) -> StartupCollector:
        return StartupCollector(checkpoint_dir=tmp_path)

    def test_normalize_domain(self, collector: StartupCollector):
        assert collector.normalize_domain("https://www.openai.com/research") == "openai.com"
        assert collector.normalize_domain("http://anthropic.com") == "anthropic.com"
        assert collector.normalize_domain("mistral.ai/") == "mistral.ai"
        assert collector.normalize_domain("") == ""
        assert collector.normalize_domain(None) == ""

    def test_parse_seed_startup(self, collector: StartupCollector):
        seed = {
            "canonical_name": "Perplexity AI",
            "aliases": ["Perplexity"],
            "website": "https://perplexity.ai",
            "description": "Conversational AI search engine delivering sourced answers."
        }
        record = collector.parse_seed_startup(seed)
        assert record is not None
        assert isinstance(record, StartupRecord)
        assert record.content.entityName == "Perplexity AI"
        assert record.content.canonicalName == "Perplexity AI"
        assert record.content.official_website == "https://perplexity.ai"
        assert record.content.funding_stage is None
        assert record.content.funding_stage_source is None
        assert record.content.funding_stage_verification_status == "UNAVAILABLE"
        assert "perplexity.ai" in collector.seen_domains

    def test_parse_yc_hit_success(self, collector: StartupCollector):
        record = collector.parse_yc_hit(SAMPLE_YC_HIT)
        assert record is not None
        assert isinstance(record, StartupRecord)
        assert record.content.entityName == "Cognitive Robotics Inc"
        assert record.content.canonicalName is not None
        assert record.content.official_website == "https://cognitiverobotics.ai"
        assert record.content.founding_year == 2022
        assert record.content.data.employeeCount == 35
        assert record.content.headquarters == "Boston, MA, USA"
        assert record.content.accelerator_or_investor == "Y Combinator (Winter 2022)"
        assert record.content.funding_stage == "Early"
        assert record.content.funding_stage_source == "Y Combinator Directory"
        assert record.content.funding_stage_verification_status == "SOURCED"
        assert "cognitiverobotics.ai" in collector.seen_domains

    def test_deduplication_by_domain_and_canonical(self, collector: StartupCollector):
        # First hit succeeds
        rec1 = collector.parse_yc_hit(SAMPLE_YC_HIT)
        assert rec1 is not None

        # Duplicate hit with same domain or canonical name is rejected
        rec2 = collector.parse_yc_hit(SAMPLE_YC_HIT)
        assert rec2 is None
        assert collector.metrics.duplicates_filtered >= 1

    def test_parse_yc_hit_missing_name_rejected(self, collector: StartupCollector):
        bad_hit = {"id": 999, "name": "", "website": "https://bad.com"}
        record = collector.parse_yc_hit(bad_hit)
        assert record is None
        assert len(collector.rejection_log) > 0

    def test_checkpoint_save_and_load(self, collector: StartupCollector):
        rec = collector.parse_yc_hit(SAMPLE_YC_HIT)
        assert rec is not None

        collector.save_checkpoint([rec])
        assert collector.checkpoint_file.exists()

        new_collector = StartupCollector(checkpoint_dir=collector.checkpoint_dir)
        loaded = new_collector.load_checkpoint()
        assert len(loaded) == 1
        assert loaded[0].content.entityName == "Cognitive Robotics Inc"
        assert "cognitiverobotics.ai" in new_collector.seen_domains

    def test_missing_funding_stage_never_defaulted(self, collector: StartupCollector):
        """Ensure missing or null funding stage is never defaulted to 'Early' or 'Growth / Private'."""
        hit_no_stage = dict(SAMPLE_YC_HIT)
        hit_no_stage["stage"] = None
        hit_no_stage["id"] = 99999
        hit_no_stage["slug"] = "no-stage-ai"
        hit_no_stage["name"] = "No Stage AI Inc"
        hit_no_stage["website"] = "https://nostageai.com"

        rec = collector.parse_yc_hit(hit_no_stage)
        assert rec is not None
        assert rec.content.funding_stage is None
        assert rec.content.funding_stage_source is None
        assert rec.content.funding_stage_verification_status == "UNAVAILABLE"
        export_dict = rec.to_export_dict()
        assert export_dict["funding_stage"] == ""
        assert export_dict["funding_stage_source"] == ""
        assert export_dict["funding_stage_verification_status"] == "UNAVAILABLE"
