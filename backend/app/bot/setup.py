"""Bot setup and initialization."""

from backend.app.bot.bot import get_dispatcher
from backend.app.bot.handlers import router


def setup_bot() -> None:
    """Set up bot with all handlers."""
    dp = get_dispatcher()
    dp.include_router(router)
