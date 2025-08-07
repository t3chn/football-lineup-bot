"""Webhook input validators."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class TelegramUser(BaseModel):
    """Telegram user model with validation."""

    id: int = Field(..., gt=0, description="User ID must be positive")
    is_bot: bool
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str | None = Field(None, max_length=255)
    username: str | None = Field(None, min_length=1, max_length=32)
    language_code: str | None = Field(None, min_length=2, max_length=10)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate Telegram username format."""
        if v and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Invalid username format")
        return v


class TelegramChat(BaseModel):
    """Telegram chat model with validation."""

    id: int = Field(..., description="Chat ID")
    type: str = Field(..., pattern="^(private|group|supergroup|channel)$")
    title: str | None = Field(None, max_length=255)
    username: str | None = Field(None, min_length=1, max_length=32)
    first_name: str | None = Field(None, max_length=255)
    last_name: str | None = Field(None, max_length=255)


class TelegramMessage(BaseModel):
    """Telegram message model with validation."""

    message_id: int = Field(..., gt=0)
    date: int = Field(..., gt=0)
    from_user: TelegramUser | None = Field(None, alias="from")
    chat: TelegramChat
    text: str | None = Field(None, max_length=4096)
    entities: list[dict[str, Any]] | None = None

    model_config = {"populate_by_name": True}


class WebhookUpdateValidator(BaseModel):
    """Validator for Telegram webhook updates."""

    update_id: int = Field(..., gt=0, description="Update ID must be positive")
    message: TelegramMessage | None = None
    callback_query: dict[str, Any] | None = None
    inline_query: dict[str, Any] | None = None
    chosen_inline_result: dict[str, Any] | None = None

    @field_validator("update_id")
    @classmethod
    def validate_update_id(cls, v: int) -> int:
        """Validate update ID range."""
        if v > 2**31 - 1:  # Max int32
            raise ValueError("Invalid update ID")
        return v

    def model_post_init(self, __context: Any) -> None:
        """Validate that at least one update type is present."""
        if not any(
            [
                self.message,
                self.callback_query,
                self.inline_query,
                self.chosen_inline_result,
            ]
        ):
            raise ValueError("Update must contain at least one update type")
