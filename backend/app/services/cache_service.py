import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """In-memory cache with TTL support and Redis-ready interface"""

    def __init__(self):
        self.cache = {}
        self.access_count = {}
        self.hit_count = 0
        self.miss_count = 0

        # Start cleanup task
        asyncio.create_task(self._cleanup_expired())

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        try:
            if key in self.cache:
                entry = self.cache[key]
                expiry = entry.get("expiry")

                # Check if expired
                if expiry and datetime.now() > expiry:
                    del self.cache[key]
                    self.miss_count += 1
                    return None

                # Update access count and last accessed
                self.access_count[key] = self.access_count.get(key, 0) + 1
                entry["last_accessed"] = datetime.now()
                self.hit_count += 1

                return entry.get("value")

            self.miss_count += 1
            return None

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl_seconds: int = 300, tags: list[str] | None = None
    ) -> bool:
        """Set value in cache with TTL"""
        try:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds else None

            self.cache[key] = {
                "value": value,
                "expiry": expiry,
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "tags": tags or [],
                "ttl": ttl_seconds,
            }

            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_count:
                    del self.access_count[key]
                return True
            return False

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_by_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            import re

            regex = re.compile(pattern.replace("*", ".*"))

            keys_to_delete = [key for key in self.cache if regex.match(key)]

            for key in keys_to_delete:
                await self.delete(key)

            return len(keys_to_delete)

        except Exception as e:
            logger.error(f"Cache delete by pattern error: {e}")
            return 0

    async def delete_by_tags(self, tags: list[str]) -> int:
        """Delete all entries with specified tags"""
        try:
            keys_to_delete = []

            for key, entry in self.cache.items():
                entry_tags = entry.get("tags", [])
                if any(tag in entry_tags for tag in tags):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                await self.delete(key)

            return len(keys_to_delete)

        except Exception as e:
            logger.error(f"Cache delete by tags error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        value = await self.get(key)
        return value is not None

    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key in seconds"""
        try:
            if key in self.cache:
                entry = self.cache[key]
                expiry = entry.get("expiry")

                if expiry:
                    remaining = (expiry - datetime.now()).total_seconds()
                    return max(0, int(remaining))

                return -1  # No expiry

            return -2  # Key doesn't exist

        except Exception as e:
            logger.error(f"Cache get TTL error for key {key}: {e}")
            return -2

    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend TTL for existing key"""
        try:
            if key in self.cache:
                entry = self.cache[key]
                current_expiry = entry.get("expiry")

                if current_expiry:
                    entry["expiry"] = current_expiry + timedelta(seconds=additional_seconds)
                else:
                    entry["expiry"] = datetime.now() + timedelta(seconds=additional_seconds)

                return True

            return False

        except Exception as e:
            logger.error(f"Cache extend TTL error for key {key}: {e}")
            return False

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values at once"""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result

    async def set_many(self, items: dict[str, Any], ttl_seconds: int = 300) -> bool:
        """Set multiple values at once"""
        try:
            for key, value in items.items():
                await self.set(key, value, ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"Cache set many error: {e}")
            return False

    async def _cleanup_expired(self):
        """Background task to cleanup expired entries"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute

                now = datetime.now()
                expired_keys = []

                for key, entry in self.cache.items():
                    expiry = entry.get("expiry")
                    if expiry and now > expiry:
                        expired_keys.append(key)

                for key in expired_keys:
                    del self.cache[key]
                    if key in self.access_count:
                        del self.access_count[key]

                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_size = len(self.cache)
        expired_count = sum(
            1
            for entry in self.cache.values()
            if entry.get("expiry") and datetime.now() > entry["expiry"]
        )

        hit_rate = (
            self.hit_count / (self.hit_count + self.miss_count)
            if (self.hit_count + self.miss_count) > 0
            else 0
        )

        # Get most accessed keys
        most_accessed = sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_keys": total_size,
            "expired_keys": expired_count,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "most_accessed": most_accessed,
        }

    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.clear()
            self.access_count.clear()
            self.hit_count = 0
            self.miss_count = 0
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


class APICache:
    """Specialized cache for API responses with smart invalidation"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

        # TTL settings for different API endpoints
        self.ttl_config = {
            "squad": 3600,  # 1 hour
            "fixture": 300,  # 5 minutes
            "lineup": 600,  # 10 minutes
            "news": 300,  # 5 minutes
            "injuries": 900,  # 15 minutes
            "team_info": 7200,  # 2 hours
            "player_stats": 1800,  # 30 minutes
        }

    def _get_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key from endpoint and params"""
        # Sort params for consistent keys
        sorted_params = sorted(params.items())
        param_str = "_".join(f"{k}:{v}" for k, v in sorted_params)
        return f"api:{endpoint}:{param_str}"

    async def get_cached_response(self, endpoint: str, params: dict) -> dict | None:
        """Get cached API response"""
        key = self._get_cache_key(endpoint, params)
        return await self.cache.get(key)

    async def cache_response(
        self, endpoint: str, params: dict, response: dict, custom_ttl: int | None = None
    ) -> bool:
        """Cache API response with appropriate TTL"""
        key = self._get_cache_key(endpoint, params)

        # Determine TTL
        ttl = custom_ttl or self.ttl_config.get(endpoint, 300)

        # Add metadata
        cached_data = {
            "response": response,
            "cached_at": datetime.now().isoformat(),
            "endpoint": endpoint,
            "params": params,
        }

        # Set tags for invalidation
        tags = [f"endpoint:{endpoint}"]
        if "team_id" in params:
            tags.append(f"team:{params['team_id']}")
        if "fixture_id" in params:
            tags.append(f"fixture:{params['fixture_id']}")

        return await self.cache.set(key, cached_data, ttl, tags)

    async def invalidate_team_cache(self, team_id: int):
        """Invalidate all cache entries for a team"""
        return await self.cache.delete_by_tags([f"team:{team_id}"])

    async def invalidate_fixture_cache(self, fixture_id: int):
        """Invalidate all cache entries for a fixture"""
        return await self.cache.delete_by_tags([f"fixture:{fixture_id}"])

    async def invalidate_endpoint_cache(self, endpoint: str):
        """Invalidate all cache entries for an endpoint"""
        return await self.cache.delete_by_tags([f"endpoint:{endpoint}"])


# Global cache instance
cache_service = CacheService()
api_cache = APICache(cache_service)
