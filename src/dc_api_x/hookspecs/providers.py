"""
Provider hook specifications for the DC-API-X plugin system.

This module defines the specifications for provider-related hooks that plugins can
implement to extend the functionality of DC-API-X.
"""

from .protocol import TRegistry, hookspec


class ProviderHookSpecs:
    """
    Hook specifications for providers in the DC-API-X plugin system.

    This class defines the specifications for hooks that plugins can implement
    to register custom providers for data, schemas, transformations, etc.
    """

    @hookspec
    def register_config_providers(self, registry: TRegistry) -> None:
        """
        Register configuration providers in the config provider registry.

        Plugins should implement this hook to register custom configuration providers.
        Each provider should be registered with a unique name as the key.

        Args:
            registry: The config provider registry to register providers in.
        """

    @hookspec
    def register_data_providers(self, registry: TRegistry) -> None:
        """
        Register data providers in the data provider registry.

        Plugins should implement this hook to register custom data providers.
        Each provider should be registered with a unique name as the key.

        Args:
            registry: The data provider registry to register providers in.
        """

    @hookspec
    def register_pagination_providers(self, registry: TRegistry) -> None:
        """
        Register pagination providers in the pagination provider registry.

        Plugins should implement this hook to register custom pagination providers.
        Each provider should be registered with a unique name as the key.

        Args:
            registry: The pagination provider registry to register providers in.
        """

    @hookspec
    def register_transform_providers(self, registry: TRegistry) -> None:
        """
        Register transform providers in the transform provider registry.

        Plugins should implement this hook to register custom transform providers.
        Each provider should be registered with a unique name as the key.

        Args:
            registry: The transform provider registry to register providers in.
        """
