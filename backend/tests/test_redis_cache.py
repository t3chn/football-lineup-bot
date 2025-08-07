"""Tests for Redis cache service."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.app.services.redis_cache import RedisCacheService


class TestRedisCacheService:
    """Test Redis cache service."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def mock_settings(self):
        """Mock settings."""
        settings = Mock()
        settings.redis_url = "redis://localhost:6379/0"
        settings.cache_ttl_seconds = 300
        return settings

    @pytest.fixture
    def redis_cache(self, mock_redis, mock_settings):
        """Redis cache service with mocked dependencies."""
        with patch("backend.app.services.redis_cache.get_settings", return_value=mock_settings):
            cache = RedisCacheService(redis_client=mock_redis)
            return cache

    @pytest.mark.asyncio
    async def test_get_success_dict(self, redis_cache, mock_redis):
        """Test successful get operation with dict value."""
        # Setup
        test_data = {"key": "value", "number": 123}
        mock_redis.get.return_value = json.dumps(test_data)

        # Test
        result = await redis_cache.get("test_key")

        # Assert
        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_success_string(self, redis_cache, mock_redis):
        """Test successful get operation with string value."""
        # Setup
        mock_redis.get.return_value = "simple_string"

        # Test
        result = await redis_cache.get("test_key")

        # Assert
        assert result == "simple_string"
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_not_found(self, redis_cache, mock_redis):
        """Test get operation when key not found."""
        # Setup
        mock_redis.get.return_value = None

        # Test
        result = await redis_cache.get("missing_key")

        # Assert
        assert result is None
        mock_redis.get.assert_called_once_with("missing_key")

    @pytest.mark.asyncio
    async def test_get_redis_error(self, redis_cache, mock_redis):
        """Test get operation with Redis error."""
        # Setup
        import redis.exceptions

        mock_redis.get.side_effect = redis.exceptions.RedisError("Connection failed")

        # Test
        result = await redis_cache.get("test_key")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_set_dict_success(self, redis_cache, mock_redis):
        """Test successful set operation with dict."""
        # Setup
        test_data = {"key": "value", "number": 123}

        # Test
        await redis_cache.set("test_key", test_data, ttl=600)

        # Assert
        mock_redis.setex.assert_called_once_with(
            "test_key", 600, json.dumps(test_data, default=str)
        )

    @pytest.mark.asyncio
    async def test_set_string_success(self, redis_cache, mock_redis):
        """Test successful set operation with string."""
        # Test
        await redis_cache.set("test_key", "test_value")

        # Assert
        mock_redis.setex.assert_called_once_with("test_key", 300, "test_value")

    @pytest.mark.asyncio
    async def test_set_default_ttl(self, redis_cache, mock_redis):
        """Test set operation uses default TTL when not specified."""
        # Test
        await redis_cache.set("test_key", "test_value")

        # Assert - should use default TTL of 300
        mock_redis.setex.assert_called_once_with("test_key", 300, "test_value")

    @pytest.mark.asyncio
    async def test_set_redis_error(self, redis_cache, mock_redis):
        """Test set operation with Redis error (should not raise)."""
        # Setup
        import redis.exceptions

        mock_redis.setex.side_effect = redis.exceptions.RedisError("Connection failed")

        # Test - should not raise exception
        await redis_cache.set("test_key", "test_value")

        # Assert
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, redis_cache, mock_redis):
        """Test successful delete operation."""
        # Setup
        mock_redis.delete.return_value = 1

        # Test
        result = await redis_cache.delete("test_key")

        # Assert
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_not_found(self, redis_cache, mock_redis):
        """Test delete operation when key not found."""
        # Setup
        mock_redis.delete.return_value = 0

        # Test
        result = await redis_cache.delete("missing_key")

        # Assert
        assert result is False
        mock_redis.delete.assert_called_once_with("missing_key")

    @pytest.mark.asyncio
    async def test_clear_success(self, redis_cache, mock_redis):
        """Test successful clear operation."""
        # Test
        await redis_cache.clear()

        # Assert
        mock_redis.flushdb.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_true(self, redis_cache, mock_redis):
        """Test exists operation when key exists."""
        # Setup
        mock_redis.exists.return_value = 1

        # Test
        result = await redis_cache.exists("test_key")

        # Assert
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_false(self, redis_cache, mock_redis):
        """Test exists operation when key doesn't exist."""
        # Setup
        mock_redis.exists.return_value = 0

        # Test
        result = await redis_cache.exists("missing_key")

        # Assert
        assert result is False
        mock_redis.exists.assert_called_once_with("missing_key")

    @pytest.mark.asyncio
    async def test_ttl_success(self, redis_cache, mock_redis):
        """Test TTL operation."""
        # Setup
        mock_redis.ttl.return_value = 120

        # Test
        result = await redis_cache.ttl("test_key")

        # Assert
        assert result == 120
        mock_redis.ttl.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_ping_success(self, redis_cache, mock_redis):
        """Test successful ping operation."""
        # Setup
        mock_redis.ping.return_value = True

        # Test
        result = await redis_cache.ping()

        # Assert
        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_failure(self, redis_cache, mock_redis):
        """Test ping operation failure."""
        # Setup
        import redis.exceptions

        mock_redis.ping.side_effect = redis.exceptions.RedisError("Connection failed")

        # Test
        result = await redis_cache.ping()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_close(self, redis_cache, mock_redis):
        """Test close operation."""
        # Test
        await redis_cache.close()

        # Assert
        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_json_serialization_complex(self, redis_cache, mock_redis):
        """Test JSON serialization of complex objects."""
        from datetime import datetime

        # Setup
        test_data = {
            "string": "value",
            "number": 123,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "datetime": datetime.now(),
        }

        # Test
        await redis_cache.set("test_key", test_data)

        # Assert - should serialize datetime to string
        mock_redis.setex.assert_called_once()
        args, kwargs = mock_redis.setex.call_args
        key, ttl, serialized_value = args

        # Should be valid JSON
        deserialized = json.loads(serialized_value)
        assert deserialized["string"] == "value"
        assert deserialized["number"] == 123
        assert deserialized["list"] == [1, 2, 3]
        assert deserialized["nested"]["key"] == "value"
        # datetime should be converted to string
        assert isinstance(deserialized["datetime"], str)
