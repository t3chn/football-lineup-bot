"""Base exception classes."""

from typing import Any


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        error_code: str,
        details: dict[str, Any] | None = None,
        status_code: int = 500,
    ):
        """Initialize base exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }
