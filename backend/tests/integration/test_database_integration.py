"""Database integration tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.prediction import PredictionRepository
from backend.app.repositories.user import UserRepository


class TestDatabaseIntegration:
    """Test database operations and relationships."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_db: AsyncSession):
        """Test user creation and retrieval."""
        user_repo = UserRepository(test_db)

        # Create user
        user_data = {
            "telegram_id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "language_code": "en",
        }

        user = await user_repo.create(**user_data)

        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.is_active is True

        # Retrieve user
        retrieved_user = await user_repo.get_by_telegram_id(123456789)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.telegram_id == user.telegram_id

    @pytest.mark.asyncio
    async def test_save_prediction_history(self, test_db: AsyncSession):
        """Test saving prediction to database."""
        prediction_repo = PredictionRepository(test_db)

        # Create prediction
        lineup_data = {
            "formation": "4-3-3",
            "players": [
                {"name": "Player 1", "position": "GK"},
                {"name": "Player 2", "position": "CB"},
                {"name": "Player 3", "position": "CB"},
                {"name": "Player 4", "position": "LB"},
                {"name": "Player 5", "position": "RB"},
                {"name": "Player 6", "position": "CDM"},
                {"name": "Player 7", "position": "CM"},
                {"name": "Player 8", "position": "CAM"},
                {"name": "Player 9", "position": "LW"},
                {"name": "Player 10", "position": "ST"},
                {"name": "Player 11", "position": "RW"},
            ],
        }

        prediction = await prediction_repo.create(
            team_name="Arsenal",
            formation="4-3-3",
            lineup=lineup_data,
            confidence=0.85,
            created_by="test_user",
        )

        assert prediction.id is not None
        assert prediction.team_name == "Arsenal"
        assert prediction.formation == "4-3-3"
        assert prediction.confidence == 0.85
        assert prediction.lineup == lineup_data
        assert prediction.created_by == "test_user"
        assert prediction.created_at is not None

    @pytest.mark.asyncio
    async def test_get_prediction_history_by_team(self, test_db: AsyncSession):
        """Test retrieving prediction history for a specific team."""
        prediction_repo = PredictionRepository(test_db)

        # Create multiple predictions for different teams
        teams = ["Arsenal", "Liverpool", "Arsenal", "Chelsea"]

        for _i, team in enumerate(teams):
            await prediction_repo.create(
                team_name=team,
                formation="4-3-3",
                lineup={"formation": "4-3-3", "players": []},
                confidence=0.8 + (_i * 0.05),
                created_by=f"user_{_i}",
            )

        # Get Arsenal predictions
        arsenal_predictions = await prediction_repo.get_by_team("Arsenal")
        assert len(arsenal_predictions) == 2

        # Verify they're sorted by creation time (most recent first)
        assert arsenal_predictions[0].confidence > arsenal_predictions[1].confidence

        # Get Liverpool predictions
        liverpool_predictions = await prediction_repo.get_by_team("Liverpool")
        assert len(liverpool_predictions) == 1
        assert liverpool_predictions[0].team_name == "Liverpool"

    @pytest.mark.asyncio
    async def test_get_recent_predictions(self, test_db: AsyncSession):
        """Test retrieving recent predictions across all teams."""
        prediction_repo = PredictionRepository(test_db)

        # Create predictions
        teams = ["Arsenal", "Liverpool", "Chelsea", "ManCity", "Tottenham"]

        for _i, team in enumerate(teams):
            await prediction_repo.create(
                team_name=team,
                formation="4-3-3",
                lineup={"formation": "4-3-3", "players": []},
                confidence=0.8,
                created_by="test_user",
            )

        # Get recent predictions (limit 3)
        recent_predictions = await prediction_repo.get_recent(limit=3)
        assert len(recent_predictions) == 3

        # Should be sorted by creation time (most recent first)
        team_names = [pred.team_name for pred in recent_predictions]
        assert "Tottenham" in team_names  # Most recent
        assert "ManCity" in team_names
        assert "Chelsea" in team_names

    @pytest.mark.asyncio
    async def test_user_prediction_relationship(self, test_db: AsyncSession):
        """Test relationship between users and their predictions."""
        user_repo = UserRepository(test_db)
        prediction_repo = PredictionRepository(test_db)

        # Create user
        user = await user_repo.create(
            telegram_id=987654321,
            username="predictionuser",
            first_name="Prediction",
            last_name="User",
        )

        # Create predictions for this user
        for team in ["Arsenal", "Liverpool"]:
            await prediction_repo.create(
                team_name=team,
                formation="4-3-3",
                lineup={"formation": "4-3-3", "players": []},
                confidence=0.8,
                created_by=str(user.telegram_id),
            )

        # Get user's predictions
        user_predictions = await prediction_repo.get_by_user(str(user.telegram_id))
        assert len(user_predictions) == 2

        team_names = [pred.team_name for pred in user_predictions]
        assert "Arsenal" in team_names
        assert "Liverpool" in team_names

    @pytest.mark.asyncio
    async def test_update_user_activity(self, test_db: AsyncSession):
        """Test updating user last activity."""
        user_repo = UserRepository(test_db)

        # Create user
        user = await user_repo.create(
            telegram_id=555666777, username="activeuser", first_name="Active", last_name="User"
        )

        original_updated_at = user.updated_at

        # Update last activity
        await user_repo.update_last_activity(user.telegram_id)

        # Retrieve updated user
        updated_user = await user_repo.get_by_telegram_id(user.telegram_id)
        assert updated_user.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_prediction_with_floating_point_precision(self, test_db: AsyncSession):
        """Test that floating point confidence values are stored correctly."""
        prediction_repo = PredictionRepository(test_db)

        confidence_values = [0.1, 0.33333, 0.66666, 0.99999]

        for i, confidence in enumerate(confidence_values):
            prediction = await prediction_repo.create(
                team_name=f"Team{i}",
                formation="4-3-3",
                lineup={"formation": "4-3-3", "players": []},
                confidence=confidence,
                created_by="test_user",
            )

            # Verify precision is maintained
            assert abs(prediction.confidence - confidence) < 0.00001

    @pytest.mark.asyncio
    async def test_json_lineup_storage(self, test_db: AsyncSession):
        """Test that complex lineup JSON data is stored and retrieved correctly."""
        prediction_repo = PredictionRepository(test_db)

        complex_lineup = {
            "formation": "4-2-3-1",
            "players": [
                {
                    "name": "Goalkeeper One",
                    "position": "GK",
                    "stats": {"saves": 10, "clean_sheets": 5},
                    "attributes": ["tall", "good_reflexes"],
                },
                {
                    "name": "Defender One",
                    "position": "CB",
                    "stats": {"tackles": 15, "interceptions": 8},
                    "attributes": ["strong", "aerial_threat"],
                },
            ],
            "tactics": {"style": "possession", "press_intensity": "high", "defensive_line": "mid"},
        }

        prediction = await prediction_repo.create(
            team_name="ComplexTeam",
            formation="4-2-3-1",
            lineup=complex_lineup,
            confidence=0.95,
            created_by="test_user",
        )

        # Retrieve and verify complex JSON is intact
        retrieved_prediction = await prediction_repo.get_by_id(prediction.id)
        assert retrieved_prediction.lineup == complex_lineup
        assert retrieved_prediction.lineup["tactics"]["style"] == "possession"
        assert len(retrieved_prediction.lineup["players"]) == 2
        assert retrieved_prediction.lineup["players"][0]["attributes"] == ["tall", "good_reflexes"]

    @pytest.mark.asyncio
    async def test_database_constraints(self, test_db: AsyncSession):
        """Test database constraints and validations."""
        user_repo = UserRepository(test_db)

        # Create user
        await user_repo.create(
            telegram_id=999888777,
            username="constraintuser",
            first_name="Constraint",
            last_name="User",
        )

        # Try to create another user with same telegram_id (should handle gracefully)
        existing_user = await user_repo.get_or_create_user(
            telegram_id=999888777,
            username="differentuser",
            first_name="Different",
            last_name="User",
        )

        # Should return existing user, not create new one
        assert existing_user.username == "constraintuser"
        assert existing_user.first_name == "Constraint"
