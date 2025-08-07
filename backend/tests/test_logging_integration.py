"""Tests for logging integration with main application."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


class TestLoggingIntegration:
    """Test logging integration with main application."""

    @pytest.fixture
    def client(self):
        """Create test client with main app."""
        return TestClient(app)

    def test_health_endpoint_has_request_id(self, client):
        """Test that health endpoint includes request ID."""
        response = client.get("/health")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    def test_root_endpoint_has_request_id(self, client):
        """Test that root endpoint includes request ID."""
        response = client.get("/")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "name" in response.json()

    def test_custom_request_id_preserved_in_main_app(self, client):
        """Test that custom request IDs are preserved in main app."""
        custom_id = "integration-test-123"
        response = client.get("/health", headers={"X-Request-ID": custom_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    def test_nonexistent_endpoint_includes_request_id(self, client):
        """Test that 404 responses still include request ID."""
        response = client.get("/nonexistent")

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
