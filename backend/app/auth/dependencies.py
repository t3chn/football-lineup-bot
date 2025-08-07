"""Authentication dependencies."""

from fastapi import Depends

from .api_key import api_key_header, verify_api_key


def require_auth(api_key: str | None = Depends(api_key_header)) -> str:
    """Dependency to require authentication.

    Args:
        api_key: API key from header

    Returns:
        Verified API key

    Raises:
        HTTPException: If authentication fails
    """
    return verify_api_key(api_key)
