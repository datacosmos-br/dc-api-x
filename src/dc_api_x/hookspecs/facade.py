"""
Facade for DCApiX hook specifications.

This module provides the main HookSpecs class that combines all hook
specifications from different modules into a single interface.
"""

from .hooks import HookHookSpecs
from .providers import ProviderHookSpecs
from .specs import AdapterHookSpecs


class HookSpecs(AdapterHookSpecs, HookHookSpecs, ProviderHookSpecs):
    """
    Combined hook specifications for the DCApiX plugin system.

    This class inherits all hook specifications from the specialized
    hook specification classes, providing a unified interface for
    all plugin hooks in one place.
    """
