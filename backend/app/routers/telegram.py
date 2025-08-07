"""Telegram webhook router."""

import logging

from aiogram.types import Update
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.app.auth import require_auth
from backend.app.bot import get_bot, get_dispatcher
from backend.app.bot.setup import setup_bot
from backend.app.security import verify_telegram_webhook_signature
from backend.app.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])

# Initialize bot handlers on module load
setup_bot()


@router.post("/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Handle incoming Telegram webhook updates.

    Args:
        request: FastAPI request object

    Returns:
        JSONResponse with status

    Raises:
        HTTPException: If webhook processing fails or signature is invalid
    """
    # Verify webhook signature
    settings = get_settings()
    signature = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    body = await request.body()

    if not verify_telegram_webhook_signature(
        secret_token=settings.webhook_secret, signature=signature, body=body
    ):
        logger.warning("Invalid webhook signature received")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        # Get bot and dispatcher instances
        bot = get_bot()
        dp = get_dispatcher()

        # Parse and validate update from request body
        import json

        from backend.app.validators.webhook import WebhookUpdateValidator

        data = json.loads(body)

        # Validate the webhook data
        try:
            validated_data = WebhookUpdateValidator(**data)
        except ValueError as e:
            logger.warning(f"Invalid webhook data: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid webhook data: {e}") from e

        # Convert back to Update object for aiogram
        update = Update(**validated_data.model_dump())

        # Process update
        await dp.feed_update(bot, update)

        return JSONResponse(content={"ok": True})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process webhook update: {e}")
        raise HTTPException(status_code=500, detail="Failed to process update") from e


@router.post("/set-webhook")
async def set_webhook(api_key: str = Depends(require_auth)) -> dict:  # noqa: ARG001
    """Set webhook URL for Telegram bot.

    Returns:
        Dictionary with webhook status

    Raises:
        HTTPException: If setting webhook fails
    """
    settings = get_settings()

    if not settings.webhook_url:
        raise HTTPException(status_code=400, detail="WEBHOOK_URL not configured")

    try:
        bot = get_bot()
        webhook_url = f"{settings.webhook_url}/telegram/webhook"

        # Set webhook with secret token
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
        )

        webhook_info = await bot.get_webhook_info()

        return {
            "ok": True,
            "webhook_url": webhook_info.url,
            "pending_update_count": webhook_info.pending_update_count,
            "allowed_updates": webhook_info.allowed_updates,
        }

    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set webhook: {e}") from e


@router.delete("/webhook")
async def delete_webhook(api_key: str = Depends(require_auth)) -> dict:  # noqa: ARG001
    """Delete webhook URL for Telegram bot.

    Returns:
        Dictionary with deletion status

    Raises:
        HTTPException: If deleting webhook fails
    """
    try:
        bot = get_bot()
        await bot.delete_webhook(drop_pending_updates=True)

        return {"ok": True, "message": "Webhook deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {e}") from e


@router.get("/webhook-info")
async def get_webhook_info(api_key: str = Depends(require_auth)) -> dict:  # noqa: ARG001
    """Get current webhook information.

    Returns:
        Dictionary with webhook information

    Raises:
        HTTPException: If getting webhook info fails
    """
    try:
        bot = get_bot()
        webhook_info = await bot.get_webhook_info()

        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "ip_address": webhook_info.ip_address,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "last_synchronization_error_date": webhook_info.last_synchronization_error_date,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates,
        }

    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get webhook info: {e}") from e
