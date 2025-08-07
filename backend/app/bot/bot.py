"""Telegram bot initialization."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from backend.app.settings import get_settings

# Global instances
_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot:
    """Get bot instance.

    Returns:
        Bot instance
    """
    global _bot
    if _bot is None:
        settings = get_settings()
        _bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            ),
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    """Get dispatcher instance.

    Returns:
        Dispatcher instance
    """
    global _dp
    if _dp is None:
        _dp = Dispatcher()
    return _dp


# Aliases for backward compatibility
bot = property(lambda _: get_bot())
dp = property(lambda _: get_dispatcher())
