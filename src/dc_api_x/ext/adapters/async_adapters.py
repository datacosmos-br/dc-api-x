"""
Async adapters for DCApiX.

This module defines abstract classes for asynchronous adapters.
"""

import abc
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any, Optional, TypeVar

from ...exceptions import AdapterError
from .protocol import AsyncDatabaseAdapter, AsyncDatabaseTransaction, ProtocolAdapter

T = TypeVar("T")


class AsyncAdapter(ProtocolAdapter):
    """
    Base interface for asynchronous adapters.

    This interface defines the common methods that all async adapters
    should implement for asynchronous connection handling.
    """

    @abc.abstractmethod
    async def aconnect(self) -> bool:
        """
        Asynchronously establish a connection to the resource.

        This method is called when initializing the adapter and should
        establish any necessary connections.

        Returns:
            True if connection was successful, False otherwise
        """

    @abc.abstractmethod
    async def adisconnect(self) -> bool:
        """
        Asynchronously close the connection to the resource.

        This method is called when shutting down the adapter and should
        clean up any resources.

        Returns:
            True if disconnection was successful, False otherwise
        """

    @abc.abstractmethod
    async def ais_connected(self) -> bool:
        """
        Asynchronously check if the adapter is connected.

        Returns:
            True if connected, False otherwise
        """

    def connect(self) -> bool:
        """
        Sync wrapper for aconnect.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call connect() on AsyncAdapter. Use await adapter.aconnect() instead.",
        )

    def disconnect(self) -> bool:
        """
        Sync wrapper for adisconnect.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call disconnect() on AsyncAdapter. Use await adapter.adisconnect() instead.",
        )

    def is_connected(self) -> bool:
        """
        Sync wrapper for ais_connected.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call is_connected() on AsyncAdapter. Use await adapter.ais_connected() instead.",
        )


class AsyncHttpAdapter(AsyncAdapter):
    """Base interface for asynchronous HTTP adapters."""

    @abc.abstractmethod
    async def arequest(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, Any], bytes]:
        """
        Make an asynchronous HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Tuple of (status_code, headers, body)
        """

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, Any], bytes]:
        """
         return None  # Implement this method

        Sync wrapper for arequest.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call request() on AsyncHttpAdapter. Use await adapter.arequest() instead.",
        )


class AsyncAdapterMixin:
    """Mixin for async adapters."""

    async def connect_async(self) -> bool:
        """Connect asynchronously to the resource.

        Returns:
            True if the connection was successful, False otherwise
        """
        raise NotImplementedError("Async connect not implemented")

    async def disconnect_async(self) -> bool:
        """Disconnect asynchronously from the resource.

        Returns:
            True if the disconnection was successful, False otherwise
        """
        raise NotImplementedError("Async disconnect not implemented")

    async def is_connected_async(self) -> bool:
        """Check if the adapter is connected asynchronously.

        Returns:
            True if connected, False otherwise
        """
        raise NotImplementedError("Async is_connected not implemented")

    async def __aenter__(self) -> "AsyncAdapterMixin":
        """Enter async context manager.

        Returns:
            Self for use in async context manager
        """
        await self.connect_async()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context manager.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        await self.disconnect_async()


class AsyncDatabaseTransactionImpl(AsyncDatabaseTransaction):
    """Implementation of an async database transaction."""

    def __init__(self, conn: Any, adapter: AsyncDatabaseAdapter) -> None:
        """Initialize the transaction.

        Args:
            conn: Database connection
            adapter: Database adapter
        """
        self.conn = conn
        self.adapter = adapter
        if self is not None:
            self.transaction = None
        else:
            # Handle None case appropriately
            pass  # TODO: Implement proper None handling

    async def __aenter__(self) -> "AsyncDatabaseTransactionImpl":
        """Enter async context manager.

        Returns:
            Self for use in async context manager
        """
        self.transaction = await self.conn.begin()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context manager.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if exc_type is not None:
            if self.transaction:
                await self.transaction.rollback()
        elif self.transaction:
            await self.transaction.commit()

    def commit(self) -> None:
        """Commit the transaction synchronously.

        This method should not be called directly on async transactions.
        Use await transaction.commit_async() instead.
        """
        raise NotImplementedError(
            "Cannot call commit() on AsyncDatabaseTransaction. Use await transaction.commit_async() instead.",
        )

    def rollback(self) -> None:
        """Rollback the transaction synchronously.

        This method should not be called directly on async transactions.
        Use await transaction.rollback_async() instead.
        """
        raise NotImplementedError(
            "Cannot call rollback() on AsyncDatabaseTransaction. Use await transaction.rollback_async() instead.",
        )

    async def commit_async(self) -> None:
        """Commit the transaction asynchronously."""
        if self.transaction:
            await self.transaction.commit()
            if self is not None:
                self.transaction = None
            else:
                # Handle None case appropriately
                pass  # TODO: Implement proper None handling

    async def rollback_async(self) -> None:
        """Rollback the transaction asynchronously."""
        if self.transaction:
            await self.transaction.rollback()
            if self is not None:
                self.transaction = None
            else:
                # Handle None case appropriately
                pass  # TODO: Implement proper None handling


@asynccontextmanager
async def async_transaction(
    adapter: AsyncDatabaseAdapter,
) -> AsyncIterator[AsyncDatabaseTransaction]:
    """Context manager for an async transaction.

    Args:
        adapter: Database adapter

    Yields:
        AsyncDatabaseTransaction: Transaction object
    """
    if not adapter.is_connected():
        await adapter.connect_async()

    transaction = await adapter.transaction_async()
    try:
        yield transaction
    except Exception as e:
        await transaction.rollback_async()  # Use rollback_async instead of rollback
        error_msg = f"Transaction error: {str(e)}"
        raise AdapterError(error_msg) from e
    finally:
        if transaction:
            # Ensure the transaction is closed if it wasn't committed or rolled back
            try:
                await transaction.rollback_async()  # Use rollback_async instead of rollback
            except (RuntimeError, AttributeError) as e:
                # Log the error instead of silently passing
                logging.getLogger(__name__).debug(
                    "Failed to rollback transaction during cleanup: %s",
                    str(e),
                )


class AsyncDatabaseAdapterImpl(AsyncDatabaseAdapter):
    """Base implementation of AsyncDatabaseAdapter."""

    async def connect_async(self) -> bool:
        """Connect asynchronously to the database.

        This is a default implementation that delegates to aconnect.
        Subclasses should override this method.

        Returns:
            True if connected successfully, False otherwise
        """
        return False  # Subclasses should override this method

    async def disconnect_async(self) -> bool:
        """Disconnect asynchronously from the database.

        This is a default implementation that delegates to adisconnect.
        Subclasses should override this method.

        Returns:
            True if disconnected successfully, False otherwise
        """
        return False  # Subclasses should override this method

    async def is_connected_async(self) -> bool:
        """Check if connected asynchronously.

        This is a default implementation that delegates to ais_connected.
        Subclasses should override this method.

        Returns:
            True if connected, False otherwise
        """
        return False  # Subclasses should override this method
