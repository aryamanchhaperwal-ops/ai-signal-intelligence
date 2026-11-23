"""Unit tests for LLM interface, chunking, and grounding verification."""

import pytest
from pydantic import BaseModel, Field
from src.llm.client import ResilientLLMClient
from src.llm.providers import MockLLMProvider


class SampleExtractionSchema(BaseModel):
    company: str = Field(default="")
    valuation: str = Field(default="")


class TestLLMClient:
    """Test resilient LLM orchestrator behavior."""

    @pytest.fixture
    def mock_client(self) -> ResilientLLMClient:
        mock_provider = MockLLMProvider(
            mock_responses={"company": "Anthropic", "valuation": "$18B"}
        )
        return ResilientLLMClient(providers=[mock_provider], max_chunk_chars=100)

    def test_chunk_text_under_limit(self, mock_client: ResilientLLMClient):
        text = "Short paragraph well under 100 characters."
        chunks = mock_client.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_over_limit(self, mock_client: ResilientLLMClient):
        text = (
            "Paragraph one is relatively long and contains detailed statements about AI.\n\n"
            "Paragraph two contains further analysis of market capitalization and revenue.\n\n"
            "Paragraph three concludes the document."
        )
        chunks = mock_client.chunk_text(text)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) > 0

    def test_grounding_validation(self, mock_client: ResilientLLMClient):
        source = "Anthropic is headquartered in San Francisco with 1200 employees."
        # Present in source -> True
        assert mock_client.validate_grounding("Anthropic", source) is True
        assert mock_client.validate_grounding("San Francisco", source) is True
        # Not present in source -> False (hallucination detected)
        assert mock_client.validate_grounding("Google DeepMind", source) is False
        assert mock_client.validate_grounding("New York", source) is False

    @pytest.mark.asyncio
    async def test_extract_with_fallback_success(self, mock_client: ResilientLLMClient):
        result = await mock_client.extract_with_fallback(
            prompt="Extract company",
            source_text="Anthropic announced new developments.",
            schema=SampleExtractionSchema
        )
        assert result is not None
        assert isinstance(result, SampleExtractionSchema)
        assert result.company == "Anthropic"
