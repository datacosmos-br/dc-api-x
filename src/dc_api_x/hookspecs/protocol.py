"""
Core hook specification protocol for DCApiX plugin system.

This module defines the base hook specification marker and common type definitions
used throughout the DCApiX plugin system.
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
