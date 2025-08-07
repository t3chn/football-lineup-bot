"""Tests for Telegram bot."""

from unittest.mock import MagicMock, patch

from aiogram import Bot, Dispatcher


def test_bot_initialization():
    """Test bot initialization with correct settings."""
    with patch("backend.app.bot.bot.get_settings") as mock_settings:
        mock_settings.return_value.telegram_bot_token = "123456:ABC-DEF1234567890"

        # Reset global bot instance
        import backend.app.bot.bot

        backend.app.bot.bot._bot = None

        from backend.app.bot.bot import get_bot

        bot = get_bot()
        assert isinstance(bot, Bot)


def test_dispatcher_initialization():
    """Test dispatcher initialization."""
    # Reset global dispatcher instance
    import backend.app.bot.bot

    backend.app.bot.bot._dp = None

    from backend.app.bot.bot import get_dispatcher

    dp = get_dispatcher()
    assert isinstance(dp, Dispatcher)


def test_get_bot():
    """Test get_bot function."""
    with patch("backend.app.bot.bot.get_settings") as mock_settings:
        mock_settings.return_value.telegram_bot_token = "123456:ABC-DEF1234567890"

        # Reset global bot instance
        import backend.app.bot.bot

        backend.app.bot.bot._bot = None

        from backend.app.bot.bot import get_bot

        bot = get_bot()
        assert isinstance(bot, Bot)


def test_get_dispatcher():
    """Test get_dispatcher function."""
    # Reset global dispatcher instance
    import backend.app.bot.bot

    backend.app.bot.bot._dp = None

    from backend.app.bot.bot import get_dispatcher

    dp = get_dispatcher()
    assert isinstance(dp, Dispatcher)


def test_setup_bot():
    """Test bot setup with handlers."""
    from backend.app.bot.setup import setup_bot

    with patch("backend.app.bot.setup.get_dispatcher") as mock_get_dp:
        mock_dp = MagicMock()
        mock_get_dp.return_value = mock_dp

        setup_bot()
        mock_dp.include_router.assert_called_once()
