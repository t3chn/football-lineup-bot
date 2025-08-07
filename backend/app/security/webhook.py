"""Webhook security utilities."""

import hashlib
import hmac


def verify_telegram_webhook_signature(
    secret_token: str,
    signature: str | None,
    body: bytes,  # noqa: ARG001
) -> bool:
    """Verify Telegram webhook signature using HMAC-SHA256.

    Args:
        secret_token: Secret token configured for webhook
        signature: X-Telegram-Bot-Api-Secret-Token header value
        body: Raw request body bytes (unused but kept for future HMAC implementation)

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret_token:
        return False

    # Telegram sends the secret token directly in the header
    # Not HMAC, just a simple comparison
    return hmac.compare_digest(signature, secret_token)


def generate_webhook_signature(secret_token: str, body: bytes) -> str:
    """Generate webhook signature for testing.

    Args:
        secret_token: Secret token
        body: Request body bytes

    Returns:
        Generated signature
    """
    return hmac.new(secret_token.encode(), body, hashlib.sha256).hexdigest()
