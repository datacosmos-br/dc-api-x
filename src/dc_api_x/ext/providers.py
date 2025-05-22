"""
Provider interfaces for DCApiX.

This module defines provider interfaces for data and schemas that can be
implemented by external packages.
"""

import abc
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class DataProvider(abc.ABC, Generic[T]):
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


class SchemaProvider(abc.ABC):
    """
    Base interface for schema providers.

    Schema providers supply schema information for data structures.
    """

    @abc.abstractmethod
    def get_schema(self, name: str) -> dict[str, Any]:
        """
        Get a schema by name.

        Args:
            name: Schema name

        Returns:
            Schema definition
        """

    @abc.abstractmethod
    def list_schemas(self) -> list[str]:
        """
        List available schemas.

        Returns:
            List of schema names
        """

    @abc.abstractmethod
    def validate(self, name: str, data: Any) -> list[str]:
        """
        Validate data against a schema.

        Args:
            name: Schema name
            data: Data to validate

        Returns:
            List of validation errors (empty if valid)
        """


class TransformProvider(abc.ABC, Generic[T, V]):
    """
    Base interface for transform providers.

    Transform providers convert data between different formats or schemas.
    """

    @abc.abstractmethod
    def transform(self, data: T, **kwargs: Any) -> V:
        """
        Transform data from one format to another.

        Args:
            data: Input data
            **kwargs: Transform parameters

        Returns:
            Transformed data
        """

    @abc.abstractmethod
    def batch_transform(self, items: list[T], **kwargs: Any) -> list[V]:
        """
        Transform multiple items.

        Args:
            items: Input items
            **kwargs: Transform parameters

        Returns:
            Transformed items
        """


class ConfigProvider(abc.ABC):
    """
    Base interface for configuration providers.

    Configuration providers supply configuration values from various sources.
    """

    @abc.abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """

    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """

    @abc.abstractmethod
    def load(self, source: Any) -> None:
        """
        Load configuration from a source.

        Args:
            source: Configuration source
        """

    @abc.abstractmethod
    def save(self, destination: Any) -> None:
        """
        Save configuration to a destination.

        Args:
            destination: Configuration destination
        """
