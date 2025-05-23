"""
Token authentication provider for DCApiX.

This module defines the TokenAuthProvider class for token-based authentication.
"""

from typing import Any, Optional

from .provider import AuthProvider


class TokenAuthProvider(AuthProvider):
    """Provider for token-based authentication."""

    def __init__(
        self,
        token: Optional[str] = None,
        token_type: str = "Bearer",
        header_name: str = "Authorization",
    ) -> None:
        """
        Initialize with token details.

        Args:
            token: Authentication token (optional, can be set later)
            token_type: Type of token, e.g., 'Bearer' (default) or 'Token'
            header_name: Name of the header to use for the token
        """
        self.token = token
        self.token_type = token_type
        self.header_name = header_name

    def authenticate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Token auth requires token to be set externally.

        This method does nothing by default and expects the token
        to be set during initialization or separately.

        Returns:
            Authentication result with token information
        """
        if self.token is None:

            def _missing_token_error():
                return ValueError("Token must be set before authentication")

            raise _missing_token_error()

        # Return token information
        return {
            "token": self.token,
            "token_type": self.token_type,
            "authenticated": True,
        }

    def is_authenticated(self) -> bool:
        """Check if token is set."""
        return self.token is not None

    def get_auth_headers(self) -> dict[str, str]:
        """Return auth headers with token."""
        if not self.is_authenticated():
            return {}

        return {self.header_name: f"{self.token_type} {self.token}"}

    def get_auth_params(self) -> dict[str, Any]:
        """Return empty dict as auth is in headers."""
        return {}

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header for making authenticated requests.

        Returns:
            Dictionary with authentication headers
        """
        return self.get_auth_headers()

    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        # Simple implementation just checks if token matches current token
        return token == self.token

    def refresh_token(self) -> dict[str, Any]:
        """Refresh the authentication token.

        Returns:
            New token information
        """
        # Token provider doesn't handle refreshing, just return current token info
        return {
            "token": self.token,
            "token_type": self.token_type,
            "refreshed": False,
        }

    def logout(self) -> bool:
        """Logout and invalidate the current token.

        Returns:
            True if logout was successful
        """
        self.clear_auth()
        return True

    def clear_auth(self) -> None:
        """Clear token."""
        self.token = None
