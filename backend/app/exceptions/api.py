"""API-related exceptions."""

from .base import BaseAppException


class APIError(BaseAppException):
    """Base exception for API-related errors."""

    def __init__(self, message: str, error_code: str = "API_ERROR", details: dict | None = None):
        """Initialize API error."""
        super().__init__(message, error_code, details, status_code=500)


class ExternalAPIError(APIError):
    """Exception for external API failures."""

    def __init__(self, message: str, api_name: str, details: dict | None = None):
        """Initialize external API error."""
        details = details or {}
        details["api"] = api_name
        super().__init__(message, "EXTERNAL_API_ERROR", details)


class TimeoutError(APIError):
    """Exception for timeout errors."""

    def __init__(self, message: str, timeout_seconds: float, details: dict | None = None):
        """Initialize timeout error."""
        details = details or {}
        details["timeout_seconds"] = timeout_seconds
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.status_code = 504


class RateLimitError(APIError):
    """Exception for rate limit errors."""

    def __init__(self, message: str, retry_after: int | None = None, details: dict | None = None):
        """Initialize rate limit error."""
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.status_code = 429
