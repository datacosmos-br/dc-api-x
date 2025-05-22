"""
Database adapter for DCApiX.

This module defines the DatabaseAdapter abstract class for database operations.
"""

import abc
from typing import Any, Generic, Optional, TypeVar

from .protocol import ProtocolAdapter

T = TypeVar("T")


class DatabaseTransaction(abc.ABC):
    """Database transaction interface."""

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Roll back the transaction."""

    def __enter__(self) -> "DatabaseTransaction":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Exit context manager."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()


class DatabaseAdapter(ProtocolAdapter, Generic[T]):
    """Base interface for database adapters."""

    @abc.abstractmethod
    def execute(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[T]:
        """
        Execute a database query.

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            Query results
        """

    @abc.abstractmethod
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

    @abc.abstractmethod
    def transaction(self) -> DatabaseTransaction:
        """
        Start a transaction.

        Returns:
            Transaction object
        """
