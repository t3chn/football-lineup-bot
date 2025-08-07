"""Tests for application settings."""

import os
from unittest.mock import patch

from backend.app.settings import Settings, get_settings


def test_default_settings():
    """Test default settings values."""
    settings = Settings()
    assert settings.port == 8000
    assert settings.host == "0.0.0.0"
    assert settings.environment == "development"
    assert settings.cache_ttl_seconds == 300
    assert settings.cors_origins == ["http://localhost:3000", "http://localhost:5173"]


def test_settings_from_env():
    """Test settings loaded from environment variables."""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "API_FOOTBALL_KEY": "test_key",
            "PORT": "9000",
            "ENVIRONMENT": "production",
        },
    ):
        settings = Settings()
        assert settings.telegram_bot_token == "test_token"
        assert settings.api_football_key == "test_key"
        assert settings.port == 9000
        assert settings.environment == "production"


def test_is_production():
    """Test production environment check."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        settings = Settings()
        assert settings.is_production is True
        assert settings.is_development is False


def test_is_development():
    """Test development environment check."""
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        settings = Settings()
        assert settings.is_development is True
        assert settings.is_production is False


def test_get_settings_cached():
    """Test settings instance is cached."""
    get_settings.cache_clear()
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
