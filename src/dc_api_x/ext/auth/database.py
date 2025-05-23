"""
Database authentication provider for DCApiX.

This module defines the DatabaseAuthProvider class for database authentication.
"""

from typing import Any, Optional

from ...exceptions import AuthenticationError


# Criando a exceção que está faltando
class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""


from .provider import AuthProvider


class DatabaseAuthProvider(AuthProvider):
    """Authentication provider that validates credentials against a database.

    This provider uses a database adapter to execute a query and validate
    credentials. It requires a database adapter, query, username and password
    field names, and optional token expiration time.
    """

    def __init__(
        self,
        adapter: Any,
        query: str,
        username_field: str = "username",
        password_field: str = "password",  # noqa: B107
        token_expiration: int = 3600,
    ):
        """Initialize the database auth provider.

        Args:
            adapter: Database adapter
            query: Query to execute for validating credentials
            username_field: Field name for username in the query parameters
            password_field: Field name for password in the query parameters
            token_expiration: Token expiration time in seconds
        """
        self.adapter = adapter
        self.query = query
        self.username_field = username_field
        self.password_field = password_field
        self.token_expiration = token_expiration

        # Store additional connection parameters
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._database: Optional[str] = None
        self._host: Optional[str] = None
        self._port: Optional[int] = None
        self._token: Optional[str] = None

    def authenticate(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate user against the database.

        Args:
            username: Username for authentication
            password: Password for authentication

        Returns:
            Authentication result with token and user information

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AuthenticationError: If authentication fails for other reasons
        """
        if not self.adapter:

            def _no_adapter_error():
                return AuthenticationError("No database adapter provided")

            raise _no_adapter_error()

        try:
            # Connect to the database if not already connected
            if not self.adapter.is_connected():
                self.adapter.connect()

            # Execute the query with credentials
            params = {
                self.username_field: username,
                self.password_field: password,
            }
            result = self.adapter.execute_query(self.query, params)

            # Check if any results were returned
            if not result or len(result) == 0:

                def _invalid_credentials():
                    return InvalidCredentialsError("Invalid credentials")

                raise _invalid_credentials()

            # Get the first user record
            user_data = result[0]

            # Generate a token (this would typically be more sophisticated)
            import time
            import uuid

            token = str(uuid.uuid4())
            expiration = int(time.time()) + self.token_expiration

            # Store the token for validation
            self._token = token

            # Create the authentication result
            auth_result = {
                "token": token,
                "expires_at": str(expiration),  # Convert to string for consistency
                "user": user_data,
            }

            return auth_result

        except Exception as e:
            if isinstance(e, InvalidCredentialsError):
                raise

            def _auth_failed_error(err):
                return AuthenticationError(f"Authentication failed: {str(err)}")

            raise _auth_failed_error(e) from e

    def set_connection_params(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Set connection parameters for the adapter.

        Args:
            username: Database username
            password: Database password
            database: Database name
            host: Database host
            port: Database port
        """
        self._username = username
        self._password = password
        self._database = database
        self._host = host
        self._port = port

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header with token.

        Returns:
            Header dictionary with token
        """
        if not self._token:
            return {}

        return {"Authorization": f"Bearer {self._token}"}

    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid
        """
        # In a real implementation, this would validate against stored tokens
        # or check token expiration, etc.
        return token == self._token and self._token is not None

    def refresh_token(self) -> dict[str, Any]:
        """Refresh authentication token.

        Returns:
            New token information
        """
        # This would typically look up the user and generate a new token
        if not self._token:

            def _not_authenticated_error():
                return AuthenticationError("Not authenticated")

            raise _not_authenticated_error()

        import time
        import uuid

        token = str(uuid.uuid4())
        expiration = int(time.time()) + self.token_expiration

        self._token = token

        return {
            "token": token,
            "expires_at": str(expiration),
        }

    def logout(self) -> bool:
        """Logout and invalidate current token.

        Returns:
            True if logout was successful
        """
        self._token = None
        return True
