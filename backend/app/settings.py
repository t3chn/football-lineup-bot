"""Application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram Bot
    telegram_bot_token: str = Field(
        default="",
        description="Telegram bot token from BotFather",
    )

    # External API
    api_football_key: str = Field(
        default="",
        description="API-Football or Sportmonks API key",
    )
    api_football_base_url: str = Field(
        default="https://api-football-v1.p.rapidapi.com/v3",
        description="Base URL for football API",
    )

    # Server Configuration
    port: int = Field(
        default=8000,
        description="Server port",
    )
    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )
    environment: str = Field(
        default="development",
        description="Environment (development/staging/production)",
    )

    # CORS Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Cache Settings
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds",
    )

    # Webhook Configuration
    webhook_url: str = Field(
        default="",
        description="Webhook URL for Telegram bot",
    )
    webhook_secret: str = Field(
        default="",
        description="Webhook secret for verification",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
