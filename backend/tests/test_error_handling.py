"""Tests for error handling and logging."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.exceptions import ExternalAPIError, TeamNotFoundError, TimeoutError
from backend.app.main import app
from backend.app.services.prediction import PredictionService


class TestErrorHandling:
    """Test error handling in the application."""

    def test_team_not_found_error(self):
        """Test handling of team not found error."""
        client = TestClient(app)

        with patch("backend.app.services.prediction.PredictionService.get_prediction") as mock_get:
            mock_get.side_effect = TeamNotFoundError("NonExistentTeam")

            response = client.get("/predict/NonExistentTeam")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_external_api_error(self):
        """Test handling of external API error."""
        client = TestClient(app)

        with patch("backend.app.services.prediction.PredictionService.get_prediction") as mock_get:
            mock_get.side_effect = ExternalAPIError("API is down", api_name="football-api")

            response = client.get("/predict/Arsenal")

            assert response.status_code == 500
            assert "API" in response.json()["detail"]

    def test_timeout_error(self):
        """Test handling of timeout error."""
        client = TestClient(app)

        with patch("backend.app.services.prediction.PredictionService.get_prediction") as mock_get:
            mock_get.side_effect = TimeoutError("Request timed out", timeout_seconds=30)

            response = client.get("/predict/Arsenal")

            assert response.status_code == 504
            assert "timed out" in response.json()["detail"].lower()

    def test_unexpected_error(self):
        """Test handling of unexpected errors."""
        client = TestClient(app)

        with patch("backend.app.services.prediction.PredictionService.get_prediction") as mock_get:
            mock_get.side_effect = RuntimeError("Something went wrong")

            response = client.get("/predict/Arsenal")

            assert response.status_code == 500
            assert "unexpected error" in response.json()["detail"].lower()


class TestLogging:
    """Test structured logging."""

    @pytest.mark.asyncio
    async def test_request_id_generation(self):
        """Test that request IDs are generated and tracked."""
        from backend.app.utils.logging import generate_request_id, request_id_var, set_request_id

        # Generate and set request ID
        request_id = generate_request_id()
        set_request_id(request_id)

        # Verify it's set in context
        assert request_id_var.get() == request_id
        assert len(request_id) == 36  # UUID length with hyphens

    @pytest.mark.asyncio
    async def test_logging_with_context(self):
        """Test that logging includes context information."""
        from backend.app.utils.logging import generate_request_id, get_logger, set_request_id

        logger = get_logger("test")
        request_id = generate_request_id()
        set_request_id(request_id)

        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = mock_get_logger.return_value
            mock_logger.bind.return_value = mock_logger

            log = logger.bind(team="Arsenal", user_id=123)
            log.info("Test message", extra_field="value")

            # Verify bind was called with context
            mock_logger.bind.assert_called()


class TestPredictionServiceErrorHandling:
    """Test error handling in prediction service."""

    @pytest.mark.asyncio
    async def test_api_timeout_handling(self):
        """Test handling of API timeouts."""
        service = PredictionService()

        with patch("backend.app.adapters.football_api.FootballAPIClient") as mock_client:
            mock_api = AsyncMock()
            mock_api.search_team.side_effect = httpx.TimeoutException("Timeout")
            mock_client.return_value.__aenter__.return_value = mock_api

            with pytest.raises(TimeoutError) as exc_info:
                await service.get_prediction("Arsenal")

            assert exc_info.value.status_code == 504
            assert "timeout" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        service = PredictionService()

        with patch("backend.app.adapters.football_api.FootballAPIClient") as mock_client:
            mock_api = AsyncMock()
            mock_api.search_team.side_effect = httpx.HTTPError("Server error")
            mock_client.return_value.__aenter__.return_value = mock_api

            with pytest.raises(ExternalAPIError) as exc_info:
                await service.get_prediction("Arsenal")

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_code == "EXTERNAL_API_ERROR"

    @pytest.mark.asyncio
    async def test_team_not_found_handling(self):
        """Test handling when team is not found."""
        service = PredictionService()
        service.cache.get.return_value = None

        with patch("backend.app.adapters.football_api.FootballAPIClient") as mock_client:
            mock_api = AsyncMock()
            mock_api.search_team.return_value = {"response": []}
            mock_client.return_value.__aenter__.return_value = mock_api

            with pytest.raises(TeamNotFoundError) as exc_info:
                await service.get_prediction("NonExistentTeam")

            assert exc_info.value.status_code == 404
            assert "NonExistentTeam" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_fallback_to_mock_on_unexpected_error(self):
        """Test fallback to mock data on unexpected errors."""
        service = PredictionService()
        service.cache.get.return_value = None

        with patch("backend.app.adapters.football_api.FootballAPIClient") as mock_client:
            mock_api = AsyncMock()
            # Simulate unexpected error during team search
            mock_api.search_team.return_value = {"response": [{"team": {"id": 1}}]}
            mock_api.get_team_fixtures.side_effect = RuntimeError("Unexpected")
            mock_client.return_value.__aenter__.return_value = mock_api

            # Should return mock data instead of raising
            result = await service.get_prediction("Arsenal")

            assert result.source == "mock"
            assert result.team == "Arsenal"
            assert len(result.lineup) == 11
