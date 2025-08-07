"""Structured logging configuration."""

import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import structlog

# Context variable for request ID
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def add_request_id(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    """Add request ID to log entries.

    Args:
        logger: Logger instance
        method_name: Method name
        event_dict: Event dictionary

    Returns:
        Updated event dictionary
    """
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging(log_level: str = "INFO", json_format: bool | None = None) -> None:
    """Setup structured logging.

    Args:
        log_level: Logging level
        json_format: Whether to use JSON format (auto-detect from environment if None)
    """
    # Auto-detect JSON format if not specified
    if json_format is None:
        import os

        json_format = os.getenv("ENVIRONMENT", "development").lower() == "production"
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_request_id,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # Add callsite information for better debugging
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
    ]

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def generate_request_id() -> str:
    """Generate a unique request ID.

    Returns:
        UUID string for request tracking
    """
    return str(uuid4())


def set_request_id(request_id: str | None) -> None:
    """Set the request ID for the current context.

    Args:
        request_id: Request ID to set
    """
    request_id_var.set(request_id)


def get_request_id() -> str | None:
    """Get the current request ID.

    Returns:
        Current request ID or None if not set
    """
    return request_id_var.get()


class PerformanceLogger:
    """Context manager for performance logging."""

    def __init__(self, logger: structlog.BoundLogger, operation: str, **kwargs: Any) -> None:
        """Initialize performance logger.

        Args:
            logger: Logger instance
            operation: Operation name
            **kwargs: Additional context
        """
        self.logger = logger.bind(operation=operation, **kwargs)
        self.operation = operation
        self.start_time: float = 0

    def __enter__(self) -> "PerformanceLogger":
        """Start timing."""
        import time

        self.start_time = time.time()
        self.logger.debug("Operation started")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End timing and log result."""
        import time

        duration = time.time() - self.start_time
        duration_ms = round(duration * 1000, 2)

        if exc_type:
            self.logger.error(
                "Operation failed",
                duration_ms=duration_ms,
                error=str(exc_val),
                error_type=exc_type.__name__,
            )
        else:
            self.logger.info("Operation completed", duration_ms=duration_ms)


def log_performance(
    logger: structlog.BoundLogger, operation: str, **kwargs: Any
) -> PerformanceLogger:
    """Create a performance logging context manager.

    Args:
        logger: Logger instance
        operation: Operation name
        **kwargs: Additional context

    Returns:
        Performance logger context manager
    """
    return PerformanceLogger(logger, operation, **kwargs)
