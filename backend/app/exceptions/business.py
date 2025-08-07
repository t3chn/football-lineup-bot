"""Business logic exceptions."""

from .base import BaseAppException


class BusinessError(BaseAppException):
    """Base exception for business logic errors."""

    def __init__(
        self, message: str, error_code: str = "BUSINESS_ERROR", details: dict | None = None
    ):
        """Initialize business error."""
        super().__init__(message, error_code, details, status_code=400)


class TeamNotFoundError(BusinessError):
    """Exception when team is not found."""

    def __init__(self, team_name: str, details: dict | None = None):
        """Initialize team not found error."""
        details = details or {}
        details["team"] = team_name
        super().__init__(
            f"Team '{team_name}' not found",
            "TEAM_NOT_FOUND",
            details,
        )
        self.status_code = 404


class ValidationError(BusinessError):
    """Exception for validation errors."""

    def __init__(self, message: str, field: str | None = None, details: dict | None = None):
        """Initialize validation error."""
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)
        self.status_code = 422
