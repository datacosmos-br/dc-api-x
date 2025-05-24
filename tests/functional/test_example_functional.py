"""
Example functional test for the dc-api-x API.

This test demonstrates how to write functional tests for the API.
"""

from typing import Any

import pytest

# Marcar todos os testes neste módulo como testes funcionais
pytestmark = pytest.mark.functional


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


class TestBasicApiFlow:
    """Test basic API flow."""

    def test_create_and_retrieve_resource(self, api_client) -> None:
        """Test creating and retrieving a resource."""
        # Create a new resource
        create_response = api_client.post(
            "users",
            json_data={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )

        # Verify creation
        assert create_response.success is True
        assert create_response.status_code == 201
        assert "id" in create_response.data
        user_id = create_response.data["id"]

        # Retrieve the created resource
        get_response = api_client.get(f"users/{user_id}")

        # Verify retrieval
        assert get_response.success is True
        assert get_response.status_code == 200
        assert get_response.data["id"] == user_id
        assert get_response.data["name"] == "John Doe"
        assert get_response.data["email"] == "john@example.com"


class TestSearchAndPagination:
    """Test search and pagination functionality."""

    def test_search_resources(self, api_client) -> None:
        """Test searching resources."""
        # Search for resources
        response = api_client.get("users", params={"search": "John"})

        # Verify response
        assert response.success is True
        assert response.status_code == 200
        assert "data" in response.data
        assert isinstance(response.data["data"], list[Any])

        # Check that results match search criteria
        for user in response.data["data"]:
            assert "John" in user["name"]

    def test_paginated_results(self, api_client) -> None:
        """Test paginated results."""
        # Get paginated results (page 1)
        page1_response = api_client.get("users", params={"page": 1, "per_page": 2})

        # Verify response
        assert page1_response.success is True
        assert page1_response.status_code == 200
        assert "data" in page1_response.data
        assert len(page1_response.data["data"]) <= 2

        # Get paginated results (page 2)
        page2_response = api_client.get("users", params={"page": 2, "per_page": 2})

        # Verify response
        assert page2_response.success is True
        assert page2_response.status_code == 200
        assert "data" in page2_response.data

        # Ensure different pages return different results
        if page1_response.data["data"] and page2_response.data["data"]:
            page1_ids = [user["id"] for user in page1_response.data["data"]]
            page2_ids = [user["id"] for user in page2_response.data["data"]]
            assert set(page1_ids).isdisjoint(set(page2_ids))
