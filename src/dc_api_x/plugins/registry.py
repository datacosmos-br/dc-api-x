"""
Plugin registry for DCApiX.

This module provides functions for discovering and loading plugins.
"""

import importlib
import inspect
import logging
import pkgutil
from importlib import metadata
from typing import Any, Optional, TypeVar, cast

import pluggy

from dc_api_x.hookspecs import HookSpecs

from .base import _PLUGINS, ApiPlugin

P = TypeVar("P", bound=ApiPlugin)

logger = logging.getLogger(__name__)

# Create the plugin manager
pm = pluggy.PluginManager("dc_api_x")
pm.add_hookspecs(HookSpecs)

# Registries for adapters and providers
adapter_registry: dict[str, Any] = {}
auth_provider_registry: dict[str, Any] = {}
schema_provider_registry: dict[str, Any] = {}
config_provider_registry: dict[str, Any] = {}
data_provider_registry: dict[str, Any] = {}
pagination_provider_registry: dict[str, Any] = {}
transform_provider_registry: dict[str, Any] = {}
request_hook_registry: dict[str, Any] = {}
response_hook_registry: dict[str, Any] = {}
error_hook_registry: dict[str, Any] = {}
api_response_hook_registry: dict[str, Any] = {}


class PluginState:
    """Class to manage plugin loading state."""

    def __init__(self) -> None:
        """Initialize the plugin state."""
        self.plugins_loaded = False

    def set_loaded(self, *, loaded: bool = True) -> None:
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
    _plugin_state.set_loaded(loaded=True)


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

    # Add calls for the missing provider hooks
    pm.hook.register_config_providers(registry=config_provider_registry)
    pm.hook.register_data_providers(registry=data_provider_registry)
    pm.hook.register_pagination_providers(registry=pagination_provider_registry)
    pm.hook.register_transform_providers(registry=transform_provider_registry)

    # Register hook implementations
    pm.hook.register_request_hooks(registry=request_hook_registry)
    pm.hook.register_response_hooks(registry=response_hook_registry)
    pm.hook.register_error_hooks(registry=error_hook_registry)
    pm.hook.register_api_response_hooks(registry=api_response_hook_registry)

    return loaded_plugins


def get_plugin(name: str) -> Optional[type[ApiPlugin]]:
    """
    Get a plugin class by name.

    Args:
        name: Name of the plugin class

    Returns:
        Plugin class or None if not found
    """
    return _PLUGINS.get(name)


def get_plugin_by_type(plugin_type: type[P]) -> Optional[type[P]]:
    """
    Get a plugin class by type.

    Args:
        plugin_type: Type of the plugin class

    Returns:
        Plugin class or None if not found
    """
    for plugin_class in _PLUGINS.values():
        if issubclass(plugin_class, plugin_type):
            return cast(type[P], plugin_class)
    return None


def list_plugins() -> list[type[ApiPlugin]]:
    """
    List all registered plugins.

    Returns:
        List of plugin classes
    """
    return list(_PLUGINS.values())


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


def get_config_provider(name: str) -> Optional[Any]:
    """
    Get a registered configuration provider by name.

    Args:
        name: Name of the config provider

    Returns:
        Config provider class or None if not found
    """
    return config_provider_registry.get(name)


def get_data_provider(name: str) -> Optional[Any]:
    """
    Get a registered data provider by name.

    Args:
        name: Name of the data provider

    Returns:
        Data provider class or None if not found
    """
    return data_provider_registry.get(name)


def get_pagination_provider(name: str) -> Optional[Any]:
    """
    Get a registered pagination provider by name.

    Args:
        name: Name of the pagination provider

    Returns:
        Pagination provider class or None if not found
    """
    return pagination_provider_registry.get(name)


def get_transform_provider(name: str) -> Optional[Any]:
    """
    Get a registered transform provider by name.

    Args:
        name: Name of the transform provider

    Returns:
        Transform provider class or None if not found
    """
    return transform_provider_registry.get(name)


def get_api_response_hook(name: str) -> Optional[Any]:
    """
    Get a registered API response hook by name.

    Args:
        name: Name of the API response hook

    Returns:
        API response hook class or None if not found
    """
    return api_response_hook_registry.get(name)


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


def list_request_hooks() -> list[str]:
    """
    List all registered request hooks.

    Returns:
        List of request hook names
    """
    return list(request_hook_registry.keys())


def list_response_hooks() -> list[str]:
    """
    List all registered response hooks.

    Returns:
        List of response hook names
    """
    return list(response_hook_registry.keys())


def list_error_hooks() -> list[str]:
    """
    List all registered error hooks.

    Returns:
        List of error hook names
    """
    return list(error_hook_registry.keys())


def list_config_providers() -> list[str]:
    """
    List all registered configuration providers.

    Returns:
        List of config provider names
    """
    return list(config_provider_registry.keys())


def list_data_providers() -> list[str]:
    """
    List all registered data providers.

    Returns:
        List of data provider names
    """
    return list(data_provider_registry.keys())


def list_pagination_providers() -> list[str]:
    """
    List all registered pagination providers.

    Returns:
        List of pagination provider names
    """
    return list(pagination_provider_registry.keys())


def list_transform_providers() -> list[str]:
    """
    List all registered transform providers.

    Returns:
        List of transform provider names
    """
    return list(transform_provider_registry.keys())


def list_api_response_hooks() -> list[str]:
    """
    List all registered API response hooks.

    Returns:
        List of API response hook names
    """
    return list(api_response_hook_registry.keys())


def discover_plugins(package_name: str = "dc_api_x.plugins") -> None:
    """
    Discover and load plugins from a package.

    This function recursively imports all modules in the specified package
    and registers any ApiPlugin subclasses found.

    Args:
        package_name: Name of the package to search for plugins
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        return

    # Get the package path
    if hasattr(package, "__path__"):
        package_path = package.__path__
    else:
        return

    # Recursively import all modules in the package
    for _, name, is_pkg in pkgutil.walk_packages(package_path, package_name + "."):
        if is_pkg:
            discover_plugins(name)
        else:
            try:
                module = importlib.import_module(name)

                # Find all ApiPlugin subclasses in the module
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, ApiPlugin)
                        and obj is not ApiPlugin
                        and obj.__module__ == module.__name__
                    ):
                        # Register the plugin
                        _PLUGINS[obj.__name__] = obj
            except ImportError:
                continue
