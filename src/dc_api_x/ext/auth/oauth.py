"""
OAuth authentication provider for DCApiX.

This module defines the OAuthProvider class for OAuth 2.0 authentication.
"""

import abc
from typing import Any, Optional

from .provider import AuthProvider


class OAuthProvider(AuthProvider):
    """Provider for OAuth 2.0 authentication."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> None:
        """
        Initialize with OAuth details.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_url: URL to get token from
            scope: OAuth scope (optional)
            redirect_uri: Redirect URI for authorization code flow (optional)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    @abc.abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate with the OAuth service.

        This method should be implemented by subclasses to handle
        specific OAuth flows (client credentials, authorization code, etc.)
        """

    def is_authenticated(self) -> bool:
        """Check if access token is set and not expired."""
        import time

        if self.access_token is None:
            return False

        if self.token_expiry is None:
            return True

        return time.time() < self.token_expiry

    def get_auth_headers(self) -> dict[str, str]:
        """Return auth headers with access token."""
        if not self.is_authenticated():
            self.authenticate()

        return {"Authorization": f"Bearer {self.access_token}"}

    def get_auth_params(self) -> dict[str, Any]:
        """Return empty dict as auth is in headers."""
        return {}

    def clear_auth(self) -> None:
        """Clear tokens."""
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
