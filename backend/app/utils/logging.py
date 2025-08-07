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


def setup_logging(log_level: str = "INFO", json_format: bool = False) -> None:
    """Setup structured logging.

    Args:
        log_level: Logging level
        json_format: Whether to use JSON format
    """
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
