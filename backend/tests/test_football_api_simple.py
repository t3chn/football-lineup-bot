"""Simplified tests for Football API client."""

from unittest.mock import patch

import pytest

from backend.app.adapters.football_api import FootballAPIClient


def test_client_initialization():
    """Test client initialization with settings."""
    with patch("backend.app.adapters.football_api.get_settings") as mock_settings:
        mock_settings.return_value.api_football_base_url = "https://api.example.com"
        mock_settings.return_value.api_football_key = "test_key"

        client = FootballAPIClient()
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test_key"
        assert client._client is None


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client works as async context manager."""
    with patch("backend.app.adapters.football_api.get_settings") as mock_settings:
        mock_settings.return_value.api_football_base_url = "https://api.example.com"
        mock_settings.return_value.api_football_key = "test_key"

        client = FootballAPIClient()
        assert client._client is None

        async with client:
            assert client._client is not None

        # After exiting context, client should be closed
        assert client._client is None


def test_headers_generation():
    """Test API headers are properly generated."""
    with patch("backend.app.adapters.football_api.get_settings") as mock_settings:
        mock_settings.return_value.api_football_base_url = "https://api.example.com/v3"
        mock_settings.return_value.api_football_key = "test_key"

        client = FootballAPIClient()
        headers = client._get_headers()

        assert headers["X-RapidAPI-Key"] == "test_key"
        assert "X-RapidAPI-Host" in headers


def test_client_property_raises_without_context():
    """Test client property raises error when not in context."""
    with patch("backend.app.adapters.football_api.get_settings") as mock_settings:
        mock_settings.return_value.api_football_base_url = "https://api.example.com"
        mock_settings.return_value.api_football_key = "test_key"

        client = FootballAPIClient()

        with pytest.raises(RuntimeError, match="Client not initialized"):
            _ = client.client
