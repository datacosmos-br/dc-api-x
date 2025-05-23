"""
Pytest configuration file.

This module contains pytest fixtures and configuration for the dc_api_x test suite.
When using Poetry with src layout and proper installation, no path manipulation is
needed.
"""

# No path manipulation needed - Poetry handles the src layout automatically
# Tests will use the installed package from the workspace .venv

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests
import responses

import dc_api_x as apix
from dc_api_x.exceptions import ApiConnectionError, ApiTimeoutError


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--mock-services",
        action="store_true",
        default=False,
        help="Enable mock services for testing",
    )


def pytest_configure(config):
    """Configure pytest based on command line options."""
    # Unset PYTHONPATH to avoid conflicts with system packages
    if "PYTHONPATH" in os.environ:
        print("Unsetting PYTHONPATH to avoid conflicts")
        os.environ.pop("PYTHONPATH")

    # Register marker for tests that require mock services
    config.addinivalue_line(
        "markers", "mock_services: mark test as requiring mock services"
    )


@pytest.fixture(scope="session")
def mock_services_enabled(request):
    """Check if mock services are enabled."""
    return request.config.getoption("--mock-services")


@pytest.fixture
def mock_response():
    """Create a mock HTTP response for testing."""
    response = MagicMock()
    response.status_code = 200
    response.text = '{"success": true, "data": {"id": 1}}'
    response.json.return_value = {"success": True, "data": {"id": 1}}
    return response


@pytest.fixture
def mock_error_response():
    """Create a mock error HTTP response for testing."""
    response = MagicMock()
    response.status_code = 400
    response.text = '{"error": "Bad Request", "code": "ERR_001"}'
    response.json.return_value = {"error": "Bad Request", "code": "ERR_001"}
    response.raise_for_status.side_effect = Exception("HTTP Error")
    return response


@pytest.fixture
def mock_http_service():
    """Create a mock HTTP service for testing."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Setup common endpoints
        rsps.add(
            responses.GET,
            "https://api.example.com/ping",
            json={"status": "ok"},
            status=200,
        )

        # Success responses
        rsps.add(
            responses.GET,
            "https://api.example.com/users",
            json={"data": [{"id": 1, "name": "John"}]},
            status=200,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John"}},
            status=200,
        )
        rsps.add(
            responses.POST,
            "https://api.example.com/users",
            json={"data": {"id": 2, "name": "Jane"}},
            status=201,
        )
        rsps.add(
            responses.PUT,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John Updated"}},
            status=200,
        )
        rsps.add(
            responses.DELETE,
            "https://api.example.com/users/1",
            json={"success": True},
            status=204,
        )
        rsps.add(
            responses.PATCH,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John Patched"}},
            status=200,
        )

        # Error responses
        rsps.add(
            responses.GET,
            "https://api.example.com/users/999",
            json={"error": "User not found"},
            status=404,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/server-error",
            json={"error": "Internal Server Error"},
            status=500,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/unauthorized",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Connection errors
        rsps.add(
            responses.GET,
            "https://api.example.com/error",
            body=ApiConnectionError("Connection refused"),
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/timeout",
            body=ApiTimeoutError("Request timed out"),
        )

        yield rsps


@pytest.fixture
def mock_auth_provider():
    """Create a mock authentication provider for testing."""
    auth_provider = MagicMock(spec=apix.AuthProvider)
    auth_provider.authenticate.return_value = {"token": "mock-token"}
    auth_provider.get_auth_headers.return_value = {"Authorization": "Bearer mock-token"}
    auth_provider.username = "testuser"
    auth_provider.password = "testpass"
    return auth_provider


@pytest.fixture
def mock_database_adapter():
    """Create a mock database adapter for testing."""
    adapter = MagicMock(spec=apix.DatabaseAdapter)
    adapter.execute.return_value = [{"id": 1, "name": "Test Record"}]
    adapter.connect.return_value = True
    adapter.disconnect.return_value = True
    return adapter


@pytest.fixture
def mock_directory_adapter():
    """Create a mock directory adapter for testing."""
    adapter = MagicMock(spec=apix.DirectoryAdapter)
    adapter.search.return_value = [
        (
            "cn=user1,ou=users,dc=example,dc=com",
            {"cn": ["user1"], "mail": ["user1@example.com"]},
        ),
        (
            "cn=user2,ou=users,dc=example,dc=com",
            {"cn": ["user2"], "mail": ["user2@example.com"]},
        ),
    ]
    adapter.connect.return_value = True
    adapter.disconnect.return_value = True
    return adapter


@pytest.fixture
def mock_message_queue_adapter():
    """Create a mock message queue adapter for testing."""
    adapter = MagicMock(spec=apix.MessageQueueAdapter)
    adapter.publish.return_value = True
    adapter.connect.return_value = True
    adapter.disconnect.return_value = True
    return adapter


@pytest.fixture(autouse=True)
def mock_env_file(mock_services_enabled):
    """Mock environment file for testing."""
    if mock_services_enabled:
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "pydantic_settings.sources.providers.secrets.path_type_label",
                return_value="directory",
            ),
            patch("os.path.isdir", return_value=True),
        ):
            yield
    else:
        yield


@pytest.fixture(autouse=True)
def mock_secrets_dir(mock_services_enabled):
    """Mock secrets directory for testing."""
    if mock_services_enabled:
        with patch("pydantic_settings.sources.providers.secrets.SecretsSettingsSource.__call__", return_value={}), \
             patch("os.path.isdir", return_value=True), \
             patch("os.path.exists", return_value=True), \
             patch("pathlib.Path.exists", return_value=True):
            yield
    else:
        yield


"""
# Example fixture:
# import pytest
#
# @pytest.fixture
# def sample_client():
#     from dc_api_x.client import APIClient
#     return APIClient(base_url="https://api.example.com")
"""
