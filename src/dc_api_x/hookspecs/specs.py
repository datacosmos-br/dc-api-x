"""
Adapter hook specifications for the DCApiX plugin system.

This module defines the specifications for adapter-related hooks that plugins can
implement to extend the functionality of DCApiX.
"""

from .protocol import TRegistry, hookspec


class AdapterHookSpecs:
    """
    Hook specifications for adapters in the DCApiX plugin system.

    This class defines the specifications for hooks that plugins can implement
    to register custom adapters and related components.
    """

    @hookspec
    def register_adapters(self, registry: TRegistry) -> None:
        """
        Register protocol adapters in the adapter registry.

        Plugins should implement this hook to register custom protocol adapters.
        Each adapter should be registered with a unique name as the key.

        Args:
            registry: The adapter registry to register adapters in.
        """

    @hookspec
    def register_auth_providers(self, registry: TRegistry) -> None:
        """
        Register authentication providers in the auth provider registry.

        Plugins should implement this hook to register custom authentication
        providers. Each provider should be registered with a unique name as the key.

        Args:
            registry: The auth provider registry to register providers in.
        """

    @hookspec
    def register_schema_providers(self, registry: TRegistry) -> None:
        """
        Register schema providers in the schema provider registry.

        Plugins should implement this hook to register custom schema providers.
        Each provider should be registered with a unique name as the key.

        Args:
            registry: The schema provider registry to register providers in.
        """
