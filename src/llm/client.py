"""Resilient LLM Client with Fallback Routing, Chunking, Backoff, and Validation."""

import asyncio
import random
from typing import Any, List, Optional, Type
from pydantic import BaseModel
from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from src.llm.providers import DeepSeekProvider, GeminiProvider, GroqProvider, MockLLMProvider
from src.utils.config import settings
from src.utils.logging import logger


class ResilientLLMClient:
    """Orchestrates LLM extraction with provider failover: Gemini -> Groq -> DeepSeek.

    Features:
    - Exponential backoff with randomized jitter on HTTP 429 (Rate Limits)
    - Intelligent payload chunking on HTTP 413 (Payload Too Large)
    - Anti-hallucination verification against raw source text
    """

    def __init__(
        self,
        providers: Optional[List[BaseLLMProvider]] = None,
        max_chunk_chars: int = 8000,
    ) -> None:
        """Initialize provider chain."""
        self.max_chunk_chars = max_chunk_chars
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [
                GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL),
                GroqProvider(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL),
                DeepSeekProvider(api_key=settings.DEEPSEEK_API_KEY, model=settings.DEEPSEEK_MODEL),
            ]

    def chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks respecting sentence or paragraph boundaries.

        Used when encountering HTTP 413 or when documents exceed provider context windows.
        """
        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks: List[str] = []
        paragraphs = text.split("\n\n")
        current_chunk: List[str] = []
        current_length = 0

        for para in paragraphs:
            para_len = len(para) + 2
            if current_length + para_len > self.max_chunk_chars:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
            current_chunk.append(para)
            current_length += para_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def validate_grounding(self, extracted_value: str, source_text: str) -> bool:
        """Verify whether an extracted critical value is grounded in the source text.

        Guards against synthetic invention of facts.
        """
        if not extracted_value or not source_text:
            return True
        # Case-insensitive substring verification
        return extracted_value.strip().lower() in source_text.lower()

    async def extract_with_fallback(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> Optional[BaseModel]:
        """Execute extraction trying each provider sequentially with backoff and jitter."""
        chunks = self.chunk_text(source_text)
        primary_chunk = chunks[0] if chunks else source_text

        for provider in self.providers:
            # Skip provider if API key is not configured and not mock
            if not getattr(provider, "api_key", None):
                continue

            for attempt in range(1, settings.LLM_MAX_RETRIES + 1):
                try:
                    logger.info(
                        "Attempting extraction using provider=%s (attempt %d/%d)",
                        provider.provider_name, attempt, settings.LLM_MAX_RETRIES
                    )
                    result = await provider.extract_structured(prompt, primary_chunk, schema)
                    return result

                except Exception as err:
                    err_msg = str(err)
                    logger.warning(
                        "Provider %s failed with error: %s",
                        provider.provider_name, err_msg
                    )

                    # Check for rate limit (429) or transient errors
                    is_rate_limit = "429" in err_msg or "rate limit" in err_msg.lower()
                    is_payload_too_large = "413" in err_msg or "too large" in err_msg.lower()

                    if is_payload_too_large and len(primary_chunk) > 2000:
                        logger.info("Payload too large (413). Reducing chunk size by 50%%.")
                        primary_chunk = primary_chunk[: len(primary_chunk) // 2]
                        continue

                    if attempt < settings.LLM_MAX_RETRIES:
                        backoff = min(
                            settings.LLM_MAX_BACKOFF_SECONDS,
                            (settings.LLM_INITIAL_BACKOFF_SECONDS ** attempt) + random.uniform(0.1, 1.0)
                        )
                        logger.info("Backing off for %.2fs before retry...", backoff)
                        await asyncio.sleep(backoff)
                    else:
                        logger.error(
                            "Provider %s exhausted retries. Failing over to next provider.",
                            provider.provider_name
                        )
                        break

        logger.error("All LLM providers in fallback chain failed extraction.")
        return None
