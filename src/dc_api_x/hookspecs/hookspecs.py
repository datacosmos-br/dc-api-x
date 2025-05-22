"""
Core hook specifications for the DC-API-X plugin system.

This module defines the specifications for hooks that plugins can implement to
extend the functionality of DC-API-X. The hook specifications define the
contract that plugins must adhere to.
"""

from typing import Any, TypeVar

import pluggy

# Hook specification marker
hookspec = pluggy.HookspecMarker("dc_api_x")

# Type for registries that store adapters, providers, etc.
TRegistry = dict[str, Any]
TAdapter = TypeVar("TAdapter")
TAuthProvider = TypeVar("TAuthProvider")
TSchemaProvider = TypeVar("TSchemaProvider")


class HookSpecs:
    """
    Hook specifications for the DC-API-X plugin system.

    This class defines the specifications for hooks that plugins can implement.
    Each method in this class is a hook specification that plugins can implement
    to extend DC-API-X functionality.
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

    @hookspec
    def register_request_hooks(self, registry: TRegistry) -> None:
        """
        Register request hooks in the request hook registry.

        Plugins should implement this hook to register custom request hooks.
        Each hook should be registered with a unique name as the key.

        Args:
            registry: The request hook registry to register hooks in.
        """

    @hookspec
    def register_response_hooks(self, registry: TRegistry) -> None:
        """
        Register response hooks in the response hook registry.

        Plugins should implement this hook to register custom response hooks.
        Each hook should be registered with a unique name as the key.

        Args:
            registry: The response hook registry to register hooks in.
        """

    @hookspec
    def register_error_hooks(self, registry: TRegistry) -> None:
        """
        Register error hooks in the error hook registry.

        Plugins should implement this hook to register custom error hooks.
        Each hook should be registered with a unique name as the key.

        Args:
            registry: The error hook registry to register hooks in.
        """
