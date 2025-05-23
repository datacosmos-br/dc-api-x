"""
Tests for the ApiClient module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import responses

from dc_api_x.client import ApiClient
from dc_api_x import exceptions
from dc_api_x.exceptions import (
    ApiConnectionError,
    ApiError,
    ApiTimeoutError,
    AuthenticationError,
    ConfigurationError,
    ResponseError,
    RequestFailedError,
)


class TestApiClient:
    """Test suite for the ApiClient class."""

    @pytest.fixture
    def client(self, request, mock_http_service):
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
        if request.config.getoption("--mock-services", False):
            from dc_api_x.ext.auth.basic import BasicAuthProvider

            mock_auth = BasicAuthProvider("testuser", "testpass")
            client.auth_provider = mock_auth

        return client

    def test_init_with_missing_url(self):
        """Test initialization with missing URL."""
        with pytest.raises(ConfigurationError, match="API base URL is required"):
            ApiClient(url=None, username="testuser", password="testpass")

    def test_init_with_missing_username(self):
        """Test initialization with missing username."""
        with pytest.raises(ConfigurationError, match="API username is required"):
            ApiClient(url="https://api.example.com", username=None, password="testpass")

    def test_init_with_missing_password(self):
        """Test initialization with missing password."""
        with pytest.raises(ConfigurationError, match="API password is required"):
            ApiClient(url="https://api.example.com", username="testuser", password=None)

    def test_build_url(self, client):
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
    def test_get_success(self, client):
        """Test successful GET request."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"data": [{"id": 1, "name": "John"}]},
            status=200,
        )

        # Make request
        response = client.get("users")

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"data": [{"id": 1, "name": "John"}]}
        assert response.error is None

    @responses.activate
    def test_get_not_found(self, client):
        """Test GET request with not found error."""
        # Test request
        with pytest.raises(RequestFailedError):
            client.get("users/999")

    @responses.activate
    def test_get_server_error(self, client):
        """Test GET request with server error."""
        # Test request
        with pytest.raises(RequestFailedError):
            client.get("server-error")

    @responses.activate
    def test_get_connection_error(self, client):
        """Test GET request with connection error."""
        # Test request
        with pytest.raises(exceptions.ApiConnectionError):
            client.get("error")

    @responses.activate
    def test_get_timeout(self, client):
        """Test GET request with timeout error."""
        # Test request
        with pytest.raises(exceptions.ApiTimeoutError):
            client.get("timeout")

    @responses.activate
    def test_post_success(self, client):
        """Test successful POST request."""
        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 1, "name": "John"},
            status=201,
        )

        # Make request
        response = client.post("users", json_data={"name": "John"})

        # Verify response
        assert response.success is True
        assert response.status_code == 201
        assert response.data == {"id": 1, "name": "John"}
        assert response.error is None

        # Verify request payload
        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == json.dumps({"name": "John"}).encode()

    @responses.activate
    def test_put_success(self, client):
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
    def test_delete_success(self, client):
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
    def test_patch_success(self, client):
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
    def test_authentication_error(self, client):
        """Test authentication error."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Make request and expect error
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("users")

        # Verify error
        assert "Unauthorized" in str(excinfo.value)

    @responses.activate
    def test_from_profile(self):
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
    def test_test_connection_success(self, client):
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
    def test_test_connection_failure(self, client):
        """Test test_connection with failure."""
        # Mock the get method to raise an exception
        with patch.object(
            client,
            "get",
            side_effect=exceptions.ApiConnectionError("Connection failed"),
        ):
            # Test connection
            success, message = client.test_connection()

            # Verify result
            assert success is False
            assert "Connection failed" in message
