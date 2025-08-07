"""API Key authentication."""

import secrets

from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader

from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None) -> str:
    """Verify API key.

    Args:
        api_key: API key from header

    Returns:
        Verified API key

    Raises:
        HTTPException: If API key is invalid
    """
    settings = get_settings()

    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not settings.api_key:
        logger.error("API key not configured in settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured",
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, settings.api_key):
        logger.warning("Invalid API key provided", api_key_prefix=api_key[:8] + "...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    logger.debug("API key verified successfully")
    return api_key


def generate_api_key() -> str:
    """Generate a secure API key.

    Returns:
        Generated API key
    """
    return secrets.token_urlsafe(32)
