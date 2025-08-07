"""API integration tests."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


class TestAPIIntegration:
    """Test complete API workflows."""

    @pytest.mark.asyncio
    async def test_health_endpoint_integration(self, async_client: AsyncClient):
        """Test health endpoint returns proper response."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_root_endpoint_integration(self, async_client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Football Lineup Bot API"
        assert "version" in data
        assert data["status"] == "running"
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_prediction_flow_without_auth(self, async_client: AsyncClient):
        """Test prediction endpoint requires authentication."""
        response = await async_client.get("/predict/Arsenal")

        assert response.status_code == 401
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_prediction_flow_with_auth(
        self, async_client: AsyncClient, test_settings, mock_football_api
    ):
        """Test complete prediction flow with authentication."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            response = await async_client.get(
                "/predict/Arsenal", headers={"X-API-Key": test_settings.api_key}
            )

            assert response.status_code == 200
            data = response.json()

            # Check response structure
            assert "lineup" in data
            assert "formation" in data
            assert "confidence" in data
            assert "team_name" in data

            # Check lineup details
            assert len(data["lineup"]) == 11
            assert data["formation"] in ["4-3-3", "4-4-2", "3-5-2"]
            assert 0 <= data["confidence"] <= 1
            assert data["team_name"] == "Arsenal"

            # Check request ID header
            assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_prediction_caching_behavior(
        self, async_client: AsyncClient, test_settings, mock_football_api
    ):
        """Test that predictions are properly cached."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # First request
            response1 = await async_client.get(
                "/predict/Liverpool", headers={"X-API-Key": test_settings.api_key}
            )

            assert response1.status_code == 200
            data1 = response1.json()

            # Second request (should use cache)
            response2 = await async_client.get(
                "/predict/Liverpool", headers={"X-API-Key": test_settings.api_key}
            )

            assert response2.status_code == 200
            data2 = response2.json()

            # Should return same data (from cache)
            assert data1 == data2

    @pytest.mark.asyncio
    async def test_invalid_team_name_validation(self, async_client: AsyncClient, test_settings):
        """Test validation for invalid team names."""
        invalid_names = ["", "a", "x" * 101, "Team@123", "12345"]

        for team_name in invalid_names:
            response = await async_client.get(
                f"/predict/{team_name}", headers={"X-API-Key": test_settings.api_key}
            )

            assert response.status_code == 422  # Validation error
            assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_telegram_webhook_integration(
        self, async_client: AsyncClient, telegram_webhook_data, test_settings
    ):
        """Test Telegram webhook processing."""
        response = await async_client.post(
            "/telegram",
            json=telegram_webhook_data,
            headers={"X-Telegram-Bot-Api-Secret-Token": test_settings.webhook_secret},
        )

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_telegram_webhook_without_auth(
        self, async_client: AsyncClient, telegram_webhook_data
    ):
        """Test Telegram webhook requires proper authentication."""
        # Without secret token
        response = await async_client.post("/telegram", json=telegram_webhook_data)

        assert response.status_code == 401
        assert "X-Request-ID" in response.headers

        # With wrong secret token
        response = await async_client.post(
            "/telegram",
            json=telegram_webhook_data,
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-token"},
        )

        assert response.status_code == 401
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, async_client: AsyncClient, test_settings):
        """Test that errors are properly handled and logged."""
        with patch(
            "backend.app.services.prediction.PredictionService.predict",
            side_effect=Exception("Test error"),
        ):
            response = await async_client.get(
                "/predict/Arsenal", headers={"X-API-Key": test_settings.api_key}
            )

            assert response.status_code == 500
            assert "X-Request-ID" in response.headers

            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_cors_headers(self, async_client: AsyncClient):
        """Test CORS headers are properly set."""
        response = await async_client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # CORS preflight should be handled
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(
        self, async_client: AsyncClient, test_settings, mock_football_api
    ):
        """Test handling multiple concurrent requests."""
        import asyncio

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Make multiple concurrent requests
            tasks = [
                async_client.get(f"/predict/Team{i}", headers={"X-API-Key": test_settings.api_key})
                for i in range(5)
            ]

            responses = await asyncio.gather(*tasks)

            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                assert "X-Request-ID" in response.headers

            # Each should have unique request ID
            request_ids = [resp.headers["X-Request-ID"] for resp in responses]
            assert len(set(request_ids)) == len(request_ids)

    @pytest.mark.asyncio
    async def test_request_id_consistency(self, async_client: AsyncClient):
        """Test request ID consistency across multiple endpoints."""
        custom_request_id = "test-request-123"

        # Test health endpoint
        response = await async_client.get("/health", headers={"X-Request-ID": custom_request_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_request_id

        # Test root endpoint
        response = await async_client.get("/", headers={"X-Request-ID": custom_request_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_request_id
