"""
Base authentication provider for DCApiX.

This module defines the base AuthProvider abstract class that all
specific authentication providers must inherit from.
"""

import abc
from typing import Any


class AuthProvider(abc.ABC):
    """
    Base interface for authentication providers.

    Authentication providers handle authentication for various protocols
    and services.
    """

    @abc.abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate with the service.

        This method should perform the authentication process and store
        any necessary credentials for future requests.
        """

    @abc.abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the provider is authenticated.

        Returns:
            True if authenticated, False otherwise
        """

    @abc.abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """
        Get headers for authentication.

        Returns:
            Headers to include in the request for authentication
        """

    @abc.abstractmethod
    def get_auth_params(self) -> dict[str, Any]:
        """
        Get parameters for authentication.

        Returns:
            Parameters to include in the request for authentication
        """

    @abc.abstractmethod
    def clear_auth(self) -> None:
        """Clear authentication credentials."""
