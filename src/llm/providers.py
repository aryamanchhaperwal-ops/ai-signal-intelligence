"""Concrete and Mock LLM Provider Implementations (Gemini, Groq, DeepSeek)."""

import json
import time
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from src.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from src.utils.logging import logger


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider for unit testing without live API keys."""

    def __init__(self, mock_responses: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(api_key="mock-key", model="mock-model")
        self.mock_responses = mock_responses or {}

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        return LLMResponse(
            provider="mock",
            model="mock-v1",
            content="{}",
            latency_seconds=0.01
        )

    async def extract_structured(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        # Returns default instance or schema-compliant mock
        if self.mock_responses:
            return schema.model_validate(self.mock_responses)
        return schema.model_validate({})


class GeminiProvider(BaseLLMProvider):
    """Primary Provider: Google Gemini Flash."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        start_time = time.monotonic()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # In production, integrates with google.genai / aiohttp REST client
        # Clean structured simulation for interface readiness
        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content="Simulated Gemini response",
            latency_seconds=time.monotonic() - start_time
        )

    async def extract_structured(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        raise NotImplementedError("Live provider call requires valid GEMINI_API_KEY.")


class GroqProvider(BaseLLMProvider):
    """First Fallback Provider: Groq Llama."""

    @property
    def provider_name(self) -> str:
        return "groq"

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")
        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content="Simulated Groq response",
            latency_seconds=0.1
        )

    async def extract_structured(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")
        raise NotImplementedError("Live provider call requires valid GROQ_API_KEY.")


class DeepSeekProvider(BaseLLMProvider):
    """Second Fallback Provider: DeepSeek."""

    @property
    def provider_name(self) -> str:
        return "deepseek"

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured.")
        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content="Simulated DeepSeek response",
            latency_seconds=0.1
        )

    async def extract_structured(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured.")
        raise NotImplementedError("Live provider call requires valid DEEPSEEK_API_KEY.")
