"""
Plugins for DCApiX.

This package contains plugin interfaces and implementations for extending DCApiX
functionality.
"""

from .base import ApiPlugin, register_plugin
from .registry import get_plugin, list_plugins

__all__ = [
    "ApiPlugin",
    "register_plugin",
    "get_plugin",
    "list_plugins",
]
