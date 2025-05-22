"""
LDAP authentication provider for DCApiX.

This module defines the LdapAuthProvider class for LDAP authentication.
"""

from typing import Any, Optional

from .provider import AuthProvider


class LdapAuthProvider(AuthProvider):
    """Provider for LDAP authentication."""

    def __init__(
        self,
        bind_dn: str,
        password: str,
        ldap_server: str,
        *,
        use_ssl: bool = True,
        port: Optional[int] = None,
    ) -> None:
        """
        Initialize with LDAP details.

        Args:
            bind_dn: LDAP bind DN
            password: LDAP password
            ldap_server: LDAP server hostname
            use_ssl: Whether to use SSL/TLS (default True)
            port: LDAP port (default 389 for non-SSL, 636 for SSL)
        """
        self.bind_dn = bind_dn
        self.password = password
        self.ldap_server = ldap_server
        self.use_ssl = use_ssl
        self.port = port or (636 if use_ssl else 389)
        self.authenticated = False

    def authenticate(self) -> None:
        """
        Mark as authenticated (actual auth happens at connection time).

        LDAP authentication typically happens during connection establishment,
        so this just marks the provider as authenticated for tracking.
        """
        self.authenticated = True

    def is_authenticated(self) -> bool:
        """Return authentication status."""
        return self.authenticated

    def get_auth_headers(self) -> dict[str, str]:
        """Return empty dict as LDAP doesn't use headers."""
        return {}

    def get_auth_params(self) -> dict[str, Any]:
        """Return LDAP connection parameters."""
        return {
            "bind_dn": self.bind_dn,
            "password": self.password,
            "server": self.ldap_server,
            "use_ssl": self.use_ssl,
            "port": self.port,
        }

    def clear_auth(self) -> None:
        """Clear authentication status."""
        self.authenticated = False
