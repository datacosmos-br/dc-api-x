"""
Base authentication provider for DCApiX.

This module defines the base AuthProvider abstract class that all
specific authentication providers must inherit from.
"""

from typing import Any, Protocol


class AuthProvider(Protocol):
    """Abstract base class for authentication providers.

    Authentication providers handle different authentication mechanisms
    like basic auth, OAuth, JWT, etc.
    """

    def authenticate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Authenticate with the provider.

        Returns:
            Authentication result with token and user information
        """
        ...

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header for making authenticated requests.

        Returns:
            Dictionary with authentication headers
        """
        ...

    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        ...

    def refresh_token(self) -> dict[str, Any]:
        """Refresh the authentication token.

        Returns:
            New token information
        """
        ...

    def logout(self) -> bool:
        """Logout and invalidate the current token.

        Returns:
            True if logout was successful
        """
        ...
