"""
Basic authentication provider for DCApiX.

This module defines the BasicAuthProvider class for HTTP Basic Authentication.
"""

from typing import Any, Optional

from .provider import AuthProvider


class BasicAuthProvider(AuthProvider):
    """Provider for HTTP Basic Authentication."""

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize with username and password.

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username: Optional[str] = username
        self.password: Optional[str] = password

    def authenticate(self) -> None:
        """Nothing to do for basic auth, just store credentials."""

    def is_authenticated(self) -> bool:
        """Always authenticated if credentials are set."""
        return self.username is not None and self.password is not None

    def get_auth_headers(self) -> dict[str, str]:
        """Return auth headers as empty dict (handled by requests auth)."""
        return {}

    def get_auth_params(self) -> dict[str, Any]:
        """Return auth params with basic auth credentials."""
        return {"auth": (self.username, self.password)}

    def clear_auth(self) -> None:
        """Clear credentials."""
        self.username = None
        self.password = None
