"""Integration test fixtures."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app.database import get_db
from backend.app.main import app
from backend.app.models.database import Base
from backend.app.services.memory_cache import InMemoryCacheService
from backend.app.settings import get_settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()


@pytest.fixture
def override_get_db(test_db: AsyncSession):
    """Override database dependency."""

    def _override_get_db():
        yield test_db

    return _override_get_db


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_client = Mock(spec=redis.Redis)

    # Mock async methods
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.exists = AsyncMock(return_value=0)
    mock_client.expire = AsyncMock(return_value=True)
    mock_client.close = AsyncMock()

    return mock_client


@pytest.fixture
def mock_cache_service(_mock_redis):
    """Mock cache service using memory cache."""
    return InMemoryCacheService()


@pytest.fixture
def mock_football_api():
    """Mock football API responses."""
    mock = Mock()
    mock.get_team_stats = AsyncMock(
        return_value={
            "team_id": 1,
            "name": "Arsenal",
            "current_form": "WWDLW",
            "recent_lineup": {
                "formation": "4-3-3",
                "players": [
                    {"name": "Aaron Ramsdale", "position": "GK"},
                    {"name": "Ben White", "position": "RB"},
                    {"name": "William Saliba", "position": "CB"},
                    {"name": "Gabriel Magalhaes", "position": "CB"},
                    {"name": "Kieran Tierney", "position": "LB"},
                    {"name": "Thomas Partey", "position": "CDM"},
                    {"name": "Granit Xhaka", "position": "CM"},
                    {"name": "Martin Odegaard", "position": "CAM"},
                    {"name": "Bukayo Saka", "position": "RW"},
                    {"name": "Gabriel Jesus", "position": "ST"},
                    {"name": "Gabriel Martinelli", "position": "LW"},
                ],
            },
        }
    )
    return mock


@pytest.fixture
async def async_client(override_get_db, _test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(override_get_db, _test_db) -> TestClient:
    """Create synchronous HTTP client for testing."""
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_settings():
    """Test application settings."""
    settings = get_settings()

    # Override for testing
    settings.api_key = "test-api-key-12345"
    settings.telegram_bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    settings.webhook_secret = "test-secret-token"
    settings.redis_url = "redis://localhost:6379/15"  # Use test DB
    settings.database_url = TEST_DATABASE_URL

    return settings


@pytest.fixture
def telegram_webhook_data():
    """Sample Telegram webhook data."""
    return {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 987654321,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "language_code": "en",
            },
            "chat": {
                "id": 987654321,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private",
            },
            "date": 1640995200,
            "text": "/predict Arsenal",
            "entities": [{"offset": 0, "length": 8, "type": "bot_command"}],
        },
    }
