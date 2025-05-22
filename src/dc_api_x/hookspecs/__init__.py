"""
Hook specifications for the DC-API-X plugin system.

This module defines the hook specifications that plugins can implement
to extend the functionality of DC-API-X.
"""

from .hookspecs import HookSpecs, hookspec

__all__ = ["HookSpecs", "hookspec"]
