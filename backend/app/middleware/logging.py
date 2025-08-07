"""Request logging middleware."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.utils.logging import generate_request_id, get_logger, set_request_id

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and correlation ID tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging and timing.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        set_request_id(request_id)

        # Bind request context to logger
        log = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) if request.url.query else None,
            user_agent=request.headers.get("user-agent"),
            client_ip=self._get_client_ip(request),
        )

        # Log request start
        start_time = time.time()
        log.info("Request started")

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Log successful completion
            log.info(
                "Request completed",
                status_code=response.status_code,
                processing_time_ms=round(processing_time * 1000, 2),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate processing time for failed requests
            processing_time = time.time() - start_time

            # Log error with details
            log.error(
                "Request failed",
                error=str(e),
                error_type=type(e).__name__,
                processing_time_ms=round(processing_time * 1000, 2),
                exc_info=True,
            )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers.

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check for forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, get the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
