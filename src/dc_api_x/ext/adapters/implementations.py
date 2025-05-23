"""
Concrete adapter implementations for DCApiX.

This module provides concrete adapter implementations for various protocols
including HTTP, database, and directory adapters.
"""

import importlib
import logging
from typing import Any, Optional, TypeVar, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ...utils.exceptions import ApiConnectionError
from ..auth import AuthProvider, BasicAuthProvider
from .database import DatabaseAdapter, DatabaseTransaction
from .directory import DirectoryAdapter
from .http import HttpAdapter

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RequestsHttpAdapter(HttpAdapter):
    """
    HTTP adapter implementation using the requests library.

    This class implements the HttpAdapter interface using the requests library.
    """

    def __init__(
        self,
        timeout: int = 60,
        *,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        auth_provider: AuthProvider | None = None,
    ) -> None:
        """
        Initialize the adapter.

        Args:
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum number of retries for failed requests
            retry_backoff: Backoff factor for retries
            auth_provider: Authentication provider
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.auth_provider = auth_provider
        self.client = None

    def connect(self) -> bool:
        """
        Establish a connection and set up the HTTP client.

        This method creates and configures a requests.Session with retry and auth.

        Returns:
            True if connection was successful, False otherwise
        """
        try:
            # Create a new session
            self.client = requests.Session()

            # Configure retries
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=self.retry_backoff,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=[
                    "HEAD",
                    "GET",
                    "OPTIONS",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                ],
            )

            # Add retry handler to session
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.client.mount("http://", adapter)
            self.client.mount("https://", adapter)

            # Set default headers
            self.client.headers.update({"User-Agent": "DCApiX/1.0"})

            # Configure authentication
            if self.auth_provider:
                if isinstance(self.auth_provider, BasicAuthProvider):
                    self.client.auth = (
                        self.auth_provider.username,
                        self.auth_provider.password,
                    )
                elif (
                    self.auth_provider.is_authenticated()
                    and self.auth_provider.is_token_valid()
                ):
                    auth_headers = self.auth_provider.get_auth_header()
                    self.client.headers.update(auth_headers)
        except Exception:
            logging.exception("Failed to create HTTP client")
            return False
        else:
            # Connection established successfully
            return True

    def disconnect(self) -> bool:
        """
        Close the connection.

        This method closes the requests session.

        Returns:
            True if disconnection was successful, False otherwise
        """
        try:
            if self.client:
                self.client.close()
                self.client = None
        except Exception:
            logging.exception("Failed to close HTTP client")
            return False
        else:
            return True

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, Any], bytes]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional request parameters

        Returns:
            Tuple of (status_code, headers, body)
        """
        if not self.client:
            self.connect()

        # Handle timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        # Handle SSL verification
        if "verify" not in kwargs:
            kwargs["verify"] = self.verify_ssl

        # Make the request
        response = self.client.request(method.upper(), url, **kwargs)

        # Prepare the return tuple
        status_code = response.status_code
        headers = dict(response.headers)
        body = response.content

        return (status_code, headers, body)

    def set_option(self, name: str, value: Any) -> None:
        """Set an adapter option."""
        setattr(self, name, value)

    def is_connected(self) -> bool:
        """Check if the adapter is connected."""
        return self.client is not None


class DatabaseTransactionImpl(DatabaseTransaction):
    """Database transaction implementation."""

    def __init__(self, connection: Any, *, autocommit: bool = False) -> None:
        """
        Initialize the transaction.

        Args:
            connection: Database connection
            autocommit: Whether to auto-commit queries
        """
        self.connection = connection
        self.autocommit = autocommit
        self.cursor = None

    def __enter__(self) -> "DatabaseTransactionImpl":
        """Enter the context manager."""
        if not self.autocommit and hasattr(self.connection, "begin"):
            # Start the transaction
            self.connection.begin()

        # Create a cursor
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None

        if exc_type is None and not self.autocommit:
            # Commit the transaction on success
            self.commit()
        elif exc_type is not None and not self.autocommit:
            # Rollback on exception
            self.rollback()

    def execute(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """
        Execute a query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query result
        """
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    def fetchall(self) -> list[dict[str, Any]]:
        """
        Fetch all rows.

        Returns:
            List of rows as dictionaries
        """
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def fetchone(self) -> dict[str, Any] | None:
        """
        Fetch one row.

        Returns:
            Row as dictionary or None
        """
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row, strict=False))

    def commit(self) -> None:
        """Commit the transaction."""
        if hasattr(self.connection, "commit"):
            self.connection.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        if hasattr(self.connection, "rollback"):
            self.connection.rollback()


