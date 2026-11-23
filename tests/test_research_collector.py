"""Unit tests for ResearchPaperCollector, XML parsing, GitHub extraction, and checkpointing."""

from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from src.collectors.research.collector import ResearchPaperCollector
from src.validation.schemas import ResearchPaperRecord


SAMPLE_ENTRY_XML = """
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
    <id>http://arxiv.org/abs/2401.09999v2</id>
    <title>
        Scalable Diffusion Models for Video Generation: A Comprehensive Study
    </title>
    <summary>
        Recent advancements in diffusion architectures demonstrate superior fidelity.
        Our open-source code and model weights are released at https://github.com/sample-ai-lab/video-diffusion.
    </summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <published>2024-01-18T14:30:00Z</published>
    <arxiv:primary_category term="cs.CV"/>
    <category term="cs.CV"/>
    <category term="cs.AI"/>
    <category term="cs.LG"/>
    <link rel="alternate" href="http://arxiv.org/abs/2401.09999v2" type="text/html"/>
    <link rel="related" href="http://arxiv.org/pdf/2401.09999v2" type="application/pdf" title="pdf"/>
    <arxiv:doi>10.1145/3343031.3350926</arxiv:doi>
    <arxiv:comment>Accepted to CVPR 2024; code at github.com/sample-ai-lab/video-diffusion</arxiv:comment>
</entry>
"""


class TestResearchPaperCollector:
    """Test suite for arXiv paper parser and collector logic."""

    @pytest.fixture
    def collector(self, tmp_path: Path) -> ResearchPaperCollector:
        return ResearchPaperCollector(checkpoint_dir=tmp_path)

    def test_clean_text(self, collector: ResearchPaperCollector):
        raw = "  Diffusion   Models\n\nwith Attention \t "
        cleaned = collector.clean_text(raw)
        assert cleaned == "Diffusion Models with Attention"

    def test_extract_clean_arxiv_id(self, collector: ResearchPaperCollector):
        raw_url = "http://arxiv.org/abs/2401.09999v2"
        arxiv_id = collector.extract_clean_arxiv_id(raw_url)
        assert arxiv_id == "2401.09999"

        raw_url2 = "https://arxiv.org/abs/hep-th/9901001"
        assert collector.extract_clean_arxiv_id(raw_url2) == "hep-th/9901001"

    def test_extract_github_url(self, collector: ResearchPaperCollector):
        text = "Our implementation is available at https://github.com/openai/whisper. Check it out!"
        github_url = collector.extract_github_url(text)
        assert github_url == "https://github.com/openai/whisper"

        # Trailing punctuation removal
        text_punct = "See code (https://github.com/meta-llama/llama3)."
        assert collector.extract_github_url(text_punct) == "https://github.com/meta-llama/llama3"

        # Trailing .git removal
        text_git = "Clone at https://github.com/huggingface/transformers.git"
        assert collector.extract_github_url(text_git) == "https://github.com/huggingface/transformers"

        # Reserved system paths should be ignored
        text_reserved = "Visit https://github.com/features or https://github.com/pricing for details"
        assert collector.extract_github_url(text_reserved) is None

        # Text without github link
        assert collector.extract_github_url("No repository mentioned in this paper.") is None

    def test_parse_entry_success(self, collector: ResearchPaperCollector):
        entry = ET.fromstring(SAMPLE_ENTRY_XML)
        record = collector.parse_entry(entry)

        assert record is not None
        assert isinstance(record, ResearchPaperRecord)
        assert record.content.arxiv_id == "2401.09999"
        assert record.content.record_id == "arxiv_2401.09999"
        assert "Scalable Diffusion Models" in record.content.title
        assert record.content.authors == ["Alice Smith", "Bob Jones"]
        assert record.content.primary_category == "cs.CV"
        assert "cs.AI" in record.content.categories
        assert record.content.paper_url == "https://arxiv.org/abs/2401.09999v2"
        assert record.content.pdf_url == "https://arxiv.org/pdf/2401.09999v2"
        assert record.content.doi == "10.1145/3343031.3350926"
        assert record.content.github_url == "https://github.com/sample-ai-lab/video-diffusion"

    def test_parse_entry_missing_id_rejected(self, collector: ResearchPaperCollector):
        malformed = "<entry xmlns='http://www.w3.org/2005/Atom'><title>No ID</title></entry>"
        entry = ET.fromstring(malformed)
        record = collector.parse_entry(entry)
        assert record is None
        assert len(collector.rejection_log) > 0

    def test_deduplication(self, collector: ResearchPaperCollector):
        arxiv_id = "2401.00001"
        assert collector.is_duplicate(arxiv_id) is False
        assert collector.is_duplicate(arxiv_id) is True
        assert collector.metrics.duplicates_filtered == 1

    def test_checkpoint_save_and_load(self, collector: ResearchPaperCollector):
        entry = ET.fromstring(SAMPLE_ENTRY_XML)
        record = collector.parse_entry(entry)
        assert record is not None

        # Save checkpoint
        collector.save_checkpoint([record])
        assert collector.checkpoint_file.exists()

        # Load in a fresh collector instance
        new_collector = ResearchPaperCollector(checkpoint_dir=collector.checkpoint_dir)
        loaded = new_collector.load_checkpoint()
        assert len(loaded) == 1
        assert loaded[0].content.arxiv_id == "2401.09999"
        assert "2401.09999" in new_collector.seen_identifiers
