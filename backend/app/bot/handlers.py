"""Telegram bot handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from backend.app.exceptions import BusinessError, ExternalAPIError, TeamNotFoundError
from backend.app.services.prediction import get_prediction_service
from backend.app.utils.logging import get_logger

router = Router()
logger = get_logger(__name__)


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

    except TeamNotFoundError as e:
        logger.warning(
            "Team not found",
            error_code=e.error_code,
            team=team_name,
            user_id=message.from_user.id if message.from_user else None,
        )
        await message.answer(f"❌ {e.message}")

    except (ExternalAPIError, BusinessError) as e:
        logger.error(
            "Business error in bot handler",
            error_code=e.error_code,
            team=team_name,
            user_id=message.from_user.id if message.from_user else None,
        )
        await message.answer(f"❌ {e.message}")

    except Exception as e:
        logger.error(
            "Unexpected error in predict handler",
            error=str(e),
            error_type=type(e).__name__,
            team=team_name,
            user_id=message.from_user.id if message.from_user else None,
        )
        await message.answer("❌ An unexpected error occurred. Please try again later.")


@router.message()
async def default_handler(message: Message) -> None:
    """Handle all other messages.

    Args:
        message: Telegram message
    """
    await message.answer(
        "I don't understand that command.\n" "Use /help to see available commands."
    )
