"""
Data provider interfaces for DCApiX.

This module defines the DataProvider and BatchDataProvider abstract classes
for standardized data access.
"""

import abc
from typing import Any, Generic, Optional, TypeVar

from .protocol import Provider

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class DataProvider(Provider, Generic[T]):
    """
    Base interface for data providers.

    Data providers supply data from various sources in a standardized format.
    """

    @abc.abstractmethod
    def get(self, key: str, **kwargs: Any) -> Optional[T]:
        """
        Get a single item by key.

        Args:
            key: Item key
            **kwargs: Additional parameters

        Returns:
            Item or None if not found
        """

    @abc.abstractmethod
    def list(self, **kwargs: Any) -> list[T]:
        """
        List items matching criteria.

        Args:
            **kwargs: Filter criteria

        Returns:
            List of matching items
        """

    @abc.abstractmethod
    def create(self, data: T, **kwargs: Any) -> T:
        """
        Create a new item.

        Args:
            data: Item data
            **kwargs: Additional parameters

        Returns:
            Created item
        """

    @abc.abstractmethod
    def update(self, key: str, data: T, **kwargs: Any) -> T:
        """
        Update an existing item.

        Args:
            key: Item key
            data: New item data
            **kwargs: Additional parameters

        Returns:
            Updated item
        """

    @abc.abstractmethod
    def delete(self, key: str, **kwargs: Any) -> None:
        """
        Delete an item.

        Args:
            key: Item key
            **kwargs: Additional parameters
        """


class BatchDataProvider(DataProvider[T]):
    """
    Interface for data providers that support batch operations.
    """

    @abc.abstractmethod
    def batch_get(self, keys: list[str], **kwargs: Any) -> dict[str, T]:
        """
        Get multiple items by key.

        Args:
            keys: Item keys
            **kwargs: Additional parameters

        Returns:
            Dictionary of key to item
        """

    @abc.abstractmethod
    def batch_create(self, items: list[T], **kwargs: Any) -> list[T]:
        """
        Create multiple items.

        Args:
            items: Item data
            **kwargs: Additional parameters

        Returns:
            List of created items
        """

    @abc.abstractmethod
    def batch_update(self, items: dict[str, T], **kwargs: Any) -> dict[str, T]:
        """
        Update multiple items.

        Args:
            items: Dictionary of key to item data
            **kwargs: Additional parameters

        Returns:
            Dictionary of key to updated item
        """

    @abc.abstractmethod
    def batch_delete(self, keys: list[str], **kwargs: Any) -> None:
        """
        Delete multiple items.

        Args:
            keys: Item keys
            **kwargs: Additional parameters
        """
