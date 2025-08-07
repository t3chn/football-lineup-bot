"""Service integration tests."""

from unittest.mock import patch

import pytest

from backend.app.services.prediction import PredictionService


class TestServiceIntegration:
    """Test service layer integration with dependencies."""

    @pytest.fixture
    def prediction_service(self, mock_cache_service, test_db):
        """Create prediction service with mocked dependencies."""
        return PredictionService(cache_service=mock_cache_service, db_session=test_db)

    @pytest.mark.asyncio
    async def test_prediction_service_full_flow(self, prediction_service, mock_football_api):
        """Test complete prediction service workflow."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Make prediction
            result = await prediction_service.predict("Arsenal", "test_user")

            # Verify result structure
            assert "lineup" in result
            assert "formation" in result
            assert "confidence" in result
            assert "team_name" in result

            assert result["team_name"] == "Arsenal"
            assert len(result["lineup"]) == 11
            assert result["formation"] in ["4-3-3", "4-4-2", "3-5-2"]
            assert 0 <= result["confidence"] <= 1

            # Verify external API was called
            mock_football_api.get_team_stats.assert_called_once_with("Arsenal")

    @pytest.mark.asyncio
    async def test_prediction_service_caching(
        self, prediction_service, mock_football_api, mock_cache_service
    ):
        """Test that prediction service properly uses caching."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Configure cache to return None initially (cache miss)
            mock_cache_service.get.return_value = None

            # First call - should hit API and cache result
            result1 = await prediction_service.predict("Liverpool", "test_user")

            # Verify API was called
            mock_football_api.get_team_stats.assert_called_once_with("Liverpool")

            # Verify cache set was called
            assert mock_cache_service.set.called

            # Configure cache to return cached result
            mock_cache_service.get.return_value = result1

            # Reset API mock
            mock_football_api.reset_mock()

            # Second call - should use cache
            result2 = await prediction_service.predict("Liverpool", "test_user")

            # Verify API was not called again
            mock_football_api.get_team_stats.assert_not_called()

            # Results should be identical
            assert result1 == result2

    @pytest.mark.asyncio
    async def test_prediction_service_database_integration(
        self, prediction_service, mock_football_api, test_db
    ):
        """Test that predictions are saved to database."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Make prediction
            result = await prediction_service.predict("Chelsea", "test_user_123")

            # Verify prediction was saved to database
            from backend.app.repositories.prediction import PredictionRepository

            repo = PredictionRepository(test_db)
            predictions = await repo.get_by_team("Chelsea")

            assert len(predictions) == 1
            saved_prediction = predictions[0]

            assert saved_prediction.team_name == "Chelsea"
            assert saved_prediction.created_by == "test_user_123"
            assert saved_prediction.confidence == result["confidence"]
            assert saved_prediction.formation == result["formation"]

    @pytest.mark.asyncio
    async def test_prediction_service_error_handling(self, prediction_service, mock_cache_service):
        """Test prediction service error handling."""
        # Mock API to raise exception
        with patch(
            "backend.app.adapters.football_api.FootballAPI.get_team_stats",
            side_effect=Exception("API Error"),
        ):
            # Should raise the exception
            with pytest.raises(Exception, match="API Error"):
                await prediction_service.predict("ErrorTeam", "test_user")

            # Cache should not be called on error
            mock_cache_service.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_prediction_service_cache_error_handling(
        self, prediction_service, mock_football_api
    ):
        """Test prediction service handles cache errors gracefully."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Mock cache to raise exception on get
            with patch.object(
                prediction_service.cache_service, "get", side_effect=Exception("Cache Error")
            ):
                # Should still work (fallback to API)
                result = await prediction_service.predict("CacheErrorTeam", "test_user")

                # Should get valid result
                assert "lineup" in result
                assert result["team_name"] == "CacheErrorTeam"

                # API should have been called
                mock_football_api.get_team_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_prediction_service_different_teams(self, prediction_service, mock_football_api):
        """Test prediction service handles different team names correctly."""
        teams = ["Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham"]

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            results = []
            for team in teams:
                result = await prediction_service.predict(team, f"user_{team.lower()}")
                results.append(result)

                # Verify each result
                assert result["team_name"] == team
                assert len(result["lineup"]) == 11
                assert "formation" in result
                assert "confidence" in result

            # Verify all teams were called
            assert mock_football_api.get_team_stats.call_count == len(teams)

            # Verify each team name was passed correctly
            called_teams = [
                call.args[0] for call in mock_football_api.get_team_stats.call_args_list
            ]
            assert set(called_teams) == set(teams)

    @pytest.mark.asyncio
    async def test_cache_service_integration_with_ttl(
        self, prediction_service, mock_football_api, mock_cache_service
    ):
        """Test cache service TTL behavior in prediction flow."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Mock cache get to return None (miss)
            mock_cache_service.get.return_value = None

            await prediction_service.predict("TTLTeam", "test_user")

            # Verify cache set was called with TTL
            mock_cache_service.set.assert_called_once()
            call_args = mock_cache_service.set.call_args

            # Should have been called with key, value, and TTL
            assert len(call_args[0]) >= 2  # key and value
            assert "ttl" in call_args[1] or len(call_args[0]) > 2  # TTL parameter

    @pytest.mark.asyncio
    async def test_database_session_rollback_on_error(
        self, mock_cache_service, test_db, mock_football_api
    ):
        """Test that database session is properly handled on errors."""
        prediction_service = PredictionService(cache_service=mock_cache_service, db_session=test_db)

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Mock database save to raise exception
            with (
                patch(
                    "backend.app.repositories.prediction.PredictionRepository.create",
                    side_effect=Exception("DB Error"),
                ),
                pytest.raises(Exception, match="DB Error"),
            ):
                await prediction_service.predict("DBErrorTeam", "test_user")

                # Database should be in clean state for next test
                # This verifies session handling doesn't leave transactions open
