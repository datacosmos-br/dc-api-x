"""
Hook specifications for the DCApiX plugin system.

This module defines the hook specifications that plugins can implement
to extend the functionality of DCApiX.
"""

from .hookspecs import HookSpecs, hookspec

__all__ = ["HookSpecs", "hookspec"]
