"""Tests for prediction endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.prediction import Player, PredictionResponse


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_predict_endpoint_success(client):
    """Test successful prediction."""
    mock_prediction = PredictionResponse(
        team="Arsenal",
        formation="4-3-3",
        lineup=[
            Player(name="Player 1", number=1, position="GK"),
            Player(name="Player 2", number=2, position="RB"),
        ],
        confidence=0.8,
        source="api",
        cached=False,
    )

    with patch("backend.app.routers.predict.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(return_value=mock_prediction)

        response = client.get("/predict/Arsenal")
        assert response.status_code == 200
        data = response.json()
        assert data["team"] == "Arsenal"
        assert data["formation"] == "4-3-3"
        assert len(data["lineup"]) == 2


def test_predict_endpoint_team_not_found(client):
    """Test prediction when team not found."""
    with patch("backend.app.routers.predict.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(
            side_effect=ValueError("Team 'InvalidTeam' not found")
        )

        response = client.get("/predict/InvalidTeam")
        assert response.status_code == 404
        assert "Team 'InvalidTeam' not found" in response.json()["detail"]


def test_predict_endpoint_api_error(client):
    """Test prediction when external API fails."""
    import httpx

    with patch("backend.app.routers.predict.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(
            side_effect=httpx.TimeoutException("API timeout")
        )

        response = client.get("/predict/Arsenal")
        assert response.status_code == 503
        assert "External API error" in response.json()["detail"]


def test_predict_endpoint_cached_response(client):
    """Test prediction returns cached data."""
    mock_prediction = PredictionResponse(
        team="Chelsea",
        formation="3-5-2",
        lineup=[
            Player(name="Player 1", number=1, position="GK"),
        ],
        confidence=0.7,
        source="api",
        cached=True,
    )

    with patch("backend.app.routers.predict.get_prediction_service") as mock_service:
        mock_service.return_value.get_prediction = AsyncMock(return_value=mock_prediction)

        response = client.get("/predict/Chelsea")
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
