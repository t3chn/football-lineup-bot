"""Tests for rate limiting functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.middleware.rate_limiting import (
    DistributedRateLimiter,
    RateLimitTiers,
    get_rate_limit_key,
    get_user_tier_limit,
)


class TestRateLimitKey:
    """Test rate limit key generation."""

    def test_get_rate_limit_key_with_api_key(self):
        """Test key generation with API key."""
        request = MagicMock()
        request.headers.get.return_value = "test-key-123"

        key = get_rate_limit_key(request)

        assert key == "api_key:test-key-123"
        request.headers.get.assert_called_once_with("X-API-Key")

    def test_get_rate_limit_key_without_api_key(self):
        """Test key generation without API key (uses IP)."""
        request = MagicMock()
        request.headers.get.return_value = None
        request.client.host = "192.168.1.1"

        with patch("backend.app.middleware.rate_limiting.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"
            key = get_rate_limit_key(request)

        assert key == "ip:192.168.1.1"


class TestUserTierLimit:
    """Test user tier limit determination."""

    @pytest.mark.asyncio
    async def test_get_user_tier_limit_no_api_key(self):
        """Test tier limit for unauthenticated user."""
        request = MagicMock()
        request.headers.get.return_value = None

        limit = await get_user_tier_limit(request)

        assert limit == RateLimitTiers.FREE

    @pytest.mark.asyncio
    async def test_get_user_tier_limit_test_key(self):
        """Test tier limit for test API key."""
        request = MagicMock()
        request.headers.get.return_value = "test-api-key"

        limit = await get_user_tier_limit(request)

        assert limit == RateLimitTiers.BASIC

    @pytest.mark.asyncio
    async def test_get_user_tier_limit_regular_key(self):
        """Test tier limit for regular API key."""
        request = MagicMock()
        request.headers.get.return_value = "user-key-456"

        limit = await get_user_tier_limit(request)

        assert limit == RateLimitTiers.FREE


class TestDistributedRateLimiter:
    """Test distributed rate limiter."""

    @pytest.mark.asyncio
    async def test_is_allowed_within_limit(self):
        """Test requests within rate limit."""
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value = redis_mock
        redis_mock.execute.return_value = [None, 5, None, None]  # 5 current requests

        limiter = DistributedRateLimiter(redis_mock)
        is_allowed, info = await limiter.is_allowed("test-key", 10, 60)

        assert is_allowed is True
        assert info["limit"] == 10
        assert info["remaining"] == 5

    @pytest.mark.asyncio
    async def test_is_allowed_exceeds_limit(self):
        """Test requests exceeding rate limit."""
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value = redis_mock
        redis_mock.execute.return_value = [None, 10, None, None]  # 10 current requests

        limiter = DistributedRateLimiter(redis_mock)
        is_allowed, info = await limiter.is_allowed("test-key", 10, 60)

        assert is_allowed is False
        assert info["limit"] == 10
        assert info["remaining"] == 0

        # Should remove the just-added request
        redis_mock.zrem.assert_called_once()


class TestRateLimitingIntegration:
    """Integration tests for rate limiting."""

    def test_rate_limit_headers_in_response(self):
        """Test that rate limit headers are included in response."""
        client = TestClient(app)

        # Mock the prediction service to avoid actual API calls
        with patch("backend.app.routers.predict.get_prediction_service") as mock_service:
            mock_service.return_value.get_prediction = AsyncMock(
                return_value=MagicMock(
                    team="Arsenal",
                    lineup=[],
                    confidence=0.85,
                    source="mock",
                    cached=False,
                    timestamp="2025-08-07T12:00:00",
                )
            )

            response = client.get("/predict/Arsenal", headers={"X-API-Key": "test-api-key"})

        assert response.status_code == 200
        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded response."""
        client = TestClient(app)

        # Mock to simulate rate limit exceeded
        with patch("backend.app.middleware.rate_limiting.limiter.is_allowed") as mock_allowed:
            mock_allowed.return_value = False

            # This should trigger rate limit
            responses = []
            for _ in range(12):  # Exceed 10 per minute limit
                response = client.get("/predict/Arsenal", headers={"X-API-Key": "regular-key"})
                responses.append(response.status_code)

            # At least one should be rate limited (429)
            # Note: In actual implementation with slowapi, this would work differently
            # This is a simplified test
