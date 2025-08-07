"""Tests for input validation."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.validators.common import TeamNameValidator, validate_team_name
from backend.app.validators.webhook import TelegramUser, WebhookUpdateValidator


class TestTeamNameValidation:
    """Test team name validation."""

    def test_valid_team_names(self):
        """Test valid team names."""
        valid_names = [
            "Arsenal",
            "Manchester United",
            "Real Madrid",
            "Bayern Munich",
            "Paris Saint-Germain",
            "F.C. Barcelona",
            "A.C. Milan",
            "Inter Milan",
        ]

        for name in valid_names:
            validator = TeamNameValidator(name=name)
            assert validator.name == name.strip()

    def test_invalid_team_names(self):
        """Test invalid team names."""
        invalid_names = [
            "",  # Empty
            "   ",  # Only spaces
            "A" * 101,  # Too long
            "Team123",  # Contains numbers
            "Team@Home",  # Contains special characters
            "Team;DROP TABLE",  # SQL injection attempt
            "Team' OR '1'='1",  # SQL injection
            "Team<script>",  # Script injection
            "Team--comment",  # SQL comment
            "Team/*comment*/",  # SQL comment
        ]

        for name in invalid_names:
            with pytest.raises(ValueError):
                TeamNameValidator(name=name)

    def test_validate_team_name_function(self):
        """Test validate_team_name function."""
        # Valid name
        result = validate_team_name("Arsenal")
        assert result == "Arsenal"

        # Invalid name raises HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_team_name("Team123")
        assert exc_info.value.status_code == 400


class TestWebhookValidation:
    """Test webhook update validation."""

    def test_valid_webhook_update(self):
        """Test valid webhook update."""
        valid_update = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
            },
        }

        validator = WebhookUpdateValidator(**valid_update)
        assert validator.update_id == 123456
        assert validator.message is not None
        assert validator.message.text == "/start"

    def test_invalid_update_id(self):
        """Test invalid update ID."""
        invalid_updates = [
            {"update_id": 0, "message": {"message_id": 1}},  # Zero ID
            {"update_id": -1, "message": {"message_id": 1}},  # Negative ID
            {"update_id": 2**31, "message": {"message_id": 1}},  # Too large
        ]

        for update in invalid_updates:
            with pytest.raises(ValueError):
                WebhookUpdateValidator(**update)

    def test_invalid_chat_type(self):
        """Test invalid chat type."""
        invalid_update = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {
                    "id": 12345,
                    "type": "invalid_type",  # Invalid type
                },
                "text": "/start",
            },
        }

        with pytest.raises(ValueError):
            WebhookUpdateValidator(**invalid_update)

    def test_empty_update(self):
        """Test empty update without any update type."""
        invalid_update = {
            "update_id": 123456
            # No message, callback_query, etc.
        }

        with pytest.raises(ValueError) as exc_info:
            WebhookUpdateValidator(**invalid_update)
        assert "must contain at least one update type" in str(exc_info.value)

    def test_telegram_user_validation(self):
        """Test Telegram user validation."""
        # Valid user
        valid_user = TelegramUser(id=12345, is_bot=False, first_name="John", username="johndoe")
        assert valid_user.id == 12345

        # Invalid user ID
        with pytest.raises(ValueError):
            TelegramUser(
                id=-1,  # Negative ID
                is_bot=False,
                first_name="John",
            )

        # Invalid username
        with pytest.raises(ValueError):
            TelegramUser(
                id=12345,
                is_bot=False,
                first_name="John",
                username="john@doe",  # Invalid character
            )


class TestAPIEndpointValidation:
    """Test API endpoint validation."""

    def test_predict_endpoint_valid_team(self):
        """Test predict endpoint with valid team name."""
        client = TestClient(app)
        response = client.get("/predict/Arsenal")
        # Should not return 400 (validation error)
        assert response.status_code != 400

    def test_predict_endpoint_invalid_team(self):
        """Test predict endpoint with invalid team name."""
        client = TestClient(app)

        invalid_teams = [
            "Team123",  # Contains numbers
            "Team@Home",  # Contains special characters
            "Team;DROP",  # SQL injection attempt
        ]

        for team in invalid_teams:
            response = client.get(f"/predict/{team}")
            assert response.status_code == 422  # Validation error

    def test_webhook_endpoint_validation(self):
        """Test webhook endpoint validation."""
        client = TestClient(app)

        # Invalid webhook data
        invalid_data = {
            "update_id": -1,  # Invalid ID
            "message": {"message_id": 1, "text": "test"},
        }

        response = client.post(
            "/telegram/webhook",
            json=invalid_data,
            headers={"X-Telegram-Bot-Api-Secret-Token": "test_secret"},
        )

        # Should fail validation even with correct signature
        assert response.status_code in [400, 403]
