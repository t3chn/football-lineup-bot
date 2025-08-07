"""System-level exceptions."""

from .base import BaseAppException


class SystemError(BaseAppException):
    """Base exception for system errors."""

    def __init__(self, message: str, error_code: str = "SYSTEM_ERROR", details: dict | None = None):
        """Initialize system error."""
        super().__init__(message, error_code, details, status_code=500)


class ConfigurationError(SystemError):
    """Exception for configuration errors."""

    def __init__(self, message: str, config_key: str | None = None, details: dict | None = None):
        """Initialize configuration error."""
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", details)
