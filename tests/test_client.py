"""
Tests for the ApiClient module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import responses
from _pytest.fixtures import SubRequest

from dc_api_x.client import ApiClient
from dc_api_x.utils import exceptions
from dc_api_x.utils.exceptions import (
    AuthenticationError,
    ConfigurationError,
    RequestFailedError,
)
from tests import requires_logfire, test_context


class TestApiClient:
    """Test suite for the ApiClient class."""

    @pytest.fixture
    def client(
        self,
        request: SubRequest,
        mock_http_service: responses.RequestsMock,
    ) -> ApiClient:
        """Create a test API client."""
        # Create test client
        client = ApiClient(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=30,
            verify_ssl=False,
        )

        # Use mock auth provider when mock_services is enabled
        if request.config.getoption("--mock-services", default=False):
            from dc_api_x.ext.auth.basic import BasicAuthProvider

            mock_auth = BasicAuthProvider("testuser", "testpass")
            client.auth_provider = mock_auth

        return client

    def test_init_with_missing_url(self) -> None:
        """Test initialization with missing URL."""
        with pytest.raises(ConfigurationError, match="API base URL is required"):
            ApiClient(url=None, username="testuser", password="testpass")

    def test_init_with_missing_username(self) -> None:
        """Test initialization with missing username."""
        with pytest.raises(ConfigurationError, match="API username is required"):
            ApiClient(url="https://api.example.com", username=None, password="testpass")

    def test_init_with_missing_password(self) -> None:
        """Test initialization with missing password."""
        with pytest.raises(ConfigurationError, match="API password is required"):
            ApiClient(url="https://api.example.com", username="testuser", password=None)

    def test_build_url(self, client: ApiClient) -> None:
        """Test URL building."""
        # Test with normal endpoint
        url = client._build_url("users")
        assert url == "https://api.example.com/users"

        # Test with leading slash
        url = client._build_url("/users")
        assert url == "https://api.example.com/users"

        # Test with nested path
        url = client._build_url("users/123/orders")
        assert url == "https://api.example.com/users/123/orders"

    @responses.activate
    @requires_logfire
    def test_get_success(self, client: ApiClient, logfire_testing) -> None:
        """Test successful GET request."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"data": [{"id": 1, "name": "John"}]},
            status=200,
        )

        # Log test context
        with test_context(operation="get_users", client_test=True):
            # Make request
            response = client.get("users")

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"data": [{"id": 1, "name": "John"}]}
        assert response.error is None

        # Verify logs
        request_log = logfire_testing.find_log(
            url="https://api.example.com/users",
            method="GET",
        )

        assert request_log is not None, "No request log found"

        # Should find debug logs for the request
        debug_logs = logfire_testing.find_logs(level="DEBUG")
        assert len(debug_logs) > 0, "No debug logs for request"

        # Verify test context was applied
        assert request_log.operation == "get_users"
        assert request_log.client_test is True

    @responses.activate
    def test_get_not_found(self, client: ApiClient) -> None:
        """Test GET request with not found error."""
        # Test request
        with pytest.raises(RequestFailedError):
            client.get("users/999")

    @responses.activate
    def test_get_server_error(self, client: ApiClient) -> None:
        """Test GET request with server error."""
        # Test request
        with pytest.raises(RequestFailedError):
            client.get("server-error")

    @responses.activate
    @requires_logfire
    def test_get_connection_error(self, client: ApiClient, logfire_testing) -> None:
        """Test GET request with connection error."""
        # Create test context
        with (
            test_context(operation="connection_error_test"),
            pytest.raises(exceptions.ApiConnectionError),
        ):
            # Test request - this will trigger an exception
            client.get("error")

        # Verify logs - should have error logs
        error_log = logfire_testing.find_log(
            level="ERROR",
            url="https://api.example.com/error",
        )

        assert error_log is not None, "No error log found for connection error"

        # Should contain error details
        assert hasattr(error_log, "error_type"), "Error log missing error_type field"

        # Verify context was applied
        assert error_log.operation == "connection_error_test"

    @responses.activate
    def test_get_timeout(self, client: ApiClient) -> None:
        """Test GET request with timeout error."""
        # Test request
        with pytest.raises(exceptions.ApiTimeoutError):
            client.get("timeout")

    @responses.activate
    @requires_logfire
    def test_post_success(self, client: ApiClient, logfire_testing) -> None:
        """Test successful POST request."""
        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 1, "name": "John"},
            status=201,
        )

        # Log test data
        user_data = {"name": "John"}

        with test_context(operation="create_user", data=user_data):
            # Make request
            response = client.post("users", json_data=user_data)

        # Verify response
        assert response.success is True
        assert response.status_code == 201
        assert response.data == {"id": 1, "name": "John"}
        assert response.error is None

        # Verify request payload
        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == json.dumps(user_data).encode()

        # Verify logs
        post_logs = logfire_testing.find_logs(
            url="https://api.example.com/users",
            method="POST",
        )

        assert len(post_logs) > 0, "No logs found for POST request"

        # Should have debug logs showing completion
        completion_log = logfire_testing.find_log(
            level="DEBUG",
            method="POST",
            message=lambda msg: "Completed POST request" in msg,
        )

        assert completion_log is not None, "No completion log for POST request"

        # Check for duration timing
        assert hasattr(completion_log, "duration_ms"), "Timing information missing"

        # Verify context was applied
        assert completion_log.operation == "create_user"
        assert completion_log.data == user_data

    @responses.activate
    def test_put_success(self, client: ApiClient) -> None:
        """Test successful PUT request."""
        # Mock response
        responses.add(
            responses.PUT,
            "https://api.example.com/users/1",
            json={"id": 1, "name": "John Updated"},
            status=200,
        )

        # Make request
        response = client.put("users/1", json_data={"name": "John Updated"})

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"id": 1, "name": "John Updated"}
        assert response.error is None

        # Verify request payload
        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.body
            == json.dumps({"name": "John Updated"}).encode()
        )

    @responses.activate
    def test_delete_success(self, client: ApiClient) -> None:
        """Test successful DELETE request."""
        # Mock response
        responses.add(
            responses.DELETE,
            "https://api.example.com/users/1",
            json={"status": "deleted"},
            status=200,
        )

        # Make request
        response = client.delete("users/1")

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"status": "deleted"}
        assert response.error is None

    @responses.activate
    def test_patch_success(self, client: ApiClient) -> None:
        """Test successful PATCH request."""
        # Mock response
        responses.add(
            responses.PATCH,
            "https://api.example.com/users/1",
            json={"id": 1, "name": "John Patched"},
            status=200,
        )

        # Make request
        response = client.patch("users/1", json_data={"name": "John Patched"})

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"id": 1, "name": "John Patched"}
        assert response.error is None

        # Verify request payload
        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.body
            == json.dumps({"name": "John Patched"}).encode()
        )

    @responses.activate
    @requires_logfire
    def test_authentication_error(self, client: ApiClient, logfire_testing) -> None:
        """Test authentication error."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Create test context
        with (
            test_context(operation="auth_error_test", user="testuser"),
            pytest.raises(AuthenticationError) as excinfo,
        ):
            # Make request and expect error
            client.get("users")

        # Verify error
        assert "Unauthorized" in str(excinfo.value)

        # Verify logs
        auth_error_log = logfire_testing.find_log(
            level="ERROR",
            error=lambda err: "Unauthorized" in str(err),
        )

        assert auth_error_log is not None, "No authentication error log found"

        # Verify context was applied
        assert auth_error_log.operation == "auth_error_test"
        assert auth_error_log.user == "testuser"

    @responses.activate
    def test_from_profile(self) -> None:
        """Test creating client from profile."""
        # Mock Config.from_profile
        with patch("dc_api_x.config.Config.from_profile") as mock_from_profile:
            # Setup mock return value
            mock_config = MagicMock()
            mock_config.url = "https://profile-api.example.com"
            mock_config.username = "profileuser"
            mock_config.password = "profilepass"
            mock_config.timeout = 45
            mock_config.verify_ssl = True
            mock_config.max_retries = 3
            mock_config.retry_backoff = 1.0
            mock_config.debug = False
            mock_from_profile.return_value = mock_config

            # Create client from profile
            client = ApiClient.from_profile("test")

            # Verify client configuration
            assert client.url == "https://profile-api.example.com"
            assert client.username == "profileuser"
            assert client.password == "profilepass"
            assert client.timeout == 45
            assert client.config.verify_ssl is True

    @responses.activate
    def test_test_connection_success(self, client: ApiClient) -> None:
        """Test successful connection test."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/ping",
            json={"status": "ok"},
            status=200,
        )

        # Test connection
        success, message = client.test_connection()

        # Verify result
        assert success is True
        assert "Connection successful" in message

    @responses.activate
    def test_test_connection_failure(self, client: ApiClient) -> None:
        """Test test_connection with failure."""
        # Mock the get method to raise an exception
        with (
            patch.object(
                client,
                "get",
                side_effect=exceptions.ApiConnectionError("Connection failed"),
            ),
        ):
            # Test connection
            success, message = client.test_connection()

            # Verify result
            assert success is False
            assert "Connection failed" in message
