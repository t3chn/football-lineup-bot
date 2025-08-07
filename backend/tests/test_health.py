"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient

from backend.app import __version__
from backend.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint returns correct status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert data["service"] == "Football Lineup Bot API"
    assert "timestamp" in data


def test_health_endpoint_timestamp_format(client):
    """Test health endpoint returns valid ISO timestamp."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    timestamp = data["timestamp"]
    assert "T" in timestamp
    assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp[-6:]
