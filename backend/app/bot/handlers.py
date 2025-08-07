"""Telegram bot handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from backend.app.services.prediction import get_prediction_service

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """Handle /start command.

    Args:
        message: Telegram message
    """
    await message.answer(
        "👋 Welcome to Football Lineup Predictor Bot!\n\n"
        "I can help you predict team lineups for upcoming matches.\n\n"
        "Use /predict <team_name> to get a lineup prediction.\n"
        "Example: /predict Arsenal"
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Handle /help command.

    Args:
        message: Telegram message
    """
    await message.answer(
        "📚 <b>Available commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/predict <team> - Get lineup prediction for a team\n\n"
        "<b>Examples:</b>\n"
        "/predict Arsenal\n"
        "/predict Chelsea\n"
        "/predict Liverpool"
    )


@router.message(Command("predict"))
async def predict_handler(message: Message) -> None:
    """Handle /predict command.

    Args:
        message: Telegram message
    """
    # Extract team name from command
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        await message.answer("❌ Please specify a team name.\n" "Example: /predict Arsenal")
        return

    team_name = command_parts[1]

    # Send typing action
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Get prediction
        service = get_prediction_service()
        prediction = await service.get_prediction(team_name)

        # Format response
        response = f"<b>📋 {prediction.team} Predicted Lineup</b>\n\n"

        if prediction.formation:
            response += f"<b>Formation:</b> {prediction.formation}\n\n"

        response += "<b>Players:</b>\n"
        for player in prediction.lineup:
            captain = "©️ " if player.is_captain else ""
            response += f"{captain}{player.number}. {player.name} ({player.position})\n"

        response += f"\n<b>Confidence:</b> {prediction.confidence:.0%}"

        if prediction.cached:
            response += "\n<i>📦 From cache</i>"

        await message.answer(response)

    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception:
        await message.answer(
            "❌ An error occurred while fetching the prediction. " "Please try again later."
        )


@router.message()
async def default_handler(message: Message) -> None:
    """Handle all other messages.

    Args:
        message: Telegram message
    """
    await message.answer(
        "I don't understand that command.\n" "Use /help to see available commands."
    )
