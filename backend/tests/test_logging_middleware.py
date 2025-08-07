"""Tests for logging middleware."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.app.middleware.logging import LoggingMiddleware


@pytest.fixture
def test_app():
    """Create test FastAPI app with logging middleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/error")
    async def error_endpoint():
        raise HTTPException(status_code=400, detail="Test error")

    @app.get("/exception")
    async def exception_endpoint():
        raise ValueError("Test exception")

    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    def test_successful_request_adds_request_id(self, client):
        """Test that successful requests get request ID in response headers."""
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_custom_request_id_preserved(self, client):
        """Test that custom request ID from headers is preserved."""
        custom_request_id = "test-request-123"
        response = client.get("/test", headers={"X-Request-ID": custom_request_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_request_id

    def test_http_exception_includes_request_id(self, client):
        """Test that HTTP exceptions still include request ID."""
        response = client.get("/error")

        assert response.status_code == 400
        assert "X-Request-ID" in response.headers

    def test_server_exception_propagates(self, client):
        """Test that server exceptions are properly propagated."""
        with pytest.raises(ValueError, match="Test exception"):
            client.get("/exception")

    def test_client_ip_extraction(self, client):
        """Test that client IP is properly extracted from headers."""
        # Test X-Forwarded-For header
        response = client.get("/test", headers={"X-Forwarded-For": "192.168.1.100, 10.0.0.1"})
        assert response.status_code == 200

        # Test X-Real-IP header
        response = client.get("/test", headers={"X-Real-IP": "192.168.1.200"})
        assert response.status_code == 200

    def test_multiple_requests_different_ids(self, client):
        """Test that multiple requests get different request IDs."""
        response1 = client.get("/test")
        response2 = client.get("/test")

        assert response1.status_code == 200
        assert response2.status_code == 200

        request_id_1 = response1.headers["X-Request-ID"]
        request_id_2 = response2.headers["X-Request-ID"]

        assert request_id_1 != request_id_2
