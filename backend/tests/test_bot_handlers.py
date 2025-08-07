"""Tests for bot handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Chat, Message, User

from backend.app.bot.handlers import (
    default_handler,
    help_handler,
    predict_handler,
    start_handler,
)
from backend.app.models.prediction import Player, PredictionResponse


@pytest.fixture
def mock_message():
    """Create mock message for testing."""
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 123456
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 789
    return message


@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test /start command handler."""
    await start_handler(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Welcome to Football Lineup Predictor Bot" in call_args
    assert "/predict" in call_args


@pytest.mark.asyncio
async def test_help_handler(mock_message):
    """Test /help command handler."""
    await help_handler(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Available commands" in call_args
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/predict" in call_args


@pytest.mark.asyncio
async def test_predict_handler_no_team(mock_message):
    """Test /predict command without team name."""
    mock_message.text = "/predict"

    await predict_handler(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Please specify a team name" in call_args


@pytest.mark.asyncio
async def test_predict_handler_success(mock_message):
    """Test /predict command with valid team."""
    mock_message.text = "/predict Arsenal"

    mock_prediction = PredictionResponse(
        team="Arsenal",
        formation="4-3-3",
        lineup=[
            Player(name="Player 1", number=1, position="GK", is_captain=False),
            Player(name="Player 10", number=10, position="AM", is_captain=True),
        ],
        confidence=0.85,
        source="api",
        cached=False,
    )

    with patch("backend.app.bot.handlers.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(return_value=mock_prediction)

        await predict_handler(mock_message)

        # Check typing action was sent
        mock_message.bot.send_chat_action.assert_called_once_with(chat_id=123456, action="typing")

        # Check response
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Arsenal Predicted Lineup" in call_args
        assert "4-3-3" in call_args
        assert "Player 1" in call_args
        assert "©️" in call_args  # Captain marker
        assert "85%" in call_args  # Confidence


@pytest.mark.asyncio
async def test_predict_handler_team_not_found(mock_message):
    """Test /predict command with invalid team."""
    mock_message.text = "/predict InvalidTeam"

    with patch("backend.app.bot.handlers.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(
            side_effect=ValueError("Team 'InvalidTeam' not found")
        )

        await predict_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Team 'InvalidTeam' not found" in call_args


@pytest.mark.asyncio
async def test_predict_handler_error(mock_message):
    """Test /predict command with API error."""
    mock_message.text = "/predict Arsenal"

    with patch("backend.app.bot.handlers.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(side_effect=Exception("API error"))

        await predict_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "An error occurred" in call_args


@pytest.mark.asyncio
async def test_default_handler(mock_message):
    """Test default handler for unknown commands."""
    mock_message.text = "random text"

    await default_handler(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "don't understand" in call_args
    assert "/help" in call_args
