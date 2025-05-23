"""
Basic authentication provider for DCApiX.

This module defines the BasicAuthProvider class for HTTP Basic Authentication.
"""

from typing import Any, Optional

from ...exceptions import AuthenticationError, InvalidCredentialsError
from .provider import AuthProvider


class BasicAuthProvider(AuthProvider):
    """Simple username/password authentication provider.

    This provider stores credentials in memory and validates against them.
    It's primarily used for testing or simple authentication scenarios.
    """

    def __init__(
        self,
        username: str = "",
        password: str = "",  # noqa: B107
        token_expiration: int = 3600,
    ):
        """
        Initialize the basic auth provider.

        Args:
            username: Default username
            password: Default password
            token_expiration: Token expiration time in seconds
        """
        self.username = username
        self.password = password
        self.valid_username = username
        self.valid_password = password
        self.token_expiration = token_expiration
        self._token: Optional[str] = None
        self._authenticated = False

    def authenticate(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> dict[str, Any]:
        """Authenticate using basic credentials.

        Args:
            username: Username to authenticate (optional if set in constructor)
            password: Password to authenticate (optional if set in constructor)

        Returns:
            Dict containing authentication info

        Raises:
            AuthenticationError: If authentication fails
            InvalidCredentialsError: If credentials are invalid
        """
        # Use provided credentials or fall back to those set in constructor
        auth_username = username or self.valid_username
        auth_password = password or self.valid_password

        # Check if credentials are valid
        if not auth_username or not auth_password:

            def _credentials_required_error():
                return AuthenticationError("Username and password are required")

            raise _credentials_required_error()

        if auth_username != self.valid_username or auth_password != self.valid_password:

            def _invalid_credentials_error():
                return InvalidCredentialsError("Invalid username or password")

            raise _invalid_credentials_error()

        # Create a simple token
        import time
        import uuid

        token_value = str(uuid.uuid4())
        expiration = int(time.time()) + self.token_expiration

        # Store token for validation
        self._token = token_value
        self._authenticated = True

        # Return authentication information
        return {
            "authenticated": True,
            "username": auth_username,
            "token": token_value,
            "expires_at": str(expiration),
            "user": {"username": auth_username},
        }

    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        return token == self._token and self._authenticated

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header for requests.

        Returns:
            Authorization header dictionary
        """
        if not self._authenticated or not self._token:
            return {}

        return {"Authorization": f"Bearer {self._token}"}

    def refresh_token(self) -> dict[str, Any]:
        """Refresh the authentication token.

        Returns:
            Dict containing the new token information
        """
        if not self._authenticated:

            def _not_authenticated_error():
                return AuthenticationError("Not authenticated")

            raise _not_authenticated_error()

        # Generate a new token
        import time
        import uuid

        token_value = str(uuid.uuid4())
        expiration = int(time.time()) + self.token_expiration

        # Update stored token
        self._token = token_value

        # Return new token information
        return {
            "token": token_value,
            "expires_at": str(expiration),
        }

    def logout(self) -> bool:
        """Logout and invalidate the current token.

        Returns:
            True if logout was successful
        """
        self._token = None
        self._authenticated = False
        return True

    def is_authenticated(self) -> bool:
        """Check if the provider is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated

    def is_token_valid(self) -> bool:
        """Check if the current token is valid.

        Returns:
            True if token is valid, False otherwise
        """
        return self._token is not None and self._authenticated
