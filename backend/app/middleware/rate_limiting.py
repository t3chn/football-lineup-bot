"""Rate limiting middleware for API endpoints."""

import time
from uuid import uuid4

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.settings import get_settings

settings = get_settings()


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on API key or IP address.

    Priority:
    1. API key if present (per-user limiting)
    2. IP address (fallback)
    """
    # Try to get API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"

    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize limiter with Redis storage if available
# In development mode, use memory storage (non-distributed)
storage_uri = None
if settings.redis_url and not settings.is_development:
    storage_uri = settings.redis_url

# In development mode, use more relaxed limits
default_limits = (
    ["1000 per minute", "10000 per hour"]
    if settings.is_development
    else ["100 per minute", "1000 per hour"]
)

limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=default_limits,
    storage_uri=storage_uri,
    headers_enabled=True,  # Add rate limit headers to responses
)


class RateLimitTiers:
    """Rate limit tiers for different user types."""

    FREE = "10 per minute"
    BASIC = "30 per minute"
    PREMIUM = "100 per minute"
    UNLIMITED = None  # No rate limiting


async def get_user_tier_limit(request: Request) -> str:
    """
    Get rate limit based on user tier.

    Currently returns FREE tier for all users.
    In production, this would check user tier from database.
    """
    api_key = request.headers.get("X-API-Key")

    # Special test key gets higher limits for development
    if api_key == "test-api-key":
        return RateLimitTiers.BASIC

    if not api_key:
        return RateLimitTiers.FREE

    # TODO: Lookup user tier from database
    # user = await get_user_by_api_key(api_key)
    # return user.rate_limit_tier if user else RateLimitTiers.FREE

    return RateLimitTiers.FREE


class DistributedRateLimiter:
    """
    Redis-based distributed rate limiter using sliding window.

    This is for future use when we need distributed rate limiting
    across multiple server instances.
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        """
        Check if request is allowed using sliding window algorithm.

        Args:
            key: Unique identifier for rate limiting
            limit: Maximum number of requests
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, info_dict)
        """
        now = time.time()
        pipeline = self.redis.pipeline()

        # Remove old entries outside the window
        pipeline.zremrangebyscore(key, 0, now - window)

        # Count current entries
        pipeline.zcard(key)

        # Add current request
        request_id = str(uuid4())
        pipeline.zadd(key, {request_id: now})

        # Set expiry
        pipeline.expire(key, window)

        results = await pipeline.execute()

        current_requests = results[1]
        is_allowed = current_requests < limit

        # If not allowed, remove the just-added request
        if not is_allowed:
            await self.redis.zrem(key, request_id)

        return is_allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_requests),
            "reset": int(now + window),
        }
