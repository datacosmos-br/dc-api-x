"""
Tests for Logfire integration with ApiClient.

This module demonstrates how to properly use Logfire with ApiClient in tests.
"""

import pytest
import responses

from dc_api_x.client import ApiClient
from dc_api_x.utils.exceptions import ApiError, AuthenticationError
from tests import LOGFIRE_AVAILABLE, context

# Mark these tests to be skipped if Logfire is not available
pytestmark = pytest.mark.skipif(not LOGFIRE_AVAILABLE, reason="Logfire not available")


class TestApiClientLogfire:
    """Test ApiClient with Logfire integration."""

    @pytest.fixture
    def api_client(self) -> ApiClient:
        """Create an API client for testing."""
        return ApiClient(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=5,
            verify_ssl=False,
        )

    @responses.activate
    def test_api_request_logging(self, api_client: ApiClient, logfire_testing) -> None:
        """Test that API requests are properly logged with Logfire."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"data": [{"id": 1, "name": "John"}]},
            status=200,
        )

        # Use Logfire context for additional context
        with context(operation="list_users", component="api_client_test"):
            response = api_client.get("users")

        # Verify response
        assert response.success is True
        assert response.status_code == 200

        # Verify logs
        request_logs = [
            log
            for log in logfire_testing.logs
            if "https://api.example.com/users" in log.get("url", "")
        ]

        assert (
            len(request_logs) >= 2
        ), "Should have at least 2 logs for the request (start and complete)"

        # Check that context values were included
        context_logs = [
            log
            for log in request_logs
            if log.get("operation") == "list_users"
            and log.get("component") == "api_client_test"
        ]

        assert len(context_logs) > 0, "Context values were not included in logs"

        # Check for timing information
        timing_logs = [log for log in request_logs if "duration_ms" in log]

        assert len(timing_logs) > 0, "Request timing was not logged"

    @responses.activate
    def test_api_error_logging(self, api_client: ApiClient, logfire_testing) -> None:
        """Test that API errors are properly logged with Logfire."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/error",
            json={"error": "Server error"},
            status=500,
        )

        # Use Logfire span to track the error
        from tests import span

        with span("api_error_test"), pytest.raises(ApiError, match="Server error"):
            api_client.get("error")

        # Verify logs
        error_logs = [
            log
            for log in logfire_testing.logs
            if log["level"] == "ERROR"
            and "https://api.example.com/error" in log.get("url", "")
        ]

        assert len(error_logs) > 0, "Error was not logged"

        # Check for error details
        assert any(
            "error" in log and "status_code" in log and log["status_code"] == 500
            for log in error_logs
        ), "Error details were not properly logged"

    @responses.activate
    def test_api_auth_error_logging(
        self,
        api_client: ApiClient,
        logfire_testing,
    ) -> None:
        """Test that authentication errors are properly logged with Logfire."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/protected",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Use Logfire testing context
        with (
            context(user_id="testuser", access_level="standard"),
            pytest.raises(AuthenticationError, match="Unauthorized"),
        ):
            api_client.get("protected")

        # Verify logs
        auth_error_logs = [
            log
            for log in logfire_testing.logs
            if log["level"] == "ERROR" and log.get("status_code") == 401
        ]

        assert len(auth_error_logs) > 0, "Authentication error was not logged"

        # Check for auth context in logs
        assert any(
            log.get("user_id") == "testuser" and log.get("access_level") == "standard"
            for log in auth_error_logs
        ), "Authentication context was not included in logs"

    def test_request_body_logging_with_redaction(
        self,
        api_client: ApiClient,
        logfire_testing,
    ) -> None:
        """Test that request bodies are logged with sensitive data redacted."""
        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/login",
            json={"token": "fake-token"},
            status=200,
        )

        # Create payload with sensitive data
        sensitive_payload = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "abcd1234",
            "metadata": {"client": "test-client"},
        }

        # Make request with sensitive data
        with context(request_id="test-123"):
            api_client.post("login", json_data=sensitive_payload)

        # Verify logs
        request_logs = [
            log
            for log in logfire_testing.logs
            if "https://api.example.com/login" in log.get("url", "")
            and log.get("method") == "POST"
        ]

        assert len(request_logs) > 0, "Request was not logged"

        # Find logs containing request body
        body_logs = [log for log in request_logs if "request_body" in log]

        assert len(body_logs) > 0, "Request body was not logged"

        # Check that sensitive data was redacted
        for log in body_logs:
            if isinstance(log.get("request_body"), dict):
                body = log["request_body"]
                # Password should be redacted
                if "password" in body:
                    assert body["password"] != "secret123", "Password was not redacted"
                    assert (
                        body["password"] == "[REDACTED]"
                    ), "Password was not properly redacted"

                # API key should be redacted
                if "api_key" in body:
                    assert body["api_key"] != "abcd1234", "API key was not redacted"
                    assert (
                        body["api_key"] == "[REDACTED]"
                    ), "API key was not properly redacted"

                # Non-sensitive data should not be redacted
                if "metadata" in body:
                    assert (
                        body["metadata"]["client"] == "test-client"
                    ), "Non-sensitive data was redacted"
