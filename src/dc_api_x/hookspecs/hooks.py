"""
Hook specifications for the DC-API-X hooks system.

This module defines the specifications for hooks that plugins can implement
to register custom request, response, and error hooks.
"""

from .protocol import TRegistry, hookspec


class HookHookSpecs:
    """
    Hook specifications for the hooks system in DC-API-X.

    This class defines the specifications for hooks that plugins can implement
    to register custom request, response, and error hooks.
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

    @hookspec
    def register_api_response_hooks(self, registry: TRegistry) -> None:
        """
        Register API response hooks in the API response hook registry.

        Plugins should implement this hook to register custom API response hooks.
        Each hook should be registered with a unique name as the key.

        Args:
            registry: The API response hook registry to register hooks in.
        """
