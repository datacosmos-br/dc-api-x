"""
Async adapters for DCApiX.

This module defines abstract classes for asynchronous adapters.
"""

import abc
from typing import Any, Generic, Optional, TypeVar, Type

from .protocol import ProtocolAdapter

T = TypeVar("T")


class AsyncAdapter(ProtocolAdapter):
    """
    Base interface for asynchronous adapters.

    This interface defines the common methods that all async adapters
    should implement for asynchronous connection handling.
    """

    @abc.abstractmethod
    async def aconnect(self) -> None:
        """
        Asynchronously establish a connection to the resource.

        This method is called when initializing the adapter and should
        establish any necessary connections.
        """

    @abc.abstractmethod
    async def adisconnect(self) -> None:
        """
        Asynchronously close the connection to the resource.

        This method is called when shutting down the adapter and should
        clean up any resources.
        """

    @abc.abstractmethod
    async def ais_connected(self) -> bool:
        """
        Asynchronously check if the adapter is connected.

        Returns:
            True if connected, False otherwise
        """

    def connect(self) -> None:
        """
        Sync wrapper for aconnect.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call connect() on AsyncAdapter. Use await adapter.aconnect() instead.",
        )

    def disconnect(self) -> None:
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
        Sync wrapper for arequest.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call request() on AsyncHttpAdapter. Use await adapter.arequest() instead.",
        )


class AsyncDatabaseTransaction(abc.ABC):
    """Asynchronous database transaction interface."""

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the transaction asynchronously."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Roll back the transaction asynchronously."""

    async def __aenter__(self) -> "AsyncDatabaseTransaction":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """Exit async context manager."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()


class AsyncDatabaseAdapter(AsyncAdapter, Generic[T]):
    """Base interface for asynchronous database adapters."""

    @abc.abstractmethod
    async def aexecute(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[T]:
        """
        Execute a database query asynchronously.

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            Query results
        """

    @abc.abstractmethod
    async def aexecute_write(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Execute a write operation asynchronously.

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            Number of affected rows
        """

    @abc.abstractmethod
    async def atransaction(self) -> AsyncDatabaseTransaction:
        """
        Start a transaction asynchronously.

        Returns:
            Async transaction object
        """

    def execute(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[T]:
        """
        Sync wrapper for aexecute.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call execute() on AsyncDatabaseAdapter. Use await adapter.aexecute() instead.",
        )

    def execute_write(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Sync wrapper for aexecute_write.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call execute_write() on AsyncDatabaseAdapter. Use await adapter.aexecute_write() instead.",
        )

    def transaction(self) -> "AsyncDatabaseTransaction":
        """
        Sync wrapper for atransaction.

        Raises:
            NotImplementedError: This method should not be called directly
                on async adapters.
        """
        raise NotImplementedError(
            "Cannot call transaction() on AsyncDatabaseAdapter. Use await adapter.atransaction() instead.",
        )
