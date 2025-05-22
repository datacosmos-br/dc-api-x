"""
Base protocol adapter for DCApiX.

This module defines the base ProtocolAdapter abstract class that all
specific protocol adapters must inherit from.
"""

import sys
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    ContextManager,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing import TypeAlias


T = TypeVar("T")
P = TypeVar("P")
R = TypeVar("R")


class Adapter(Protocol):
    """Base protocol for all adapters."""

    def connect(self) -> bool:
        """Connect to the underlying system.

        Returns:
            True if connection was successful, False otherwise
        """
        ...

    def disconnect(self) -> bool:
        """Disconnect from the underlying system.

        Returns:
            True if disconnection was successful, False otherwise
        """
        ...

    def is_connected(self) -> bool:
        """Check if the adapter is connected.

        Returns:
            True if connected, False otherwise
        """
        ...


class ProtocolAdapter(Adapter, Protocol):
    """Protocol adapter interface for communication protocols."""

    def set_option(self, name: str, value: Any) -> None:
        """Set an adapter option.

        Args:
            name: Option name
            value: Option value
        """
        ...


class ContextAdapter(Adapter, Protocol):
    """Context manager adapter interface."""

    def __enter__(self) -> "ContextAdapter":
        """Enter context manager.

        Returns:
            Self for use in context manager
        """
        ...

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context manager.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised

        Returns:
            Whether the exception was handled
        """
        ...


class AsyncContextAdapter(Adapter, Protocol):
    """Async context manager adapter interface."""

    async def __aenter__(self) -> "AsyncContextAdapter":
        """Enter async context manager.

        Returns:
            Self for use in async context manager
        """
        ...

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit async context manager.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised

        Returns:
            Whether the exception was handled
        """
        ...


