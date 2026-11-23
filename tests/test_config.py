"""Unit tests for configuration loading."""

from src.utils.config import Settings


class TestConfiguration:
    """Test environment configuration parsing and defaults."""

    def test_default_settings(self):
        settings = Settings()
        assert settings.APP_ENV in ["development", "production", "staging"]
        assert settings.MAX_CONCURRENT_REQUESTS >= 1
        assert settings.REQUEST_TIMEOUT_SECONDS >= 5
        assert "AISignalIntelligenceBot" in settings.USER_AGENT
        assert settings.GEMINI_MODEL == "gemini-1.5-flash"
        assert settings.GROQ_MODEL == "llama-3.3-70b-versatile"
        assert settings.DEEPSEEK_MODEL == "deepseek-chat"

    def test_custom_override(self):
        custom = Settings(MAX_CONCURRENT_REQUESTS=25, APP_ENV="staging")
        assert custom.MAX_CONCURRENT_REQUESTS == 25
        assert custom.APP_ENV == "staging"
