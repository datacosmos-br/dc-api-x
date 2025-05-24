"""
Test data factories for creating test objects.

This module provides factory functions and classes for creating test data
with sensible defaults that can be overridden as needed.
"""

from typing import Any, Optional

from pydantic import BaseModel

from dc_api_x.client import ApiClient
from tests.constants import (
    DEFAULT_USER,
    NO_MOCK_RESPONSE_ERROR,
    TEST_API_URL,
    TEST_AUTH_PASSWORD,
    TEST_AUTH_TOKEN,
    TEST_AUTH_USERNAME,
)


class User(BaseModel):
    """User model for testing."""

    id: int
    name: str
    email: str
    role: str = "user"
    active: bool = True

    def has_permission(self, permission: str) -> bool:
        """Check if user has specified permission."""
        if permission == "manage_users":
            return self.role == "admin"
        if permission == "edit_content":
            return self.role in ["admin", "editor"]
        return permission == "view_content"


class MockAuthProvider:
    """Mock authentication provider for testing."""

    def __init__(self, token: str = TEST_AUTH_TOKEN) -> None:  # noqa: S107
        self.token = token
        self.username = TEST_AUTH_USERNAME
        self.password = TEST_AUTH_PASSWORD

    def authenticate(self) -> dict[str, str]:
        """Return a mock authentication response."""
        return {"token": self.token}

    def get_headers(self) -> dict[str, str]:
        """Return authorization headers."""
        return {"Authorization": f"Bearer {self.token}"}


class MockAdapter:
    """Mock adapter for testing."""

    def __init__(self, responses: dict[tuple[str, str], Any] = None) -> None:
        """Initialize with predefined responses.

        Args:
            responses: Dictionary mapping (method, path) tuples to response data
        """
        self.responses = responses or {}
        self.requests = []
        if self is not None:
            self.last_request = None
        else:
            # Handle None case appropriately
            pass  # TODO: Implement proper None handling

    def request(self, method: str, path: str, **kwargs) -> Any:
        """Mock a request and return predefined response.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            **kwargs: Additional request parameters

        Returns:
            Predefined response data

        Raises:
            KeyError: If no response is defined for the request
        """
        # Store the request for later inspection
        request = {"method": method, "path": path, "kwargs": kwargs}
        self.requests.append(request)
        self.last_request = request

        # Look up the response
        key = (method, path)
        if key not in self.responses:
            raise KeyError(NO_MOCK_RESPONSE_ERROR)

        return self.responses[key]


class UserFactory:
    """Factory for creating User instances with defaults."""

    @classmethod
    def create(cls, overrides: Optional[dict[str, Any]] = None) -> User:
        """Create a User instance with custom overrides.

        Args:
            overrides: Optional dictionary of attribute overrides

        Returns:
            User instance
        """
        defaults = DEFAULT_USER.copy()

        if overrides:
            defaults.update(overrides)

        return User(**defaults)


def create_mock_client_with_responses(
    responses: dict[tuple[str, str], Any],
) -> ApiClient:
    """Create an API client with mock responses.

    Args:
        responses: Dictionary mapping (method, path) tuples to response data

    Returns:
        ApiClient instance with mock adapter
    """
    mock_adapter = MockAdapter(responses=responses)
    # Create client based on the actual signature expected by ApiClient
    # Adjust parameters based on the actual implementation
    client = ApiClient(url=TEST_API_URL, adapter=mock_adapter)
    # Add a reference to the mock adapter for test assertions
    client.adapter = mock_adapter
    # Add a mock auth provider for convenience in tests
    client.auth_provider = MockAuthProvider()

    return client


def create_temp_file_with_content(content: str) -> str:
    """Create a temporary file with the specified content.

    Args:
        content: File content

    Returns:
        Path to the temporary file
    """
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(content.encode())

    return temp_file.name
