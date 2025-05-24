"""
Example integration tests for the dc-api-x API.

These tests validate the integration with external services.
"""

import os
from typing import Any
from unittest.mock import patch

import pytest
import responses

# Marcar todos os testes neste módulo como testes de integração
pytestmark = pytest.mark.integration


@pytest.fixture
def api_client() -> (
    None
):  # TODO: Add proper result = type if this fixture returns a value
    """Create a test API client."""
    from dc_api_x.client import ApiClient

    return ApiClient(
        url="https://api.example.com",
        username="testuser",
        password="testpass",
    )


class TestDatabaseIntegration:
    """Test integration with database services."""

    @pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="Database tests are skipped in CI environment",
    )
    def test_database_connection(self, in_memory_db) -> None:
        """Test database connection and basic operations."""
        cursor = in_memory_db.cursor()

        # Create a test table
        cursor.execute(
            """
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
            """,
        )

        # Insert test data
        cursor.execute(
            """
            INSERT INTO test_users (id, name, email)
            VALUES (1, 'Test User', 'test@example.com')
            """,
        )
        in_memory_db.commit()

        # Query the data
        cursor.execute("SELECT * FROM test_users WHERE id = 1")
        result = cursor.fetchone()

        # Verify the result
        assert result is not None
        assert result[0] == 1
        assert result[1] == "Test User"
        assert result[2] == "test@example.com"


class TestExternalApiIntegration:
    """Test integration with external APIs."""

    @responses.activate
    def test_external_api_call(self, api_client) -> None:
        """Test calling an external API."""
        # Add mock response for the external API
        responses.add(
            responses.GET,
            "https://api.example.com/external/users",
            json={"data": [{"id": 1, "name": "External User"}]},
            status=200,
        )

        # Call the external API
        response = api_client.get("external/users")

        # Verify the response
        assert response.success is True
        assert response.status_code == 200
        assert "data" in response.data
        assert isinstance(response.data["data"], list[Any])
        assert response.data["data"][0]["name"] == "External User"

    @patch("httpx.AsyncClient.get")
    async def test_async_external_api_call(self, mock_get, api_client):
        """Test async call to external API."""
        from httpx import Response

        # Mock the async response
        mock_response = Response(
            status_code=200,
            json={"data": [{"id": 2, "name": "Async User"}]},
        )
        mock_get.return_value = mock_response

        # This would be part of the actual API code
        async def fetch_external_data():
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com/external/async")
                return response.json()

        # Execute the async call
        result = await fetch_external_data()

        # Verify the result
        assert "data" in result
        assert isinstance(result["data"], list[Any])
        assert result["data"][0]["name"] == "Async User"
