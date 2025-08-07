"""Tests for performance logging utilities."""

from unittest.mock import Mock

import pytest
import structlog

from backend.app.utils.logging import PerformanceLogger, get_logger, log_performance


class TestPerformanceLogger:
    """Test performance logging functionality."""

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=structlog.BoundLogger)

    @pytest.fixture
    def mock_logger_with_bind(self, mock_logger):
        """Create mock logger that returns itself on bind."""
        mock_logger.bind.return_value = mock_logger
        mock_logger.debug = Mock()
        mock_logger.info = Mock()
        mock_logger.error = Mock()
        return mock_logger

    def test_successful_operation_logging(self, mock_logger_with_bind):
        """Test logging for successful operations."""
        with PerformanceLogger(mock_logger_with_bind, "test_operation", extra="data"):
            pass

        # Check that bind was called with correct arguments
        mock_logger_with_bind.bind.assert_called_once_with(operation="test_operation", extra="data")

        # Check that debug and info were called
        mock_logger_with_bind.debug.assert_called_once_with("Operation started")
        mock_logger_with_bind.info.assert_called_once()

        # Verify info call includes duration
        info_call = mock_logger_with_bind.info.call_args
        assert "Operation completed" in info_call[0]
        assert "duration_ms" in info_call[1]

    def test_failed_operation_logging(self, mock_logger_with_bind):
        """Test logging for failed operations."""
        test_error = ValueError("Test error")

        with (
            pytest.raises(ValueError),
            PerformanceLogger(mock_logger_with_bind, "failing_operation"),
        ):
            raise test_error

        # Check that error was logged
        mock_logger_with_bind.error.assert_called_once()
        error_call = mock_logger_with_bind.error.call_args

        assert "Operation failed" in error_call[0]
        assert "duration_ms" in error_call[1]
        assert error_call[1]["error"] == "Test error"
        assert error_call[1]["error_type"] == "ValueError"

    def test_log_performance_helper(self, mock_logger_with_bind):
        """Test log_performance helper function."""
        with log_performance(mock_logger_with_bind, "helper_test", param="value"):
            pass

        mock_logger_with_bind.bind.assert_called_once_with(operation="helper_test", param="value")

    def test_timing_accuracy(self, mock_logger_with_bind):
        """Test that timing is reasonably accurate."""
        import time

        with PerformanceLogger(mock_logger_with_bind, "timing_test"):
            time.sleep(0.01)  # Sleep for 10ms

        # Get the logged duration
        info_call = mock_logger_with_bind.info.call_args
        duration_ms = info_call[1]["duration_ms"]

        # Should be at least 10ms, but allow for some variance
        assert duration_ms >= 8.0  # Allow some tolerance
        assert duration_ms < 50.0  # Should not be too long

    def test_real_logger_integration(self):
        """Test with real structlog logger."""
        logger = get_logger(__name__)

        # This should not raise any exceptions
        with log_performance(logger, "integration_test", test_param="value"):
            pass

    def test_exception_details_captured(self, mock_logger_with_bind):
        """Test that exception details are properly captured."""

        class CustomError(Exception):
            pass

        with (
            pytest.raises(CustomError),
            PerformanceLogger(mock_logger_with_bind, "custom_error_test"),
        ):
            raise CustomError("Custom error message")

        error_call = mock_logger_with_bind.error.call_args
        assert error_call[1]["error"] == "Custom error message"
        assert error_call[1]["error_type"] == "CustomError"