class GenericDatabaseAdapter(DatabaseAdapter[dict[str, Any]]):
    """
    Generic database adapter implementation.

    This adapter works with various SQL database engines.
    """

    def __init__(
        self,
        connection_string: str,
        driver: str = "sqlite3",
        auth_provider: AuthProvider | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the adapter.

        Args:
            connection_string: Database connection string
            driver: Database driver module (default: sqlite3)
            auth_provider: Authentication provider
            **kwargs: Additional connection parameters
        """
        self.connection_string = connection_string
        self.driver = driver
        self.auth_provider = auth_provider
        self.connection_params = kwargs
        self.connection: Any = None
        self.db_module: Any = None

    def connect(self) -> bool:
        """
        Establish a connection to the database.

        This method loads the database driver and connects to the database.

        Returns:
            True if connection was successful, False otherwise
        """
        try:
            # Load the database driver
            self.db_module = importlib.import_module(self.driver)

            # Get credentials from auth provider if available
            if self.auth_provider:
                self.auth_provider.authenticate()
                if hasattr(self.auth_provider, "get_credentials"):
                    credentials = self.auth_provider.get_credentials()
                    self.connection_params.update(credentials)

            # Connect to the database
            if self.driver == "sqlite3":
                self.connection = self.db_module.connect(self.connection_string)
            else:
                self.connection = self.db_module.connect(
                    self.connection_string,
                    **self.connection_params,
                )

            logger.debug(f"Connected to {self.driver} database")
        except ImportError as err:
            raise ImportError(f"Database driver {self.driver} not found") from err
        except Exception as e:
            raise ApiConnectionError(f"Failed to connect to database: {str(e)}") from e
        else:
            return True

    def disconnect(self) -> bool:
        """
        Close the database connection.

        Returns:
            True if disconnection was successful, False otherwise
        """
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.debug(f"Disconnected from {self.driver} database")
        except Exception:
            logger.exception("Failed to close database connection")
            return False
        else:
            return True

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a database query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        if not self.connection:
            self.connect()

        with DatabaseTransactionImpl(self.connection) as transaction:
            transaction.execute(query, params)
            return transaction.fetchall()

    def execute_write(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Execute a write operation.

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            Number of affected rows
        """
        if not self.connection:
            self.connect()

        with DatabaseTransactionImpl(self.connection) as transaction:
            result = transaction.execute(query, params)
            if hasattr(result, "rowcount"):
                return result.rowcount
            return 0

    def transaction(self) -> DatabaseTransaction:
        """
        Begin a database transaction.

        Returns:
            Transaction object
        """
        if not self.connection:
            self.connect()

        return DatabaseTransactionImpl(self.connection, autocommit=False)

    def is_connected(self) -> bool:
        """
        Check if connected to the database.

        Returns:
            True if connected, False otherwise
        """
        return self.connection is not None

    def set_option(self, name: str, value: Any) -> None:
        """
        Set an adapter option.

        Args:
            name: Option name
            value: Option value
        """
        setattr(self, name, value)


class DirectoryAdapterImpl(DirectoryAdapter):
    """
    LDAP directory adapter implementation.

    This adapter works with the python-ldap library.
    """

    def __init__(
        self,
        url: str,
        base_dn: str,
        auth_provider: AuthProvider | None = None,
    ) -> None:
        """
        Initialize the adapter.

        Args:
            url: LDAP server URL
            base_dn: Base DN for the directory
            auth_provider: Authentication provider
        """
        self.url = url
        self.base_dn = base_dn
        self.auth_provider = auth_provider
        self.connection = None
        self.ldap_module = None

    def connect(self) -> bool:
        """
        Establish a connection to the LDAP directory.

        This method loads the python-ldap module and connects to the directory.

        Returns:
            True if connection was successful, False otherwise
        """
        try:
            # Load the LDAP module
            self.ldap_module = importlib.import_module("ldap")

            # Initialize the connection
            self.connection = self.ldap_module.initialize(self.url)

            # Set options
            self.connection.set_option(self.ldap_module.OPT_REFERRALS, 0)
            self.connection.set_option(self.ldap_module.OPT_PROTOCOL_VERSION, 3)

            # Bind with credentials if auth provider is available
            if self.auth_provider:
                self.auth_provider.authenticate()
                if hasattr(self.auth_provider, "get_credentials"):
                    credentials = self.auth_provider.get_credentials()
                    bind_dn = credentials.get("username")
                    bind_password = credentials.get("password")
                    if bind_dn and bind_password:
                        self.connection.simple_bind_s(bind_dn, bind_password)

            logger.debug(f"Connected to LDAP directory at {self.url}")
        except ImportError as err:
            raise ImportError("python-ldap module not found") from err
        except Exception as e:
            raise ApiConnectionError(
                f"Failed to connect to LDAP directory: {str(e)}",
            ) from e
        else:
            return True

    def disconnect(self) -> bool:
        """
        Close the LDAP connection.

        Returns:
            True if disconnection was successful, False otherwise
        """
        try:
            if self.connection:
                self.connection.unbind_s()
                self.connection = None
                logger.debug(f"Disconnected from LDAP directory at {self.url}")
        except Exception:
            logger.exception("Failed to close LDAP connection")
            return False
        else:
            return True

    def search(
        self,
        base_dn: str,
        search_filter: str,
        attributes: list[str] | None = None,
        scope: str = "subtree",
    ) -> list[dict[str, list[bytes]]]:
        """
        Search the LDAP directory.

        Args:
            base_dn: Base DN for the search
            search_filter: LDAP search filter
            attributes: Attributes to return
            scope: Search scope (base, onelevel, subtree)

        Returns:
            List of entries, each a dict of attribute: values
        """
        if not self.connection:
            self.connect()

        if self.connection is None or self.ldap_module is None:
            return []  # Return empty list if connection failed

        # Combine with base DN if provided
        if not base_dn:
            base_dn = self.base_dn

        # Map scope string to LDAP scope constant
        scope_map = {
            "base": self.ldap_module.SCOPE_BASE,
            "onelevel": self.ldap_module.SCOPE_ONELEVEL,
            "subtree": self.ldap_module.SCOPE_SUBTREE,
        }
        scope_value = scope_map.get(scope.lower(), self.ldap_module.SCOPE_SUBTREE)

        # Perform the search
        result = self.connection.search_s(
            base_dn,
            scope_value,
            search_filter,
            attributes,
        )

        # Convert to list of dictionaries (remove DN from result)
        return [attrs for _, attrs in result]

    def add(
        self,
        dn: str,
        attributes: dict[str, list[Union[str, bytes]]],
    ) -> None:
        """
        Add an entry to the directory.

        Args:
            dn: DN of the entry to add
            attributes: Attributes of the entry
        """
        if not self.connection:
            self.connect()

        # Convert attributes to proper format if needed
        ldap_attrs = {}
        for key, values in attributes.items():
            if all(isinstance(v, str) for v in values):
                # Convert strings to bytes
                ldap_attrs[key] = [
                    v.encode("utf-8") if isinstance(v, str) else v for v in values
                ]
            else:
                ldap_attrs[key] = values

        # Add the entry
        self.connection.add_s(dn, list(ldap_attrs.items()))

    def modify(
        self,
        dn: str,
        changes: dict[str, tuple[str, list[Union[str, bytes]]]],
    ) -> None:
        """
        Modify an entry in the directory.

        Args:
            dn: DN of the entry to modify
            changes: Dictionary of attribute: (operation, values)
                    where operation is one of "add", "delete", "replace"
        """
        if not self.connection:
            self.connect()

        # Map operation strings to LDAP constants
        op_map = {
            "add": self.ldap_module.MOD_ADD,
            "delete": self.ldap_module.MOD_DELETE,
            "replace": self.ldap_module.MOD_REPLACE,
        }

        # Convert changes to proper format
        mods = []
        for attr, (op, values) in changes.items():
            # Convert operation string to LDAP constant
            op_value = op_map.get(op.lower(), self.ldap_module.MOD_REPLACE)

            # Convert string values to bytes if needed
            if all(isinstance(v, str) for v in values):
                values = [
                    v.encode("utf-8") if isinstance(v, str) else v for v in values
                ]

            mods.append((op_value, attr, values))

        # Modify the entry
        self.connection.modify_s(dn, mods)

    def delete(self, dn: str) -> None:
        """
        Delete an entry from the directory.

        Args:
            dn: DN of the entry to delete
        """
        if not self.connection:
            self.connect()

        # Delete the entry
        self.connection.delete_s(dn)

    def is_connected(self) -> bool:
        """
        Check if connected to the directory.

        Returns:
            True if connected, False otherwise
        """
        return self.connection is not None

    def set_option(self, name: str, value: Any) -> None:
        """
        Set an adapter option.

        Args:
            name: Option name
            value: Option value
        """
        setattr(self, name, value)
