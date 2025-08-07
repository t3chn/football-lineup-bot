"""Tests for main FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns correct data."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Football Lineup Bot API"
    assert data["status"] == "running"
    assert "version" in data


def test_cors_headers(client):
    """Test CORS headers are properly set."""
    response = client.get(
        "/",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
