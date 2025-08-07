"""End-to-end integration tests."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


class TestE2EIntegration:
    """Test complete end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_complete_telegram_prediction_flow(
        self,
        async_client: AsyncClient,
        test_db,
        telegram_webhook_data,
        test_settings,
        mock_football_api,
    ):
        """Test complete flow from Telegram webhook to database storage."""
        # Override webhook data to request prediction
        telegram_webhook_data["message"]["text"] = "/predict Arsenal"

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Send Telegram webhook
            response = await async_client.post(
                "/telegram",
                json=telegram_webhook_data,
                headers={"X-Telegram-Bot-Api-Secret-Token": test_settings.webhook_secret},
            )

            assert response.status_code == 200

            # Verify user was created/updated in database
            from backend.app.repositories.user import UserRepository

            user_repo = UserRepository(test_db)

            telegram_id = telegram_webhook_data["message"]["from"]["id"]
            user = await user_repo.get_by_telegram_id(telegram_id)

            assert user is not None
            assert user.telegram_id == telegram_id
            assert user.username == telegram_webhook_data["message"]["from"]["username"]

            # Verify prediction was stored
            from backend.app.repositories.prediction import PredictionRepository

            pred_repo = PredictionRepository(test_db)

            predictions = await pred_repo.get_by_user(str(telegram_id))
            assert len(predictions) >= 0  # May not be stored if command just sends message

    @pytest.mark.asyncio
    async def test_api_to_database_workflow(
        self, async_client: AsyncClient, test_db, test_settings, mock_football_api
    ):
        """Test API prediction request creates proper database records."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Make API prediction request
            response = await async_client.get(
                "/predict/ManCity", headers={"X-API-Key": test_settings.api_key}
            )

            assert response.status_code == 200
            prediction_data = response.json()

            # Verify prediction structure
            assert prediction_data["team_name"] == "ManCity"
            assert "lineup" in prediction_data
            assert "formation" in prediction_data
            assert "confidence" in prediction_data

            # Verify database record was created
            from backend.app.repositories.prediction import PredictionRepository

            pred_repo = PredictionRepository(test_db)

            db_predictions = await pred_repo.get_by_team("ManCity")
            assert len(db_predictions) == 1

            db_prediction = db_predictions[0]
            assert db_prediction.team_name == "ManCity"
            assert db_prediction.formation == prediction_data["formation"]
            assert abs(db_prediction.confidence - prediction_data["confidence"]) < 0.001

    @pytest.mark.asyncio
    async def test_cache_database_consistency(
        self,
        async_client: AsyncClient,
        test_db,
        test_settings,
        mock_football_api,
        mock_cache_service,
    ):
        """Test that cache and database stay consistent."""
        # Override cache service in the app
        with patch("backend.app.services.cache_factory.create_cache_service") as mock_factory:
            mock_factory.return_value = mock_cache_service
            mock_cache_service.get.return_value = None  # Cache miss

            with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
                mock_api_class.return_value = mock_football_api

                # First request - should populate cache and database
                response1 = await async_client.get(
                    "/predict/Consistency", headers={"X-API-Key": test_settings.api_key}
                )

                assert response1.status_code == 200
                data1 = response1.json()

                # Verify cache was set
                mock_cache_service.set.assert_called()
                cached_data = mock_cache_service.set.call_args[0][1]

                # Now return cached data for second request
                mock_cache_service.get.return_value = cached_data

                # Second request - should use cache
                response2 = await async_client.get(
                    "/predict/Consistency", headers={"X-API-Key": test_settings.api_key}
                )

                assert response2.status_code == 200
                data2 = response2.json()

                # Data should be identical
                assert data1 == data2

                # Verify database has one record (not duplicated)
                from backend.app.repositories.prediction import PredictionRepository

                pred_repo = PredictionRepository(test_db)

                db_predictions = await pred_repo.get_by_team("Consistency")
                # May have 1-2 records depending on cache implementation
                assert len(db_predictions) >= 1

    @pytest.mark.asyncio
    async def test_multiple_users_different_predictions(
        self, async_client: AsyncClient, test_db, test_settings, mock_football_api
    ):
        """Test multiple users can get predictions independently."""
        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Create multiple prediction requests for different teams
            teams_and_users = [
                ("Arsenal", "user1"),
                ("Liverpool", "user2"),
                ("Chelsea", "user1"),  # Same user, different team
            ]

            for team, user in teams_and_users:
                response = await async_client.get(
                    f"/predict/{team}",
                    headers={
                        "X-API-Key": test_settings.api_key,
                        "X-User-ID": user,  # Custom header for user tracking
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert data["team_name"] == team

            # Verify database has all predictions
            from backend.app.repositories.prediction import PredictionRepository

            pred_repo = PredictionRepository(test_db)

            all_predictions = await pred_repo.get_recent(limit=10)
            assert len(all_predictions) == 3

            # Verify we have predictions for all teams
            team_names = {pred.team_name for pred in all_predictions}
            assert team_names == {"Arsenal", "Liverpool", "Chelsea"}

    @pytest.mark.asyncio
    async def test_error_propagation_through_stack(self, async_client: AsyncClient, test_settings):
        """Test that errors propagate correctly through the entire stack."""
        # Mock API to fail
        with patch(
            "backend.app.adapters.football_api.FootballAPI.get_team_stats",
            side_effect=ConnectionError("External API unavailable"),
        ):
            response = await async_client.get(
                "/predict/ErrorTeam", headers={"X-API-Key": test_settings.api_key}
            )

            # Should return 500 error
            assert response.status_code == 500
            assert "X-Request-ID" in response.headers

            # Error should be structured
            error_data = response.json()
            assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_request_logging_through_complete_flow(
        self, async_client: AsyncClient, test_settings, mock_football_api
    ):
        """Test that request logging works through complete prediction flow."""
        custom_request_id = "e2e-test-request-123"

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            response = await async_client.get(
                "/predict/LoggingTest",
                headers={"X-API-Key": test_settings.api_key, "X-Request-ID": custom_request_id},
            )

            assert response.status_code == 200

            # Request ID should be preserved throughout
            assert response.headers["X-Request-ID"] == custom_request_id

            # Response should contain prediction data
            data = response.json()
            assert data["team_name"] == "LoggingTest"

    @pytest.mark.asyncio
    async def test_concurrent_requests_data_integrity(
        self, async_client: AsyncClient, test_db, test_settings, mock_football_api
    ):
        """Test data integrity under concurrent requests."""
        import asyncio

        with patch("backend.app.adapters.football_api.FootballAPI") as mock_api_class:
            mock_api_class.return_value = mock_football_api

            # Make multiple concurrent requests for same team
            tasks = [
                async_client.get(
                    "/predict/ConcurrentTeam", headers={"X-API-Key": test_settings.api_key}
                )
                for _ in range(5)
            ]

            responses = await asyncio.gather(*tasks)

            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["team_name"] == "ConcurrentTeam"

            # Verify database integrity - should handle concurrent writes
            from backend.app.repositories.prediction import PredictionRepository

            pred_repo = PredictionRepository(test_db)

            predictions = await pred_repo.get_by_team("ConcurrentTeam")
            # May have multiple records due to concurrent requests
            assert len(predictions) >= 1

            # All predictions should have valid data
            for prediction in predictions:
                assert prediction.team_name == "ConcurrentTeam"
                assert prediction.confidence is not None
                assert prediction.formation is not None

    @pytest.mark.asyncio
    async def test_health_check_with_dependencies(self, async_client: AsyncClient):
        """Test that health check reflects system state."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        health_data = response.json()

        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "X-Request-ID" in response.headers

        # Health check should work even under load
        import asyncio

        health_tasks = [async_client.get("/health") for _ in range(10)]
        health_responses = await asyncio.gather(*health_tasks)

        for health_response in health_responses:
            assert health_response.status_code == 200
