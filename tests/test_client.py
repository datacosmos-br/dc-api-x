"""
Tests for the ApiClient module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import responses

from dc_api_x.client import ApiClient
from dc_api_x.exceptions import (
    ApiConnectionError,
    ApiTimeoutError,
    AuthenticationError,
    ConfigurationError,
    ResponseError,
)


class TestApiClient:
    """Test suite for the ApiClient class."""

    @pytest.fixture
    def client(self):
        """Create a test API client."""
        return ApiClient(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

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
        """Test GET request with 404 response."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users/999",
            json={"error": "User not found"},
            status=404,
        )

        # Make request and expect error
        with pytest.raises(ResponseError) as excinfo:
            client.get("users/999")

        # Verify error
        assert excinfo.value.status_code == 404
        assert "User not found" in str(excinfo.value)

    @responses.activate
    def test_get_server_error(self, client):
        """Test GET request with server error."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"error": "Internal server error"},
            status=500,
        )

        # Make request and expect error
        with pytest.raises(ResponseError) as excinfo:
            client.get("users")

        # Verify error
        assert excinfo.value.status_code == 500
        assert "Internal server error" in str(excinfo.value)

    @responses.activate
    def test_get_connection_error(self, client):
        """Test GET request with connection error."""
        # Mock response to raise connection error
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            body=ApiConnectionError("Connection refused"),
        )

        # Make request and expect error
        with pytest.raises(ConnectionError) as excinfo:
            client.get("users")

        # Verify error
        assert "Failed to connect to API" in str(excinfo.value)

    @responses.activate
    def test_get_timeout(self, client):
        """Test GET request with timeout."""
        # Mock response to time out
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            body=ApiTimeoutError("Request timed out"),
        )

        # Make request and expect error
        with pytest.raises(ConnectionError) as excinfo:
            client.get("users")

        # Verify error
        assert "Request timed out" in str(excinfo.value)

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

    @patch("dc_api_x.client.Config")
    def test_from_profile(self, mock_config):
        """Test creating client from profile."""
        # Mock Config.from_profile
        mock_config.from_profile.return_value = MagicMock(
            url="https://api.profile.com",
            username="profileuser",
            password="profilepass",
            timeout=30,
            verify_ssl=True,
            max_retries=5,
            retry_backoff=1.0,
            debug=False,
        )

        # Create client from profile
        client = ApiClient.from_profile("dev")

        # Verify client configuration
        assert client.url == "https://api.profile.com"
        assert client.username == "profileuser"
        assert client.password == "profilepass"
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client.max_retries == 5
        assert client.retry_backoff == 1.0
        assert client.debug is False

        # Verify Config.from_profile was called with the right profile
        mock_config.from_profile.assert_called_once_with("dev")

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
        """Test failed connection test."""
        # Mock response to fail
        responses.add(
            responses.GET,
            "https://api.example.com/ping",
            json={"error": "Service unavailable"},
            status=503,
        )

        # Test connection
        success, message = client.test_connection()

        # Verify result
        assert success is False
        assert "Connection failed" in message
