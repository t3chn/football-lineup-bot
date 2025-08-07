"""Tests for prediction service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.services.prediction import PredictionService


@pytest.fixture
def prediction_service():
    """Create prediction service for testing."""
    with patch("backend.app.services.prediction.get_cache") as mock_cache:
        mock_cache.return_value = MagicMock()
        service = PredictionService()
        yield service


@pytest.mark.asyncio
async def test_get_prediction_from_cache(prediction_service):
    """Test getting prediction from cache."""
    cached_data = {
        "team": "Arsenal",
        "formation": "4-3-3",
        "lineup": [],
        "confidence": 0.8,
        "source": "api",
        "cached": False,
        "timestamp": "2025-01-01T00:00:00",
    }

    prediction_service.cache.get.return_value = cached_data

    result = await prediction_service.get_prediction("Arsenal")

    assert result.team == "Arsenal"
    assert result.cached is True
    prediction_service.cache.get.assert_called_once_with("prediction:arsenal")


@pytest.mark.asyncio
async def test_get_prediction_from_api(prediction_service):
    """Test getting prediction from API when not cached."""
    prediction_service.cache.get.return_value = None

    with patch("backend.app.services.prediction.FootballAPIClient") as mock_client:
        mock_api = AsyncMock()
        mock_api.search_team.return_value = {"response": [{"team": {"id": 123, "name": "Arsenal"}}]}
        mock_api.get_team_fixtures.return_value = {"response": []}
        mock_client.return_value.__aenter__.return_value = mock_api

        result = await prediction_service.get_prediction("Arsenal")

        assert result.team == "Arsenal"
        assert result.cached is False
        assert len(result.lineup) == 11  # Mock lineup has 11 players
        prediction_service.cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_prediction_team_not_found(prediction_service):
    """Test error when team not found."""
    prediction_service.cache.get.return_value = None

    with patch("backend.app.services.prediction.FootballAPIClient") as mock_client:
        mock_api = AsyncMock()
        mock_api.search_team.return_value = {"response": []}
        mock_client.return_value.__aenter__.return_value = mock_api

        with pytest.raises(ValueError, match="Team 'InvalidTeam' not found"):
            await prediction_service.get_prediction("InvalidTeam")


def test_generate_mock_lineup(prediction_service):
    """Test mock lineup generation."""
    lineup = prediction_service._generate_mock_lineup()

    assert len(lineup) == 11
    assert lineup[0].position == "GK"
    assert lineup[0].number == 1

    # Check captain
    captains = [p for p in lineup if p.is_captain]
    assert len(captains) == 1
    assert captains[0].number == 10
