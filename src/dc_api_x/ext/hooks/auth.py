"""
Authentication hook for DCApiX.

This module provides hooks for injecting authentication credentials into requests.
"""

from typing import Any

from ..auth import AuthProvider
from .protocol import RequestHook


class AuthHook(RequestHook):
    """
    Hook that injects authentication information into requests.

    This hook uses an AuthProvider to inject authentication credentials
    into each request.
    """

    def __init__(self, auth_provider: AuthProvider) -> None:
        """
        Initialize with an authentication provider.

        Args:
            auth_provider: Provider that implements authentication logic
        """
        self.auth_provider = auth_provider

    def process_request(
        self,
        _method: str,
        _url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add authentication to the request.

        This adds authentication headers from the auth_provider
        to the request kwargs.

        Args:
            _method: HTTP method
            _url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified request kwargs with authentication added
        """
        # Get headers with authentication from provider
        auth_headers = self.auth_provider.get_auth_header()

        # If headers exist in kwargs, update them; otherwise create
        if "headers" in kwargs:
            headers = kwargs.get("headers", {})
            if isinstance(headers, dict[str, Any]):
                headers.update(auth_headers)
            kwargs["headers"] = headers
        else:
            kwargs["headers"] = auth_headers

        return kwargs
