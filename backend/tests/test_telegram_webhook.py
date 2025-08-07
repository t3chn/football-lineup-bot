"""Tests for Telegram webhook endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_webhook_endpoint(client):
    """Test webhook endpoint with valid update."""
    update_data = {
        "update_id": 123456,
        "message": {
            "message_id": 1,
            "date": 1234567890,
            "chat": {"id": 123, "type": "private"},
            "from": {"id": 456, "is_bot": False, "first_name": "Test"},
            "text": "/start",
        },
    }

    with (
        patch("backend.app.routers.telegram.get_bot") as mock_get_bot,
        patch("backend.app.routers.telegram.get_dispatcher") as mock_get_dp,
    ):
        mock_bot = MagicMock()
        mock_dp = MagicMock()
        mock_dp.feed_update = AsyncMock()

        mock_get_bot.return_value = mock_bot
        mock_get_dp.return_value = mock_dp

        response = client.post("/telegram/webhook", json=update_data)

        assert response.status_code == 200
        assert response.json() == {"ok": True}
        mock_dp.feed_update.assert_called_once()


def test_webhook_endpoint_invalid_data(client):
    """Test webhook endpoint with invalid update data."""
    invalid_data = {"invalid": "data"}

    with (
        patch("backend.app.routers.telegram.get_bot") as mock_get_bot,
        patch("backend.app.routers.telegram.get_dispatcher") as mock_get_dp,
    ):
        mock_get_bot.return_value = MagicMock()
        mock_get_dp.return_value = MagicMock()

        response = client.post("/telegram/webhook", json=invalid_data)

        assert response.status_code == 500
        assert "Failed to process update" in response.json()["detail"]


def test_set_webhook_success(client):
    """Test setting webhook successfully."""
    with (
        patch("backend.app.routers.telegram.get_settings") as mock_settings,
        patch("backend.app.routers.telegram.get_bot") as mock_get_bot,
    ):
        mock_settings.return_value.webhook_url = "https://example.com"
        mock_settings.return_value.webhook_secret = "secret123"

        mock_bot = MagicMock()
        mock_bot.set_webhook = AsyncMock()

        mock_webhook_info = MagicMock()
        mock_webhook_info.url = "https://example.com/telegram/webhook"
        mock_webhook_info.pending_update_count = 0
        mock_webhook_info.allowed_updates = ["message", "callback_query"]

        mock_bot.get_webhook_info = AsyncMock(return_value=mock_webhook_info)
        mock_get_bot.return_value = mock_bot

        response = client.post("/telegram/set-webhook")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["webhook_url"] == "https://example.com/telegram/webhook"
        assert data["pending_update_count"] == 0


def test_set_webhook_no_url(client):
    """Test setting webhook without URL configured."""
    with patch("backend.app.routers.telegram.get_settings") as mock_settings:
        mock_settings.return_value.webhook_url = ""

        response = client.post("/telegram/set-webhook")

        assert response.status_code == 400
        assert "WEBHOOK_URL not configured" in response.json()["detail"]


def test_delete_webhook(client):
    """Test deleting webhook."""
    with patch("backend.app.routers.telegram.get_bot") as mock_get_bot:
        mock_bot = MagicMock()
        mock_bot.delete_webhook = AsyncMock()
        mock_get_bot.return_value = mock_bot

        response = client.delete("/telegram/webhook")

        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert "Webhook deleted successfully" in response.json()["message"]
        mock_bot.delete_webhook.assert_called_once_with(drop_pending_updates=True)


def test_get_webhook_info(client):
    """Test getting webhook info."""
    with patch("backend.app.routers.telegram.get_bot") as mock_get_bot:
        mock_bot = MagicMock()

        mock_webhook_info = MagicMock()
        mock_webhook_info.url = "https://example.com/telegram/webhook"
        mock_webhook_info.has_custom_certificate = False
        mock_webhook_info.pending_update_count = 5
        mock_webhook_info.ip_address = "1.2.3.4"
        mock_webhook_info.last_error_date = None
        mock_webhook_info.last_error_message = None
        mock_webhook_info.last_synchronization_error_date = None
        mock_webhook_info.max_connections = 40
        mock_webhook_info.allowed_updates = ["message", "callback_query"]

        mock_bot.get_webhook_info = AsyncMock(return_value=mock_webhook_info)
        mock_get_bot.return_value = mock_bot

        response = client.get("/telegram/webhook-info")

        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://example.com/telegram/webhook"
        assert data["pending_update_count"] == 5
        assert data["ip_address"] == "1.2.3.4"
        assert data["allowed_updates"] == ["message", "callback_query"]
