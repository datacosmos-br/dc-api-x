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

        # Set default port based on SSL setting if not provided
        if port is None:
            self.port = 636 if use_ssl else 389
        else:
            self.port = port

        self.authenticated = False
        self.conn = None

    def authenticate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Authenticate with LDAP server.

        Returns:
            Dictionary with authentication result
        """
        try:
            # Try to import ldap3
            import ldap3

            # Create server object
            server = ldap3.Server(
                self.ldap_server,
                port=self.port,
                use_ssl=self.use_ssl,
            )

            # Create connection
            conn = ldap3.Connection(
                server,
                user=self.bind_dn,
                password=self.password,
                auto_bind=True,
            )

            # Check if bind was successful
            if conn.bound:
                self.conn = conn
                self.authenticated = True
                return {
                    "authenticated": True,
                    "user": self.bind_dn,
                }

            return {
                "authenticated": False,
                "message": "Failed to bind with provided credentials",
            }

        except ImportError:
            return {
                "authenticated": False,
                "message": "LDAP support not available (ldap3 not installed)",
            }
        except Exception as e:
            return {
                "authenticated": False,
                "message": f"LDAP authentication failed: {str(e)}",
            }

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header for making authenticated requests.

        Not typically used for LDAP but included for protocol compatibility.

        Returns:
            Empty dictionary as LDAP doesn't use auth headers in the same way
        """
        return {}

    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.

        LDAP doesn't use tokens in the same way as OAuth/JWT, but we check
        if the token matches the bind_dn for compatibility.

        Args:
            token: Token to validate

        Returns:
            True if authenticated and token matches bind_dn
        """
        return self.authenticated and token == self.bind_dn

    def refresh_token(self) -> dict[str, Any]:
        """Refresh the authentication by reconnecting to LDAP.

        Returns:
            Authentication result
        """
        if self.conn:
            try:
                # Close existing connection
                self.conn.unbind()
            except Exception:
                # Ignore errors when closing existing connection
                pass

        # Re-authenticate
        return self.authenticate()

    def logout(self) -> bool:
        """Logout by unbinding from LDAP server.

        Returns:
            True if successful
        """
        if self.conn and self.authenticated:
            try:
                self.conn.unbind()
                self.authenticated = False
                self.conn = None
                return True
            except Exception:
                return False

        return True  # Already logged out
