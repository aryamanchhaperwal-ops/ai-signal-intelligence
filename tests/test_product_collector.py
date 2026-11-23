"""Unit tests for ProductCollector, pricing normalization, space parsing, and deduplication."""

from pathlib import Path
import pytest
from src.collectors.products.collector import ProductCollector
from src.validation.schemas import PricingModel, ProductRecord


SAMPLE_HF_SPACE = {
    "_id": "6abaa43202007344336a78f9",
    "id": "stabilityai/stable-diffusion-3.5-large",
    "author": "stabilityai",
    "cardData": {
        "title": "Stable Diffusion 3.5 Large 🎨",
        "emoji": "🎨",
        "colorFrom": "indigo",
        "colorTo": "pink",
        "sdk": "gradio",
    },
    "sdk": "gradio",
    "likes": 1250,
    "tags": ["diffusion", "image-generation", "license:mit", "region:us"]
}


class TestProductCollector:
    """Test suite for ProductCollector parsing, normalization, resolution, and deduplication."""

    @pytest.fixture
    def collector(self, tmp_path: Path) -> ProductCollector:
        return ProductCollector(checkpoint_dir=tmp_path)

    def test_normalize_pricing(self, collector: ProductCollector):
        assert collector.normalize_pricing("Free Community Tier") == PricingModel.FREE
        assert collector.normalize_pricing("Free") == PricingModel.FREE
        assert collector.normalize_pricing("Freemium model with GPU upgrades") == PricingModel.FREEMIUM
        assert collector.normalize_pricing("Paid subscription $20/mo") == PricingModel.PAID
        assert collector.normalize_pricing("$15 per month") == PricingModel.PAID
        assert collector.normalize_pricing("Enterprise quote talk to sales") == PricingModel.ENTERPRISE
        assert collector.normalize_pricing("Custom pricing") == PricingModel.ENTERPRISE
        assert collector.normalize_pricing(None) == PricingModel.FREEMIUM
        assert collector.normalize_pricing("") == PricingModel.FREEMIUM

    def test_clean_product_name(self, collector: ProductCollector):
        assert collector.clean_product_name("FLUX.1 Schnell ⚡", "black-forest-labs/flux-schnell") == "FLUX.1 Schnell"
        assert collector.clean_product_name("🎨 🔥 ✨", "author/cool-tool") == "Cool Tool"
        assert collector.clean_product_name(None, "org/my-ai-model") == "My Ai Model"
        assert collector.clean_product_name("Claude Assistant", "anthropic/claude") == "Claude Assistant"

    def test_parse_seed_product(self, collector: ProductCollector):
        seed = {
            "product_name": "ChatGPT",
            "startup_name": "OpenAI",
            "pricing_model": PricingModel.FREEMIUM,
            "description": "Conversational generative AI assistant.",
            "product_url": "https://chatgpt.com",
        }
        record = collector.parse_seed_product(seed)
        assert record is not None
        assert isinstance(record, ProductRecord)
        assert record.content.productName == "ChatGPT"
        assert record.content.startupName == "OpenAI"
        assert record.content.canonicalStartupName == "OpenAI"
        assert record.content.pricingModel == PricingModel.FREEMIUM
        assert record.content.productUrl == "https://chatgpt.com"
        assert "https://chatgpt.com" in collector.seen_urls

    def test_parse_hf_space_success(self, collector: ProductCollector):
        record = collector.parse_hf_space(SAMPLE_HF_SPACE)
        assert record is not None
        assert isinstance(record, ProductRecord)
        assert record.content.productName == "Stable Diffusion 3.5 Large"
        assert record.content.startupName == "stabilityai"
        assert record.content.canonicalStartupName == "Stability AI"
        assert record.content.pricingModel in (PricingModel.FREE, PricingModel.FREEMIUM)
        assert record.content.productUrl == "https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large"
        assert "https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large" in collector.seen_urls

    def test_deduplication_by_url_and_product_key(self, collector: ProductCollector):
        rec1 = collector.parse_hf_space(SAMPLE_HF_SPACE)
        assert rec1 is not None

        # Duplicate space with same ID and URL is rejected
        rec2 = collector.parse_hf_space(SAMPLE_HF_SPACE)
        assert rec2 is None
        assert collector.metrics.duplicates_filtered >= 1

    def test_invalid_space_rejected(self, collector: ProductCollector):
        bad_space = {"id": "invalid_no_slash"}
        record = collector.parse_hf_space(bad_space)
        assert record is None
        assert len(collector.rejection_log) > 0

    def test_checkpoint_save_and_load(self, collector: ProductCollector):
        rec = collector.parse_hf_space(SAMPLE_HF_SPACE)
        assert rec is not None

        collector.save_checkpoint([rec])
        assert collector.checkpoint_file.exists()

        new_collector = ProductCollector(checkpoint_dir=collector.checkpoint_dir)
        loaded = new_collector.load_checkpoint()
        assert len(loaded) == 1
        assert loaded[0].content.productName == "Stable Diffusion 3.5 Large"
        assert "https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large" in new_collector.seen_urls
