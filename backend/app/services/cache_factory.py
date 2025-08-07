"""Cache factory for creating appropriate cache instances."""

from typing import Any, Protocol

from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)


class CacheProtocol(Protocol):
    """Protocol for cache implementations."""

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with TTL."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    async def clear(self) -> None:
        """Clear all cached values."""
        ...


async def create_cache() -> CacheProtocol:
    """Create appropriate cache instance based on configuration.

    Returns:
        Cache instance (Redis or in-memory fallback)
    """
    settings = get_settings()

    # Try Redis first if URL is configured and not default localhost
    if settings.redis_url and settings.redis_url != "redis://localhost:6379/0":
        try:
            from backend.app.services.redis_cache import RedisCacheService

            redis_cache = RedisCacheService()

            # Test connection
            if await redis_cache.ping():
                logger.info("Using Redis cache", redis_url=settings.redis_url)
                return redis_cache
            else:
                logger.warning("Redis connection failed, falling back to in-memory cache")
                await redis_cache.close()

        except ImportError as e:
            logger.warning("Redis not available, using in-memory cache", error=str(e))
        except Exception as e:
            logger.warning("Redis connection error, using in-memory cache", error=str(e))

    # Fallback to in-memory cache
    logger.info("Using in-memory cache")
    from backend.app.services.memory_cache import InMemoryCacheService

    return InMemoryCacheService()


# Global cache instance
_cache_instance: CacheProtocol | None = None


async def get_cache() -> CacheProtocol:
    """Get global cache instance.

    Returns:
        Global cache service instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = await create_cache()
    return _cache_instance


async def reset_cache() -> None:
    """Reset cache instance (useful for testing)."""
    global _cache_instance
    if _cache_instance:
        await _cache_instance.clear()
        _cache_instance = None
