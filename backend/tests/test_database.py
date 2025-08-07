"""Tests for database functionality."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.database import Base
from backend.app.repositories.prediction import PredictionRepository
from backend.app.repositories.user import UserRepository


@pytest_asyncio.fixture
async def async_engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    """Create database session for tests."""
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


class TestUserRepository:
    """Test user repository operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a new user."""
        repo = UserRepository(db_session)

        user = await repo.create(
            username="testuser",
            email="test@example.com",
            api_key_hash="hashed_key",
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.api_key_hash == "hashed_key"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session):
        """Test getting user by username."""
        repo = UserRepository(db_session)

        # Create user
        await repo.create(username="findme", email="find@example.com")

        # Find user
        user = await repo.get_by_username("findme")

        assert user is not None
        assert user.username == "findme"
        assert user.email == "find@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session):
        """Test getting user by email."""
        repo = UserRepository(db_session)

        # Create user
        await repo.create(username="emailtest", email="email@test.com")

        # Find user by email
        user = await repo.get_by_email("email@test.com")

        assert user is not None
        assert user.username == "emailtest"
        assert user.email == "email@test.com"

    @pytest.mark.asyncio
    async def test_get_user_by_api_key_hash(self, db_session):
        """Test getting user by API key hash."""
        repo = UserRepository(db_session)

        # Create user
        await repo.create(username="apiuser", email="api@test.com", api_key_hash="unique_hash_123")

        # Find user by API key hash
        user = await repo.get_by_api_key_hash("unique_hash_123")

        assert user is not None
        assert user.username == "apiuser"
        assert user.api_key_hash == "unique_hash_123"

    @pytest.mark.asyncio
    async def test_update_last_login(self, db_session):
        """Test updating user's last login."""
        repo = UserRepository(db_session)

        # Create user
        user = await repo.create(username="logintest")
        assert user.last_login is None

        # Update last login
        updated_user = await repo.update_last_login(user.id)

        assert updated_user is not None
        assert updated_user.last_login is not None

    @pytest.mark.asyncio
    async def test_deactivate_user(self, db_session):
        """Test deactivating user."""
        repo = UserRepository(db_session)

        # Create user
        user = await repo.create(username="activeuser")
        assert user.is_active is True

        # Deactivate user
        deactivated_user = await repo.deactivate_user(user.id)

        assert deactivated_user is not None
        assert deactivated_user.is_active is False


class TestPredictionRepository:
    """Test prediction repository operations."""

    @pytest.mark.asyncio
    async def test_create_prediction(self, db_session):
        """Test creating a new prediction."""
        repo = PredictionRepository(db_session)

        lineup = [{"name": "Player 1", "position": "GK", "number": 1}]

        prediction = await repo.create(
            team_name="Test Team",
            formation="4-3-3",
            lineup=lineup,
            confidence=0.85,
            created_by="test_user",
        )

        assert prediction.id is not None
        assert prediction.team_name == "Test Team"
        assert prediction.formation == "4-3-3"
        assert prediction.lineup == lineup
        assert prediction.confidence == 0.85
        assert prediction.created_by == "test_user"

    @pytest.mark.asyncio
    async def test_get_prediction_by_id(self, db_session):
        """Test getting prediction by ID."""
        repo = PredictionRepository(db_session)

        # Create prediction
        created = await repo.create(team_name="Find Me FC")

        # Get by ID
        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.team_name == "Find Me FC"

    @pytest.mark.asyncio
    async def test_get_recent_by_team(self, db_session):
        """Test getting recent predictions for a team."""
        repo = PredictionRepository(db_session)

        # Create multiple predictions for the same team
        for i in range(3):
            await repo.create(
                team_name="Consistent FC",
                formation="4-4-2",
                confidence=0.7 + (i * 0.1),
            )

        # Create prediction for different team
        await repo.create(team_name="Different FC")

        # Get recent predictions for specific team
        recent = await repo.get_recent_by_team("Consistent FC", limit=5)

        assert len(recent) == 3
        for prediction in recent:
            assert prediction.team_name == "Consistent FC"

        # Should be ordered by created_at descending
        assert abs(recent[0].confidence - 0.9) < 0.01  # Most recent
        assert abs(recent[-1].confidence - 0.7) < 0.01  # Oldest

    @pytest.mark.asyncio
    async def test_get_recent_predictions(self, db_session):
        """Test getting recent predictions across all teams."""
        repo = PredictionRepository(db_session)

        # Create predictions for multiple teams
        teams = ["Team A", "Team B", "Team C"]
        for team in teams:
            await repo.create(team_name=team)

        # Get recent predictions
        recent = await repo.get_recent_predictions(limit=5)

        assert len(recent) == 3
        team_names = [p.team_name for p in recent]
        assert "Team A" in team_names
        assert "Team B" in team_names
        assert "Team C" in team_names
