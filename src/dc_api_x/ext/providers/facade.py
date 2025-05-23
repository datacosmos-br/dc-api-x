"""
Provider facade for DCApiX.

This module provides a simplified interface for working with providers,
following the facade design pattern.
"""

from typing import Any, Optional, TypeVar

from .config import ConfigProvider
from .data import DataProvider
from .pagination import PaginationProvider
from .schema import SchemaProvider
from .transform import TransformProvider

T = TypeVar("T")
V = TypeVar("V")


class ProviderManager:
    """
    Facade for managing and registering providers.

    This class provides a simplified interface for registering and
    managing different types of providers.
    """

    def __init__(self) -> None:
        """Initialize the provider manager with empty provider registries."""
        self._data_providers: dict[str, DataProvider[Any]] = {}
        self._schema_providers: dict[str, SchemaProvider] = {}
        self._transform_providers: dict[str, TransformProvider[Any, Any]] = {}
        self._config_providers: dict[str, ConfigProvider] = {}
        self._pagination_providers: dict[str, PaginationProvider[Any]] = {}

    def register_data_provider(self, name: str, provider: DataProvider[T]) -> None:
        """
        Register a data provider.

        Args:
            name: Provider name
            provider: Data provider instance
        """
        self._data_providers[name] = provider

    def register_schema_provider(self, name: str, provider: SchemaProvider) -> None:
        """
        Register a schema provider.

        Args:
            name: Provider name
            provider: Schema provider instance
        """
        self._schema_providers[name] = provider

    def register_transform_provider(
        self,
        name: str,
        provider: TransformProvider[Any, Any],
    ) -> None:
        """
        Register a transform provider.

        Args:
            name: Provider name
            provider: Transform provider instance
        """
        self._transform_providers[name] = provider

    def register_config_provider(self, name: str, provider: ConfigProvider) -> None:
        """
        Register a configuration provider.

        Args:
            name: Provider name
            provider: Config provider instance
        """
        self._config_providers[name] = provider

    def register_pagination_provider(
        self,
        name: str,
        provider: PaginationProvider[T],
    ) -> None:
        """
        Register a pagination provider.

        Args:
            name: Provider name
            provider: Pagination provider instance
        """
        self._pagination_providers[name] = provider

    def get_data_provider(self, name: str) -> Optional[DataProvider[Any]]:
        """
        Get a data provider by name.

        Args:
            name: Provider name

        Returns:
            Data provider or None if not found
        """
        return self._data_providers.get(name)

    def get_schema_provider(self, name: str) -> Optional[SchemaProvider]:
        """
        Get a schema provider by name.

        Args:
            name: Provider name

        Returns:
            Schema provider or None if not found
        """
        return self._schema_providers.get(name)

    def get_transform_provider(
        self,
        name: str,
    ) -> Optional[TransformProvider[Any, Any]]:
        """
        Get a transform provider by name.

        Args:
            name: Provider name

        Returns:
            Transform provider or None if not found
        """
        return self._transform_providers.get(name)

    def get_config_provider(self, name: str) -> Optional[ConfigProvider]:
        """
        Get a configuration provider by name.

        Args:
            name: Provider name

        Returns:
            Config provider or None if not found
        """
        return self._config_providers.get(name)

    def get_pagination_provider(self, name: str) -> Optional[PaginationProvider[Any]]:
        """
        Get a pagination provider by name.

        Args:
            name: Provider name

        Returns:
            Pagination provider or None if not found
        """
        return self._pagination_providers.get(name)

    def initialize_all(self) -> None:
        """Initialize all registered providers."""
        provider_dicts: list[dict[str, Any]] = [
            self._data_providers,
            self._schema_providers,
            self._transform_providers,
            self._config_providers,
            self._pagination_providers,
        ]
        for provider_dict in provider_dicts:
            for provider in list(provider_dict.values()):
                provider.initialize()

    def shutdown_all(self) -> None:
        """Shutdown all registered providers."""
        provider_dicts: list[dict[str, Any]] = [
            self._data_providers,
            self._schema_providers,
            self._transform_providers,
            self._config_providers,
            self._pagination_providers,
        ]
        for provider_dict in provider_dicts:
            for provider in list(provider_dict.values()):
                provider.shutdown()


# Factory functions for creating common providers


def create_data_provider(provider_type: str, **kwargs: Any) -> DataProvider[Any]:
    """
    Create a data provider of the specified type.

    Args:
        provider_type: Type of data provider to create
        **kwargs: Provider-specific configuration

    Returns:
        Data provider instance

    Raises:
        ValueError: If the provider type is not supported
    """
    # This would be implemented with a registry of provider factories
    raise NotImplementedError(f"Provider type '{provider_type}' not supported")


def create_schema_provider(provider_type: str, **kwargs: Any) -> SchemaProvider:
    """
    Create a schema provider of the specified type.

    Args:
        provider_type: Type of schema provider to create
        **kwargs: Provider-specific configuration

    Returns:
        Schema provider instance

    Raises:
        ValueError: If the provider type is not supported
    """
    # This would be implemented with a registry of provider factories
    raise NotImplementedError(f"Provider type '{provider_type}' not supported")
