"""
Adapter implementations for DCApiX.

This module provides concrete implementations of the adapter interfaces.
"""

import importlib
import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

from ..ext.adapters import (
    DatabaseAdapter,
    DatabaseTransaction,
    DirectoryAdapter,
    HttpAdapter,
)
from ..ext.auth import AuthProvider, BasicAuthProvider

logger = logging.getLogger(__name__)


class RequestsHttpAdapter(HttpAdapter):
    """
    HTTP adapter implementation using the requests library.

    This adapter serves as the default HTTP implementation when no
    other adapter is specified.
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
            max_retries: Maximum number of retry attempts
            retry_backoff: Exponential backoff factor for retries
            auth_provider: Authentication provider
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.auth_provider = auth_provider
        self.session = None

    def connect(self) -> None:
        """
        Establish a connection to the resource.

        This method initializes the requests session with the appropriate
        configuration and authenticates if necessary.
        """
        self.session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Configure default headers
        self.session.headers.update(
            {
                "Content-type": "application/json",
                "Accept": "application/json",
                "User-Agent": "DCApiX/0.1.0",
            },
        )

        # Configure authentication if provided
        if self.auth_provider:
            self.auth_provider.authenticate()
            if isinstance(self.auth_provider, BasicAuthProvider):
                self.session.auth = HTTPBasicAuth(
                    self.auth_provider.username,
                    self.auth_provider.password,
                )
            elif hasattr(self.auth_provider, "get_auth_headers"):
                auth_headers = self.auth_provider.get_auth_headers()
                if auth_headers:
                    self.session.headers.update(auth_headers)

    def disconnect(self) -> None:
        """
        Close the connection.

        This method closes the requests session.
        """
        if self.session:
            self.session.close()
            self.session = None

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, str], bytes]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to requests

        Returns:
            Tuple of (status_code, headers, content)

        Raises:
            ConnectionError: If connection fails
            TimeoutError: If request times out
            RequestError: If request fails
        """
        if not self.session:
            self.connect()

        # Refresh authentication if needed
        if (
            self.auth_provider
            and self.auth_provider.is_authenticated()
            and not self.auth_provider.is_token_valid()
        ):
            self.auth_provider.authenticate()
            if hasattr(self.auth_provider, "get_auth_headers"):
                auth_headers = self.auth_provider.get_auth_headers()
                if auth_headers:
                    self.session.headers.update(auth_headers)

        # Add timeout and SSL verification
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify_ssl)

        # Make the request
        response = self.session.request(method, url, **kwargs)

        # Return status code, headers, and content
        return (
            response.status_code,
            dict(response.headers),
            response.content,
        )


class DatabaseTransactionImpl(DatabaseTransaction):
    """
    Implementation of a database transaction using a connection.
    """

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
        """
        Enter the transaction context.

        Returns:
            Transaction object
        """
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the transaction context.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None

        if exc_type is None and self.autocommit:
            self.connection.commit()
        elif exc_type is not None:
            self.connection.rollback()

    def execute(self, query: str, params: Optional[dict[str, Any]] = None) -> Any:
        """
        Execute a query within the transaction.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Cursor object
        """
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    def fetchall(self) -> list[dict[str, Any]]:
        """
        Fetch all rows from the last query.

        Returns:
            List of rows as dictionaries
        """
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in self.cursor.fetchall()]

    def fetchone(self) -> Optional[dict[str, Any]]:
        """
        Fetch one row from the last query.

        Returns:
            Row as dictionary or None
        """
        row = self.cursor.fetchone()
        if row:
            columns = [col[0] for col in self.cursor.description]
            return dict(zip(columns, row, strict=False))
        return None

    def commit(self) -> None:
        """
        Commit the transaction.
        """
        self.connection.commit()

    def rollback(self) -> None:
        """
        Rollback the transaction.
        """
        self.connection.rollback()


class GenericDatabaseAdapter(DatabaseAdapter):
    """
    Generic database adapter that can work with various database libraries.

    This adapter dynamically loads the appropriate database library
    based on the connection string.
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
            driver: Database driver to use (default: sqlite3)
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
            raise ImportError(f"Database driver {self.driver} not found") from err
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}") from e

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
            raise ImportError("python-ldap module not found") from err
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to LDAP directory: {str(e)}",
            ) from e

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
