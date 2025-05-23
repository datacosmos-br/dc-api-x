"""
Adapter implementations for DCApiX.

This module provides concrete adapter implementations that can be used out of the box,
including HTTP, database, and directory adapters.
"""

import importlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import AdapterError
from ..ext.adapters import (
    DatabaseAdapter,
    DatabaseTransaction,
    DirectoryAdapter,
    HttpAdapter,
)
from ..ext.auth import AuthProvider, BasicAuthProvider

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
        auth_provider: Optional[AuthProvider] = None,
    ):
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

    def connect(self) -> None:
        """
        Establish a connection and set up the HTTP client.

        This method creates and configures a requests.Session with retry and auth.
        """
        try:
            # Create a new session
            self.client = requests.Session()

            # Configure retries
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=self.retry_backoff,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
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
                elif self.auth_provider.is_authenticated():
                    if self.auth_provider.is_token_valid():
                        auth_headers = self.auth_provider.get_auth_header()
                        self.client.headers.update(auth_headers)
            return
        except Exception as e:
            logger.error(f"Failed to create HTTP client: {str(e)}")
            raise

    def disconnect(self) -> None:
        """
        Close the connection.

        This method closes the requests session.
        """
        if self.client:
            self.client.close()
            self.client = None

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, str], bytes]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
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

        # Return status code, headers, and body
        headers = dict(response.headers)
        return response.status_code, headers, response.content

    def set_option(self, name: str, value: Any) -> None:
        """Set an adapter option."""
        pass  # Implement if needed

    def is_connected(self) -> bool:
        """Check if the adapter is connected."""
        return self.client is not None


class DatabaseTransactionImpl(DatabaseTransaction):
    """Database transaction implementation."""

    def __init__(self, connection: Any, *, autocommit: bool = False):
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
        if not self.autocommit:
            # Start the transaction
            if hasattr(self.connection, "begin"):
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

    def execute(self, query: str, params: Optional[dict[str, Any]] = None) -> Any:
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
        return [dict(zip(columns, row)) for row in rows]

    def fetchone(self) -> Optional[dict[str, Any]]:
        """
        Fetch one row.

        Returns:
            Row as dictionary or None
        """
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    def commit(self) -> None:
        """Commit the transaction."""
        if hasattr(self.connection, "commit"):
            self.connection.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        if hasattr(self.connection, "rollback"):
            self.connection.rollback()


class GenericDatabaseAdapter(DatabaseAdapter):
    """
    Generic database adapter implementation.

    This adapter works with various SQL database engines.
    """

    def __init__(
        self,
        connection_string: str,
        driver: str = "sqlite3",
        auth_provider: Optional[AuthProvider] = None,
        **kwargs: Any,
    ):
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
        self.connection = None
        self.db_module = None

    def connect(self) -> None:
        """
        Establish a connection to the database.

        This method loads the database driver and connects to the database.
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

            logger.debug("Connected to {self.driver} database")
        except ImportError as err:
            def _driver_not_found_error():
                return ImportError(f"Database driver {self.driver} not found")
            raise _driver_not_found_error() from err
        except Exception as e:
            def _connection_error(err):
                return ConnectionError(f"Failed to connect to database: {str(err)}")
            raise _connection_error(e) from e

    def disconnect(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("Disconnected from {self.driver} database")

    def execute(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
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

    def begin_transaction(self, *, autocommit: bool = False) -> DatabaseTransaction:
        """
        Begin a database transaction.

        Args:
            autocommit: Whether to auto-commit queries

        Returns:
            Transaction object
        """
        if not self.connection:
            self.connect()

        return DatabaseTransactionImpl(self.connection, autocommit)


class DirectoryAdapterImpl(DirectoryAdapter):
    """
    LDAP directory adapter implementation.

    This adapter works with the python-ldap library.
    """

    def __init__(
        self,
        url: str,
        base_dn: str,
        auth_provider: Optional[AuthProvider] = None,
    ):
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

    def connect(self) -> None:
        """
        Establish a connection to the LDAP directory.

        This method loads the python-ldap module and connects to the directory.
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

            logger.debug("Connected to LDAP directory at {self.url}")
        except ImportError as err:
            def _ldap_not_found_error():
                return ImportError("python-ldap module not found")
            raise _ldap_not_found_error() from err
        except Exception as e:
            def _ldap_connection_error(err):
                return ConnectionError(
                    f"Failed to connect to LDAP directory: {str(err)}"
                )
            raise _ldap_connection_error(e) from e

    def disconnect(self) -> None:
        """
        Close the LDAP connection.
        """
        if self.connection:
            self.connection.unbind_s()
            self.connection = None
            logger.debug("Disconnected from LDAP directory at {self.url}")

    def search(
        self,
        base_dn: str,
        search_filter: str,
        attributes: Optional[list[str]] = None,
        scope: str = "subtree",
    ) -> list[tuple[str, dict[str, list[bytes]]]]:
        """
        Search the LDAP directory.

        Args:
            base_dn: Base DN for the search
            search_filter: LDAP search filter
            attributes: Attributes to return
            scope: Search scope (base, onelevel, subtree)

        Returns:
            List of (dn, attributes) tuples
        """
        if not self.connection:
            self.connect()

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
        return self.connection.search_s(
            base_dn,
            scope_value,
            search_filter,
            attributes,
        )
