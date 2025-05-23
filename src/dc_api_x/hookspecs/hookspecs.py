"""
Central hook specifications for the DC-API-X plugin system.

This module provides the combined hook specifications for the DC-API-X plugin system,
gathering all hook specifications defined in specialized modules.
"""

import pluggy

from .facade import HookSpecs

# Re-export the unified hook spec class and marker
hookspec = pluggy.HookspecMarker("dc_api_x")

__all__ = ["HookSpecs", "hookspec"]
