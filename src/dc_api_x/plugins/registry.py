"""
Plugin registry for DCApiX.

This module provides functions for discovering and loading plugins.
"""

import importlib
import inspect
import pkgutil
from typing import Optional, TypeVar, cast

from .base import _PLUGINS, ApiPlugin

P = TypeVar("P", bound=ApiPlugin)


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
