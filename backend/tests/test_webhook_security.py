"""Tests for webhook security."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.security.webhook import verify_telegram_webhook_signature


class TestWebhookSecurity:
    """Test webhook security functions."""

    def test_verify_telegram_webhook_signature_valid(self):
        """Test valid webhook signature verification."""
        secret = "test_secret_token"
        signature = "test_secret_token"
        body = b'{"test": "data"}'

        assert verify_telegram_webhook_signature(secret, signature, body) is True

    def test_verify_telegram_webhook_signature_invalid(self):
        """Test invalid webhook signature verification."""
        secret = "test_secret_token"
        signature = "wrong_token"
        body = b'{"test": "data"}'

        assert verify_telegram_webhook_signature(secret, signature, body) is False

    def test_verify_telegram_webhook_signature_missing(self):
        """Test webhook signature verification with missing signature."""
        secret = "test_secret_token"
        signature = None
        body = b'{"test": "data"}'

        assert verify_telegram_webhook_signature(secret, signature, body) is False

    def test_verify_telegram_webhook_signature_empty_secret(self):
        """Test webhook signature verification with empty secret."""
        secret = ""
        signature = "test_signature"
        body = b'{"test": "data"}'

        assert verify_telegram_webhook_signature(secret, signature, body) is False


@pytest.mark.asyncio
class TestWebhookEndpoint:
    """Test webhook endpoint with security."""

    async def test_webhook_with_valid_signature(self):
        """Test webhook endpoint with valid signature."""
        client = TestClient(app)

        webhook_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
            },
        }

        with (
            patch("backend.app.routers.telegram.get_settings") as mock_settings,
            patch("backend.app.routers.telegram.get_bot"),
            patch("backend.app.routers.telegram.get_dispatcher") as mock_dp,
        ):
            mock_settings.return_value.webhook_secret = "test_secret"
            mock_dp.return_value.feed_update = AsyncMock()

            response = client.post(
                "/telegram/webhook",
                json=webhook_data,
                headers={"X-Telegram-Bot-Api-Secret-Token": "test_secret"},
            )

            assert response.status_code == 200
            assert response.json() == {"ok": True}

    async def test_webhook_with_invalid_signature(self):
        """Test webhook endpoint with invalid signature."""
        client = TestClient(app)

        webhook_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
            },
        }

        with patch("backend.app.routers.telegram.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = "test_secret"

            response = client.post(
                "/telegram/webhook",
                json=webhook_data,
                headers={"X-Telegram-Bot-Api-Secret-Token": "wrong_secret"},
            )

            assert response.status_code == 403
            assert response.json()["detail"] == "Invalid signature"

    async def test_webhook_without_signature(self):
        """Test webhook endpoint without signature header."""
        client = TestClient(app)

        webhook_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
            },
        }

        with patch("backend.app.routers.telegram.get_settings") as mock_settings:
            mock_settings.return_value.webhook_secret = "test_secret"

            response = client.post("/telegram/webhook", json=webhook_data)

            assert response.status_code == 403
            assert response.json()["detail"] == "Invalid signature"
