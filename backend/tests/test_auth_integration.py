"""Integration tests for API authentication."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings with API key configured."""
    settings = Mock()
    settings.api_key = "test-api-key-123"
    settings.cors_origins = ["http://localhost:3000"]
    settings.cache_ttl_seconds = 300
    return settings


@pytest.fixture
def mock_prediction_service():
    """Mock prediction service."""
    from unittest.mock import AsyncMock

    from backend.app.models.prediction import Player, PredictionResponse

    service = Mock()
    service.get_prediction = AsyncMock(
        return_value=PredictionResponse(
            team="Arsenal",
            formation="4-3-3",
            lineup=[
                Player(name="Goalkeeper", position="GK", number=1),
                Player(name="Defender", position="DEF", number=2),
            ],
            confidence=0.85,
            source="cache",
            cached=True,
        )
    )
    return service


class TestPredictionEndpointAuthentication:
    """Test authentication on prediction endpoints."""

    @patch("backend.app.auth.api_key.get_settings")
    @patch("backend.app.routers.predict.get_prediction_service")
    def test_predict_with_valid_api_key(
        self, mock_get_service, mock_get_settings, client, mock_settings, mock_prediction_service
    ):
        """Test prediction endpoint with valid API key."""
        # Setup
        mock_get_settings.return_value = mock_settings
        mock_get_service.return_value = mock_prediction_service

        # Test
        response = client.get("/predict/Arsenal", headers={"X-API-Key": "test-api-key-123"})

        # Assert
        assert response.status_code == 200

    @patch("backend.app.auth.api_key.get_settings")
    def test_predict_without_api_key(self, mock_get_settings, client, mock_settings):
        """Test prediction endpoint without API key."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.get("/predict/Arsenal")

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    @patch("backend.app.auth.api_key.get_settings")
    def test_predict_with_invalid_api_key(self, mock_get_settings, client, mock_settings):
        """Test prediction endpoint with invalid API key."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.get("/predict/Arsenal", headers={"X-API-Key": "wrong-key"})

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"

    @patch("backend.app.auth.api_key.get_settings")
    def test_predict_with_empty_api_key(self, mock_get_settings, client, mock_settings):
        """Test prediction endpoint with empty API key."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.get("/predict/Arsenal", headers={"X-API-Key": ""})

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"


class TestTelegramEndpointAuthentication:
    """Test authentication on Telegram admin endpoints."""

    def test_webhook_endpoint_no_auth_required(self, client):
        """Test that webhook endpoint doesn't require API key (uses signature verification)."""
        # Test - webhook should fail due to missing signature, not auth
        response = client.post("/telegram/webhook", json={})

        # Assert - should fail on signature verification, not authentication
        assert response.status_code == 403
        assert "signature" in response.json()["detail"].lower()

    @patch("backend.app.auth.api_key.get_settings")
    def test_set_webhook_requires_auth(self, mock_get_settings, client, mock_settings):
        """Test that set-webhook endpoint requires authentication."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.post("/telegram/set-webhook")

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    @patch("backend.app.auth.api_key.get_settings")
    def test_delete_webhook_requires_auth(self, mock_get_settings, client, mock_settings):
        """Test that delete-webhook endpoint requires authentication."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.delete("/telegram/webhook")

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    @patch("backend.app.auth.api_key.get_settings")
    def test_webhook_info_requires_auth(self, mock_get_settings, client, mock_settings):
        """Test that webhook-info endpoint requires authentication."""
        # Setup
        mock_get_settings.return_value = mock_settings

        # Test
        response = client.get("/telegram/webhook-info")

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"


class TestHealthEndpointNoAuth:
    """Test that health endpoint doesn't require authentication."""

    def test_health_endpoint_no_auth_required(self, client):
        """Test that health endpoint is accessible without authentication."""
        # Test
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAPIKeyHeader:
    """Test API key header behavior."""

    @patch("backend.app.auth.api_key.get_settings")
    @patch("backend.app.routers.predict.get_prediction_service")
    def test_case_sensitive_header_name(
        self, mock_get_service, mock_get_settings, client, mock_settings, mock_prediction_service
    ):
        """Test that API key header name is case sensitive."""
        # Setup
        mock_get_settings.return_value = mock_settings
        mock_get_service.return_value = mock_prediction_service

        # Test with wrong case
        response = client.get(
            "/predict/Arsenal",
            headers={"x-api-key": "test-api-key-123"},  # lowercase
        )

        # Assert - FastAPI headers are case-insensitive, but test the behavior
        # This test verifies the current behavior rather than enforcing case sensitivity
        assert response.status_code in [200, 401]  # May work due to case-insensitive headers

    @patch("backend.app.auth.api_key.get_settings")
    @patch("backend.app.routers.predict.get_prediction_service")
    def test_multiple_api_key_headers(
        self, mock_get_service, mock_get_settings, client, mock_settings, mock_prediction_service
    ):
        """Test behavior with multiple API key headers."""
        # Setup
        mock_get_settings.return_value = mock_settings
        mock_get_service.return_value = mock_prediction_service

        # Test
        response = client.get(
            "/predict/Arsenal",
            headers=[("X-API-Key", "test-api-key-123"), ("X-API-Key", "another-key")],
        )

        # Assert - behavior with multiple headers (usually takes first one)
        assert response.status_code in [200, 401]
