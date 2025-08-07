"""Tests for API authentication."""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from backend.app.auth.api_key import generate_api_key, verify_api_key
from backend.app.auth.dependencies import require_auth


class TestAPIKeyAuthentication:
    """Test API key authentication."""

    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = generate_api_key()

        assert isinstance(api_key, str)
        assert len(api_key) > 40  # URL-safe base64 should be longer

        # Generate another and ensure they're different
        api_key2 = generate_api_key()
        assert api_key != api_key2

    @patch("backend.app.auth.api_key.get_settings")
    def test_verify_api_key_success(self, mock_get_settings):
        """Test successful API key verification."""
        # Setup
        mock_settings = Mock()
        mock_settings.api_key = "test-api-key"
        mock_get_settings.return_value = mock_settings

        # Test
        result = verify_api_key("test-api-key")

        # Assert
        assert result == "test-api-key"

    @patch("backend.app.auth.api_key.get_settings")
    def test_verify_api_key_missing(self, mock_get_settings):
        """Test API key verification with missing key."""
        # Setup
        mock_settings = Mock()
        mock_settings.api_key = "test-api-key"
        mock_get_settings.return_value = mock_settings

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "API key required"

    @patch("backend.app.auth.api_key.get_settings")
    def test_verify_api_key_empty(self, mock_get_settings):
        """Test API key verification with empty key."""
        # Setup
        mock_settings = Mock()
        mock_settings.api_key = "test-api-key"
        mock_get_settings.return_value = mock_settings

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key("")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "API key required"

    @patch("backend.app.auth.api_key.get_settings")
    def test_verify_api_key_invalid(self, mock_get_settings):
        """Test API key verification with invalid key."""
        # Setup
        mock_settings = Mock()
        mock_settings.api_key = "correct-api-key"
        mock_get_settings.return_value = mock_settings

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key("wrong-api-key")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch("backend.app.auth.api_key.get_settings")
    def test_verify_api_key_not_configured(self, mock_get_settings):
        """Test API key verification when not configured."""
        # Setup
        mock_settings = Mock()
        mock_settings.api_key = ""
        mock_get_settings.return_value = mock_settings

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key("any-key")

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Authentication not configured"

    @patch("backend.app.auth.dependencies.verify_api_key")
    def test_require_auth_dependency_success(self, mock_verify):
        """Test require_auth dependency with valid key."""
        # Setup
        mock_verify.return_value = "valid-key"

        # Test
        result = require_auth("valid-key")

        # Assert
        assert result == "valid-key"
        mock_verify.assert_called_once_with("valid-key")

    @patch("backend.app.auth.dependencies.verify_api_key")
    def test_require_auth_dependency_invalid(self, mock_verify):
        """Test require_auth dependency with invalid key."""
        # Setup
        mock_verify.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            require_auth("invalid-key")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"


class TestTimingAttackPrevention:
    """Test timing attack prevention."""

    @patch("backend.app.auth.api_key.get_settings")
    def test_constant_time_comparison(self, mock_get_settings):
        """Test that comparison uses constant time to prevent timing attacks."""
        import contextlib
        import time

        # Setup
        mock_settings = Mock()
        correct_key = "a" * 32  # 32 character key
        mock_settings.api_key = correct_key
        mock_get_settings.return_value = mock_settings

        # Test with wrong key of same length (should take similar time)
        wrong_key = "b" * 32

        start_time = time.time()
        with contextlib.suppress(HTTPException):
            verify_api_key(wrong_key)
        wrong_key_time = time.time() - start_time

        # Test with wrong key of different length (should take similar time)
        short_wrong_key = "b"

        start_time = time.time()
        with contextlib.suppress(HTTPException):
            verify_api_key(short_wrong_key)
        short_key_time = time.time() - start_time

        # Both should be rejected and take similar time (within reasonable tolerance)
        # Note: This is a basic test - in practice timing attacks are more sophisticated
        time_difference = abs(wrong_key_time - short_key_time)
        assert time_difference < 0.1  # Allow 100ms tolerance for test environment
