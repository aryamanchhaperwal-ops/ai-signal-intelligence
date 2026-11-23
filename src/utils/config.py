"""Centralized Configuration Management using Pydantic Settings."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application Environment
    APP_ENV: str = Field("development", description="Runtime environment")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field("console", description="Logging format: json or console")
    DATA_DIR: Path = Field(Path("data"), description="Path to runtime data directory")
    EXPORTS_DIR: Path = Field(Path("data/exports"), description="Path to output exports directory")

    # Concurrency and Rate Limiting
    MAX_CONCURRENT_REQUESTS: int = Field(10, description="Global concurrency limit")
    REQUEST_TIMEOUT_SECONDS: int = Field(30, description="Default HTTP request timeout")
    POLITE_DELAY_MIN_MS: int = Field(250, description="Min jitter delay in ms")
    POLITE_DELAY_MAX_MS: int = Field(750, description="Max jitter delay in ms")
    USER_AGENT: str = Field(
        "AISignalIntelligenceBot/1.0 (+https://ai-signal.internal/bot; research@ai-signal.internal)",
        description="Polite HTTP User-Agent header"
    )

    # LLM Provider Credentials
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API Key")
    GEMINI_MODEL: str = Field("gemini-1.5-flash", description="Gemini Flash Model Identifier")

    GROQ_API_KEY: Optional[str] = Field(None, description="Groq API Key")
    GROQ_MODEL: str = Field("llama-3.3-70b-versatile", description="Groq Llama Model Identifier")

    DEEPSEEK_API_KEY: Optional[str] = Field(None, description="DeepSeek API Key")
    DEEPSEEK_MODEL: str = Field("deepseek-chat", description="DeepSeek Model Identifier")

    LLM_MAX_RETRIES: int = Field(4, description="Max retry attempts for LLM extraction")
    LLM_INITIAL_BACKOFF_SECONDS: float = Field(2.0, description="Initial retry backoff delay")
    LLM_MAX_BACKOFF_SECONDS: float = Field(30.0, description="Maximum retry backoff delay")

    # External APIs
    GITHUB_TOKEN: Optional[str] = Field(None, description="GitHub REST API PAT for star metrics")
    GOOGLE_SHEETS_CREDENTIALS_JSON: Optional[str] = Field(None, description="Path to service account credentials")
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = Field(None, description="Google Sheet target ID")

    # Storage
    DATABASE_URL: str = Field("sqlite+aiosqlite:///data/ai_signal.db", description="Database connection URL")
    REDIS_URL: Optional[str] = Field("redis://localhost:6379/0", description="Redis connection URL")


# Singleton instance
settings = Settings()
