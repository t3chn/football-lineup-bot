"""Custom exceptions for the application."""

from .api import APIError, ExternalAPIError, RateLimitError, TimeoutError
from .business import BusinessError, TeamNotFoundError, ValidationError
from .system import ConfigurationError, SystemError

__all__ = [
    # API Exceptions
    "APIError",
    "ExternalAPIError",
    "TimeoutError",
    "RateLimitError",
    # Business Exceptions
    "BusinessError",
    "TeamNotFoundError",
    "ValidationError",
    # System Exceptions
    "SystemError",
    "ConfigurationError",
]
