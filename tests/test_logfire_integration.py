"""
Tests for Logfire integration.

This module demonstrates how to properly use Logfire in tests.
"""

import contextlib
import time

import pytest

from dc_api_x.client import ApiClient
from dc_api_x.utils.validation import validate_email, validate_url
from tests import (
    LOGFIRE_AVAILABLE,
    context,
    error,
    info,
    requires_logfire,
    span,
    test_context,
    warning,
)

# Skip all tests in this module if Logfire is not available
pytestmark = pytest.mark.skipif(not LOGFIRE_AVAILABLE, reason="Logfire not available")


class TestLogfireCapture:
    """Test the Logfire capture functionality."""

    def test_logfire_capture_basic(self, logfire_testing) -> None:
        """Test basic log capture with Logfire."""
        # Log some messages
        info("Test message")
        warning("Warning message", important=True)
        error("Error message", code=500)

        # Verify logs were captured
        assert len(logfire_testing.logs) >= 3

        # Find specific logs using improved methods
        info_log = logfire_testing.find_log(message="Test message")
        warning_log = logfire_testing.find_log(message="Warning message")
        error_log = logfire_testing.find_log(message="Error message")

        # Assert log contents using attribute access
        assert info_log is not None
        assert info_log.level == "INFO"

        assert warning_log is not None
        assert warning_log.level == "WARNING"
        assert warning_log.important is True

        assert error_log is not None
        assert error_log.level == "ERROR"
        assert error_log.code == 500

    def test_validation_with_logfire(self, logfire_testing) -> None:
        """Test validation functions with Logfire logging."""
        # Test with valid values first (should not log warnings)
        valid_url = "https://example.com"
        valid_email = "user@example.com"

        is_valid_url, _ = validate_url(valid_url)
        is_valid_email, _ = validate_email(valid_email)

        assert is_valid_url is True
        assert is_valid_email is True

        # Test with invalid values (should log warnings)
        invalid_url = "invalid-url"
        invalid_email = "invalid-email"

        is_valid_url, _ = validate_url(invalid_url)
        is_valid_email, _ = validate_email(invalid_email)

        assert is_valid_url is False
        assert is_valid_email is False

        # Check that validation errors were logged using the improved methods
        url_error_log = logfire_testing.find_log(field="url", value=invalid_url)
        email_error_log = logfire_testing.find_log(field="email", value=invalid_email)

        assert url_error_log is not None, "URL validation error not logged"
        assert email_error_log is not None, "Email validation error not logged"

        # Assert log level using attribute access
        assert url_error_log.level == "WARNING"
        assert email_error_log.level == "WARNING"


class TestLogfireWithApiClient:
    """Test Logfire integration with ApiClient."""

    @pytest.fixture
    def client(self) -> ApiClient:
        """Create a test API client."""
        return ApiClient(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            debug=True,
        )

    @pytest.mark.xfail(reason="This test is expected to fail due to connection error")
    def test_api_request_logging(self, client: ApiClient, logfire_testing) -> None:
        """Test API request logging with Logfire.

        Note: This test is expected to fail since we're not mocking HTTP requests,
        but it demonstrates how Logfire captures API client operations.
        """
        # Use contextlib.suppress to handle the expected exception
        with contextlib.suppress(Exception):
            # Attempt to make a request (will fail)
            client.get("test")

        # Find logs related to the API request using the improved method
        request_logs = logfire_testing.find_logs(
            url=lambda url: "api.example.com/test" in str(url),
        )

        # Assert that we have request logs
        assert len(request_logs) > 0, "No API request logs found"

        # Should have at least one error log
        error_logs = logfire_testing.find_logs(level="ERROR")

        assert len(error_logs) > 0, "No error logs for failed request"


@requires_logfire
def test_log_structured_data(logfire_testing) -> None:
    """Test logging structured data with Logfire."""
    # Create some structured data
    user_data = {
        "id": 123,
        "name": "Test User",
        "email": "test@example.com",
        "roles": ["admin", "user"],
        "active": True,
    }

    # Log with structured data
    info(
        "User data processed",
        user=user_data,
        operation="read",
        timestamp=1234567890,
    )

    # Find our log entry using improved method
    log_entry = logfire_testing.find_log(message="User data processed")

    # Assert log entry contents using attribute access
    assert log_entry is not None
    assert log_entry.level == "INFO"
    assert log_entry.operation == "read"
    assert log_entry.timestamp == 1234567890

    # Check that user data is properly structured
    assert hasattr(log_entry, "user")
    assert log_entry.user["id"] == 123
    assert log_entry.user["name"] == "Test User"
    assert log_entry.user["email"] == "test@example.com"
    assert "admin" in log_entry.user["roles"]
    assert log_entry.user["active"] is True


@requires_logfire
def test_context_and_span(logfire_testing) -> None:
    """Test using context and span from our test utilities."""
    # Use context manager
    with context(operation="test_operation", component="test_component"):
        info("Log within context")

        # Use span
        with span("test_span"):
            info("Log within span")
            # Add some delay to measure
            time.sleep(0.01)

    # Check that context values were added to logs using improved methods
    context_log = logfire_testing.find_log(
        message="Log within context",
        operation="test_operation",
        component="test_component",
    )

    assert context_log is not None, "Context values not added to logs"

    # Check that span was created using improved methods
    span_log = logfire_testing.find_log(span_name="test_span")

    assert span_log is not None, "Span not created correctly"
    assert span_log.duration_ms > 0, "Span duration not recorded"


@requires_logfire
def test_test_context_helper(logfire_testing) -> None:
    """Test the test_context helper function."""
    # Use the test_context helper
    with test_context(custom_field="custom_value"):
        info("Log with test context")

    # Find the log
    log = logfire_testing.find_log(message="Log with test context")

    # Verify test context was applied
    assert log is not None
    assert log.test is True  # test_context automatically adds test=True
    assert log.custom_field == "custom_value"

    # Verify test metadata was added
    assert hasattr(log, "test_name")
    assert hasattr(log, "test_module")
    assert "test_test_context_helper" in log.test_name


@requires_logfire(strict=False)
def test_non_strict_logfire(logfire_testing) -> None:
    """Test the non-strict logfire decorator.

    This test will run even if Logfire is not available.
    """
    info("This test runs with or without Logfire")

    if LOGFIRE_AVAILABLE:
        log = logfire_testing.find_log(message="This test runs with or without Logfire")
        assert log is not None
    else:
        # With strict=False, this test would run but logfire_testing would be None
        assert logfire_testing is None
