"""In-memory cache service."""

import time
from typing import Any

from backend.app.settings import get_settings


class InMemoryCacheService:
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize cache service."""
        self._cache: dict[str, tuple[Any, float]] = {}
        self.settings = get_settings()
        self.default_ttl = self.settings.cache_ttl_seconds

    async def get(self, key: str) -> Any | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        if time.time() > expiry_time:
            del self._cache[key]
            return None

        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not provided)
        """
        if ttl is None:
            ttl = self.default_ttl

        expiry_time = time.time() + ttl
        self._cache[key] = (value, expiry_time)

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items() if current_time > expiry_time
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def size(self) -> int:
        """Get current cache size.

        Returns:
            Number of items in cache
        """
        return len(self._cache)

    def is_empty(self) -> bool:
        """Check if cache is empty.

        Returns:
            True if cache is empty
        """
        return len(self._cache) == 0
