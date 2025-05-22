"""
Pytest configuration file.

This module contains pytest fixtures and configuration for the dc_api_x test suite.
When using Poetry with src layout and proper installation, no path manipulation is
needed.
"""

# No path manipulation needed - Poetry handles the src layout automatically
# Tests will use the installed package from the workspace .venv

from unittest.mock import MagicMock

# Place shared fixtures below as needed
import pytest


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


"""
# Example fixture:
# import pytest
#
# @pytest.fixture
# def sample_client():
#     from dc_api_x.client import APIClient
#     return APIClient(base_url="https://api.example.com")
"""
