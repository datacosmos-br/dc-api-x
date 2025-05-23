"""
Plugin management for DCApiX.

This module provides functions for discovering, loading, and managing plugins
for extending DCApiX functionality.
"""

import logging
from importlib import metadata
from typing import Any, Optional

import pluggy

from .hookspecs.hookspecs import HookSpecs

logger = logging.getLogger(__name__)

# Create the plugin manager
pm = pluggy.PluginManager("dc_api_x")
pm.add_hookspecs(HookSpecs)

# Registries for adapters and providers
adapter_registry: dict[str, Any] = {}
auth_provider_registry: dict[str, Any] = {}
schema_provider_registry: dict[str, Any] = {}
request_hook_registry: dict[str, Any] = {}
response_hook_registry: dict[str, Any] = {}
error_hook_registry: dict[str, Any] = {}


class PluginState:
    """Class to manage plugin loading state."""

    def __init__(self):
        """Initialize the plugin state."""
        self.plugins_loaded = False

    def set_loaded(self, loaded: bool = True) -> None:
        """Set the loaded state of plugins."""
        self.plugins_loaded = loaded

    def is_loaded(self) -> bool:
        """Check if plugins have been loaded."""
        return self.plugins_loaded


# Plugin state manager
_plugin_state = PluginState()


def enable_plugins() -> None:
    """
    Enable and load all available plugins.

    This function discovers and loads all plugins registered via entry points.
    It should be called before using any plugins.
    """
    if _plugin_state.is_loaded():
        logger.debug("Plugins already loaded")
        return

    load_plugins()
    _plugin_state.set_loaded(True)


def load_plugins() -> list[str]:
    """
    Discover and load all available plugins.

    Returns:
        List of loaded plugin names
    """
    loaded_plugins = []

    try:
        # Discover plugins from entry points
        for entry_point in metadata.entry_points(group="dc_api_x.plugins"):
            plugin_name = entry_point.name

            try:
                plugin = entry_point.load()
                pm.register(plugin)
                loaded_plugins.append(plugin_name)
                logger.info("Loaded plugin: %s", plugin_name)
            except (ImportError, AttributeError):
                logger.exception("Error loading plugin %s", plugin_name)
            except Exception:
                logger.exception("Error loading plugin %s", plugin_name)

    except (ImportError, ValueError):
        logger.exception("Error discovering plugins")
    except Exception:
        logger.exception("Error discovering plugins")

    # Check for any pending hooks
    pm.check_pending()

    # Call hook implementations to register adapters and providers
    pm.hook.register_adapters(registry=adapter_registry)
    pm.hook.register_auth_providers(registry=auth_provider_registry)
    pm.hook.register_schema_providers(registry=schema_provider_registry)
    pm.hook.register_request_hooks(registry=request_hook_registry)
    pm.hook.register_response_hooks(registry=response_hook_registry)
    pm.hook.register_error_hooks(registry=error_hook_registry)

    return loaded_plugins


def get_adapter(name: str) -> Optional[Any]:
    """
    Get a registered adapter by name.

    Args:
        name: Name of the adapter

    Returns:
        Adapter class or None if not found
    """
    return adapter_registry.get(name)


def get_auth_provider(name: str) -> Optional[Any]:
    """
    Get a registered authentication provider by name.

    Args:
        name: Name of the auth provider

    Returns:
        Auth provider class or None if not found
    """
    return auth_provider_registry.get(name)


def get_schema_provider(name: str) -> Optional[Any]:
    """
    Get a registered schema provider by name.

    Args:
        name: Name of the schema provider

    Returns:
        Schema provider class or None if not found
    """
    return schema_provider_registry.get(name)


def get_request_hook(name: str) -> Optional[Any]:
    """
    Get a registered request hook by name.

    Args:
        name: Name of the request hook

    Returns:
        Request hook class or None if not found
    """
    return request_hook_registry.get(name)


def get_response_hook(name: str) -> Optional[Any]:
    """
    Get a registered response hook by name.

    Args:
        name: Name of the response hook

    Returns:
        Response hook class or None if not found
    """
    return response_hook_registry.get(name)


def get_error_hook(name: str) -> Optional[Any]:
    """
    Get a registered error hook by name.

    Args:
        name: Name of the error hook

    Returns:
        Error hook class or None if not found
    """
    return error_hook_registry.get(name)


def list_adapters() -> list[str]:
    """
    List all registered adapters.

    Returns:
        List of adapter names
    """
    return list(adapter_registry.keys())


def list_auth_providers() -> list[str]:
    """
    List all registered authentication providers.

    Returns:
        List of auth provider names
    """
    return list(auth_provider_registry.keys())


def list_schema_providers() -> list[str]:
    """
    List all registered schema providers.

    Returns:
        List of schema provider names
    """
    return list(schema_provider_registry.keys())
