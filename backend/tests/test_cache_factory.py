"""Tests for cache factory."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.app.services.cache_factory import create_cache, get_cache, reset_cache


class TestCacheFactory:
    """Test cache factory functionality."""

    @pytest.fixture
    def mock_settings_memory(self):
        """Mock settings for in-memory cache."""
        settings = Mock()
        settings.redis_url = "redis://localhost:6379/0"  # Default local Redis
        settings.cache_ttl_seconds = 300
        return settings

    @pytest.fixture
    def mock_settings_redis(self):
        """Mock settings for Redis cache."""
        settings = Mock()
        settings.redis_url = "redis://production:6379/0"  # Non-default Redis
        settings.cache_ttl_seconds = 300
        return settings

    @pytest.mark.asyncio
    async def test_create_cache_memory_default_url(self, mock_settings_memory):
        """Test cache creation with default Redis URL uses in-memory cache."""
        with patch(
            "backend.app.services.cache_factory.get_settings", return_value=mock_settings_memory
        ):
            cache = await create_cache()

            # Should be in-memory cache
            from backend.app.services.memory_cache import InMemoryCacheService

            assert isinstance(cache, InMemoryCacheService)

    @pytest.mark.asyncio
    async def test_create_cache_redis_success(self, mock_settings_redis):
        """Test cache creation with Redis success."""
        mock_redis_cache = AsyncMock()
        mock_redis_cache.ping.return_value = True

        with (
            patch(
                "backend.app.services.cache_factory.get_settings", return_value=mock_settings_redis
            ),
            patch(
                "backend.app.services.redis_cache.RedisCacheService", return_value=mock_redis_cache
            ),
        ):
            cache = await create_cache()

            # Should be Redis cache
            assert cache == mock_redis_cache
            mock_redis_cache.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_cache_redis_connection_failed(self, mock_settings_redis):
        """Test cache creation when Redis connection fails."""
        mock_redis_cache = AsyncMock()
        mock_redis_cache.ping.return_value = False
        mock_redis_cache.close = AsyncMock()

        with (
            patch(
                "backend.app.services.cache_factory.get_settings", return_value=mock_settings_redis
            ),
            patch(
                "backend.app.services.redis_cache.RedisCacheService", return_value=mock_redis_cache
            ),
        ):
            cache = await create_cache()

            # Should fallback to in-memory cache
            from backend.app.services.memory_cache import InMemoryCacheService

            assert isinstance(cache, InMemoryCacheService)

            # Should have tried to close failed Redis connection
            mock_redis_cache.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_cache_redis_import_error(self, mock_settings_redis):
        """Test cache creation when Redis import fails."""
        import sys

        # Store original module
        original_module = sys.modules.get("backend.app.services.redis_cache")

        # Simulate missing Redis module
        sys.modules["backend.app.services.redis_cache"] = None

        try:
            with (
                patch(
                    "backend.app.services.cache_factory.get_settings",
                    return_value=mock_settings_redis,
                ),
                patch("backend.app.services.cache_factory.logger") as mock_logger,
            ):
                cache = await create_cache()

                # Should fallback to in-memory cache
                from backend.app.services.memory_cache import InMemoryCacheService

                assert isinstance(cache, InMemoryCacheService)

                # Should log warning about Redis not available
                mock_logger.warning.assert_called()
        finally:
            # Restore original module
            if original_module is not None:
                sys.modules["backend.app.services.redis_cache"] = original_module
            else:
                sys.modules.pop("backend.app.services.redis_cache", None)

    @pytest.mark.asyncio
    async def test_create_cache_redis_exception(self, mock_settings_redis):
        """Test cache creation when Redis raises exception."""
        with (
            patch(
                "backend.app.services.cache_factory.get_settings", return_value=mock_settings_redis
            ),
            patch(
                "backend.app.services.redis_cache.RedisCacheService",
                side_effect=Exception("Redis error"),
            ),
        ):
            cache = await create_cache()

            # Should fallback to in-memory cache
            from backend.app.services.memory_cache import InMemoryCacheService

            assert isinstance(cache, InMemoryCacheService)

    @pytest.mark.asyncio
    async def test_get_cache_singleton(self, mock_settings_memory):
        """Test that get_cache returns singleton instance."""
        # Reset cache instance first
        await reset_cache()

        with patch(
            "backend.app.services.cache_factory.get_settings", return_value=mock_settings_memory
        ):
            cache1 = await get_cache()
            cache2 = await get_cache()

            # Should be the same instance
            assert cache1 is cache2

    @pytest.mark.asyncio
    async def test_reset_cache(self, mock_settings_memory):
        """Test cache reset functionality."""
        with patch(
            "backend.app.services.cache_factory.get_settings", return_value=mock_settings_memory
        ):
            # Get initial cache
            cache1 = await get_cache()

            # Reset cache
            await reset_cache()

            # Get new cache
            cache2 = await get_cache()

            # Should be different instances
            assert cache1 is not cache2


class TestCacheProtocol:
    """Test that cache implementations follow the protocol."""

    @pytest.mark.asyncio
    async def test_memory_cache_protocol(self):
        """Test that memory cache follows the protocol."""
        from backend.app.services.memory_cache import InMemoryCacheService

        cache = InMemoryCacheService()

        # Test basic operations
        await cache.set("test_key", "test_value", ttl=300)
        value = await cache.get("test_key")
        assert value == "test_value"

        deleted = await cache.delete("test_key")
        assert deleted is True

        value = await cache.get("test_key")
        assert value is None

        await cache.clear()

    @pytest.mark.asyncio
    async def test_redis_cache_protocol(self):
        """Test that Redis cache follows the protocol."""
        from backend.app.services.redis_cache import RedisCacheService

        # Mock Redis client
        mock_redis = AsyncMock()
        cache = RedisCacheService(redis_client=mock_redis)

        # Test set operation
        await cache.set("test_key", "test_value", ttl=300)
        mock_redis.setex.assert_called_once()

        # Test get operation
        mock_redis.get.return_value = "test_value"
        value = await cache.get("test_key")
        assert value == "test_value"

        # Test delete operation
        mock_redis.delete.return_value = 1
        deleted = await cache.delete("test_key")
        assert deleted is True

        # Test clear operation
        await cache.clear()
        mock_redis.flushdb.assert_called_once()
