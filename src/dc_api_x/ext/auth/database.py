"""
Database authentication provider for DCApiX.

This module defines the DatabaseAuthProvider class for database authentication.
"""

from typing import Any, Optional

from .provider import AuthProvider


class DatabaseAuthProvider(AuthProvider):
    """Provider for database authentication."""

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        host: str = "localhost",
        port: Optional[int] = None,
    ) -> None:
        """
        Initialize with database details.

        Args:
            username: Database username
            password: Database password
            database: Database name
            host: Database host (default localhost)
            port: Database port (optional, database-specific default)
        """
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.authenticated = False

    def authenticate(self) -> None:
        """
        Mark as authenticated (actual auth happens at connection time).

        Database authentication typically happens during connection establishment,
        so this just marks the provider as authenticated for tracking.
        """
        self.authenticated = True

    def is_authenticated(self) -> bool:
        """Return authentication status."""
        return self.authenticated

    def get_auth_headers(self) -> dict[str, str]:
        """Return empty dict as database doesn't use headers."""
        return {}

    def get_auth_params(self) -> dict[str, Any]:
        """Return database connection parameters."""
        params = {
            "user": self.username,
            "password": self.password,
            "database": self.database,
            "host": self.host,
        }

        if self.port is not None:
            params["port"] = int(self.port)

        return params

    def clear_auth(self) -> None:
        """Clear authentication status."""
        self.authenticated = False