class HttpAdapter(ProtocolAdapter, Protocol):
    """HTTP protocol adapter interface."""

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request data
            json: JSON data
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def get(
        self,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def post(
        self,
        url: str,
        *,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            url: Request URL
            data: Request data
            json: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def put(
        self,
        url: str,
        *,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a PUT request.

        Args:
            url: Request URL
            data: Request data
            json: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def delete(
        self,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a DELETE request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def patch(
        self,
        url: str,
        *,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a PATCH request.

        Args:
            url: Request URL
            data: Request data
            json: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...

    def head(
        self,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a HEAD request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout

        Returns:
            Response data
        """
        ...


ConnectionType: TypeAlias = Any  # Connection type


class Transaction(Protocol):
    """Database transaction protocol."""

    def commit(self) -> None:
        """Commit the transaction."""
        ...

    def rollback(self) -> None:
        """Rollback the transaction."""
        ...


class DatabaseTransaction(Transaction, ContextManager["DatabaseTransaction"]):
    """Database transaction with context manager support."""


class AsyncDatabaseTransaction(
    Transaction,
    AsyncContextManager["AsyncDatabaseTransaction"],
):
    """Async database transaction with async context manager support."""


class DatabaseAdapter(ProtocolAdapter, Protocol):
    """Database adapter protocol."""

    def execute_query(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Execute a query and return results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results as a list of dictionaries
        """
        ...

    def execute_write(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> int:
        """Execute a write query and return number of affected rows.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        ...

    def query_value(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Execute a query and return a single value.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Single value
        """
        ...

    def transaction(self) -> DatabaseTransaction:
        """Start a new transaction.

        Returns:
            Transaction object
        """
        ...


class AsyncDatabaseAdapter(DatabaseAdapter, Protocol):
    """Async database adapter protocol."""

    async def execute_query_async(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Execute a query asynchronously and return results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results
        """
        ...

    async def execute_write_async(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> int:
        """Execute a write query asynchronously and return number of affected rows.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        ...

    async def query_value_async(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Execute a query asynchronously and return a single value.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Single value
        """
        ...

    async def transaction_async(self) -> AsyncDatabaseTransaction:
        """Start a new async transaction.

        Returns:
            Async transaction object
        """
        ...


class DirectoryAdapter(ProtocolAdapter, Protocol):
    """Directory (LDAP) adapter protocol."""

    def search(
        self,
        base_dn: str,
        search_filter: str,
        attributes: Optional[list[str]] = None,
        scope: str = "subtree",
    ) -> list[dict[str, list[bytes]]]:
        """Search the directory.

        Args:
            base_dn: Base distinguished name
            search_filter: LDAP search filter
            attributes: Attributes to return
            scope: Search scope

        Returns:
            List of entries
        """
        ...

    def add(
        self,
        dn: str,
        attributes: dict[str, list[Union[str, bytes]]],
    ) -> bool:
        """Add an entry to the directory.

        Args:
            dn: Distinguished name
            attributes: Entry attributes

        Returns:
            True if successful, False otherwise
        """
        ...

    def modify(
        self,
        dn: str,
        attributes: dict[str, list[Union[str, bytes]]],
    ) -> bool:
        """Modify an entry in the directory.

        Args:
            dn: Distinguished name
            attributes: Attributes to modify

        Returns:
            True if successful, False otherwise
        """
        ...

    def delete(
        self,
        dn: str,
    ) -> bool:
        """Delete an entry from the directory.

        Args:
            dn: Distinguished name

        Returns:
            True if successful, False otherwise
        """
        ...


class FileSystemAdapter(ProtocolAdapter, Protocol):
    """File system adapter protocol."""

    def read_file(
        self,
        path: str,
        mode: str = "r",
    ) -> str:
        """Read a file.

        Args:
            path: File path
            mode: File mode

        Returns:
            File contents
        """
        ...

    def write_file(
        self,
        path: str,
        content: str,
        mode: str = "w",
    ) -> bool:
        """Write to a file.

        Args:
            path: File path
            content: File content
            mode: File mode

        Returns:
            True if successful, False otherwise
        """
        ...

    def delete_file(
        self,
        path: str,
    ) -> bool:
        """Delete a file.

        Args:
            path: File path

        Returns:
            True if successful, False otherwise
        """
        ...

    def file_exists(
        self,
        path: str,
    ) -> bool:
        """Check if a file exists.

        Args:
            path: File path

        Returns:
            True if file exists, False otherwise
        """
        ...

    def list_directory(
        self,
        path: str,
    ) -> list[str]:
        """List directory contents.

        Args:
            path: Directory path

        Returns:
            List of file/directory names
        """
        ...

    def create_directory(
        self,
        path: str,
    ) -> bool:
        """Create a directory.

        Args:
            path: Directory path

        Returns:
            True if successful, False otherwise
        """
        ...


class MessageQueueAdapter(ProtocolAdapter, Protocol):
    """Message queue adapter protocol."""

    def send_message(
        self,
        queue: str,
        message: Any,
        *,
        attributes: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Send a message to a queue.

        Args:
            queue: Queue name
            message: Message content
            attributes: Message attributes

        Returns:
            True if successful, False otherwise
        """
        ...

    def receive_message(
        self,
        queue: str,
        *,
        timeout: Optional[int] = None,
    ) -> Optional[dict[str, Any]]:
        """Receive a message from a queue.

        Args:
            queue: Queue name
            timeout: Receive timeout

        Returns:
            Message or None if no message is available
        """
        ...

    def delete_message(
        self,
        queue: str,
        receipt_handle: str,
    ) -> bool:
        """Delete a message from a queue.

        Args:
            queue: Queue name
            receipt_handle: Message receipt handle

        Returns:
            True if successful, False otherwise
        """
        ...


class CacheAdapter(ProtocolAdapter, Protocol):
    """Cache adapter protocol."""

    def get(
        self,
        key: str,
    ) -> Any:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        ...

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        ...

    def delete(
        self,
        key: str,
    ) -> bool:
        """Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        ...

    def exists(
        self,
        key: str,
    ) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        ...


class GraphQLAdapter(ProtocolAdapter, Protocol):
    """GraphQL adapter protocol."""

    def query(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query
            variables: Query variables
            operation_name: Operation name

        Returns:
            Query result
        """
        ...

    def mutation(
        self,
        mutation: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL mutation.

        Args:
            mutation: GraphQL mutation
            variables: Mutation variables
            operation_name: Operation name

        Returns:
            Mutation result
        """
        ...


class WebSocketAdapter(ProtocolAdapter, Protocol):
    """WebSocket adapter protocol."""

    def send(
        self,
        message: str,
    ) -> bool:
        """Send a message.

        Args:
            message: Message to send

        Returns:
            True if successful, False otherwise
        """
        ...

    def receive(
        self,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Receive a message.

        Args:
            timeout: Receive timeout

        Returns:
            Received message or None if no message is available
        """
        ...

    def subscribe(
        self,
        topic: str,
    ) -> bool:
        """Subscribe to a topic.

        Args:
            topic: Topic to subscribe to

        Returns:
            True if successful, False otherwise
        """
        ...

    def unsubscribe(
        self,
        topic: str,
    ) -> bool:
        """Unsubscribe from a topic.

        Args:
            topic: Topic to unsubscribe from

        Returns:
            True if successful, False otherwise
        """
        ...
