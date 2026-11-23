"""Abstract Base Classes and Data Transfer Objects for LLM Providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """Normalized chat message."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message body")


class LLMResponse(BaseModel):
    """Normalized response from an LLM provider."""
    provider: str
    model: str
    content: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_seconds: float = 0.0


class BaseLLMProvider(ABC):
    """Abstract interface that all LLM backends must implement."""

    def __init__(self, api_key: Optional[str] = None, model: str = "") -> None:
        self.api_key = api_key
        self.model = model

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of the provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate unstructured or structured completion from messages."""
        pass

    @abstractmethod
    async def extract_structured(
        self,
        prompt: str,
        source_text: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        """Extract typed structured data adhering to a Pydantic schema."""
        pass
