"""Tests for cache service."""

import time
from unittest.mock import patch

import pytest

from backend.app.services.cache import CacheService, get_cache


@pytest.fixture
def cache():
    """Create cache instance for testing."""
    with patch("backend.app.services.cache.get_settings") as mock_settings:
        mock_settings.return_value.cache_ttl_seconds = 300
        cache = CacheService()
        cache.clear()
        yield cache
        cache.clear()


def test_cache_set_and_get(cache):
    """Test setting and getting values from cache."""
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent(cache):
    """Test getting non-existent key returns None."""
    assert cache.get("nonexistent") is None


def test_cache_ttl_expiry(cache):
    """Test cache TTL expiration."""
    cache.set("key1", "value1", ttl=0)
    time.sleep(0.01)
    assert cache.get("key1") is None


def test_cache_custom_ttl(cache):
    """Test cache with custom TTL."""
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"
    time.sleep(1.01)
    assert cache.get("key1") is None


def test_cache_delete(cache):
    """Test deleting key from cache."""
    cache.set("key1", "value1")
    assert cache.delete("key1") is True
    assert cache.get("key1") is None
    assert cache.delete("key1") is False


def test_cache_clear(cache):
    """Test clearing all cache."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.is_empty() is True


def test_cache_cleanup_expired(cache):
    """Test cleanup of expired entries."""
    cache.set("key1", "value1", ttl=0)
    cache.set("key2", "value2", ttl=100)
    time.sleep(0.01)

    removed = cache.cleanup_expired()
    assert removed == 1
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"


def test_cache_size(cache):
    """Test cache size tracking."""
    assert cache.size() == 0
    cache.set("key1", "value1")
    assert cache.size() == 1
    cache.set("key2", "value2")
    assert cache.size() == 2
    cache.delete("key1")
    assert cache.size() == 1


def test_cache_is_empty(cache):
    """Test cache empty check."""
    assert cache.is_empty() is True
    cache.set("key1", "value1")
    assert cache.is_empty() is False
    cache.clear()
    assert cache.is_empty() is True


def test_cache_complex_values(cache):
    """Test caching complex data types."""
    test_dict = {"name": "Test", "data": [1, 2, 3]}
    cache.set("complex", test_dict)
    retrieved = cache.get("complex")
    assert retrieved == test_dict
    assert retrieved["name"] == "Test"
    assert retrieved["data"] == [1, 2, 3]


def test_get_cache_singleton():
    """Test get_cache returns singleton instance."""
    # Clear any existing instance
    import backend.app.services.cache

    backend.app.services.cache._cache_instance = None

    with patch("backend.app.services.cache.get_settings") as mock_settings:
        mock_settings.return_value.cache_ttl_seconds = 300

        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2
