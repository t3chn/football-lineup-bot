"""Redis cache service."""

import json
from typing import Any

import redis.asyncio as redis

from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)


class RedisCacheService:
    """Redis-based cache with TTL support."""

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        """Initialize Redis cache service.

        Args:
            redis_client: Optional Redis client for testing
        """
        self.settings = get_settings()
        self.default_ttl = self.settings.cache_ttl_seconds

        if redis_client:
            self.redis = redis_client
        else:
            self.redis = redis.from_url(
                self.settings.redis_url,
                decode_responses=True,
            )

    async def get(self, key: str) -> Any | None:
        """Get value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None

            # Try to parse as JSON, fallback to string if parsing fails
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except redis.RedisError as e:
            logger.error("Redis get error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in Redis cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not provided)
        """
        if ttl is None:
            ttl = self.default_ttl

        try:
            # Serialize value to JSON if not a string
            if isinstance(value, dict | list):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)

            await self.redis.setex(key, ttl, serialized_value)
            logger.debug("Cache set", key=key, ttl=ttl)

        except redis.RedisError as e:
            logger.error("Redis set error", key=key, error=str(e))
            # Don't raise the error to prevent cache failures from breaking the app

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)

        except redis.RedisError as e:
            logger.error("Redis delete error", key=key, error=str(e))
            return False

    async def clear(self) -> None:
        """Clear all cached values."""
        try:
            await self.redis.flushdb()
            logger.info("Cache cleared")

        except redis.RedisError as e:
            logger.error("Redis clear error", error=str(e))

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            result = await self.redis.exists(key)
            return bool(result)

        except redis.RedisError as e:
            logger.error("Redis exists error", key=key, error=str(e))
            return False

    async def ttl(self, key: str) -> int:
        """Get time to live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if key exists but no TTL, -2 if key doesn't exist
        """
        try:
            return await self.redis.ttl(key)

        except redis.RedisError as e:
            logger.error("Redis TTL error", key=key, error=str(e))
            return -2

    async def ping(self) -> bool:
        """Check Redis connection.

        Returns:
            True if Redis is responding
        """
        try:
            await self.redis.ping()
            return True

        except redis.RedisError as e:
            logger.error("Redis ping error", error=str(e))
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        try:
            await self.redis.close()

        except redis.RedisError as e:
            logger.error("Redis close error", error=str(e))
