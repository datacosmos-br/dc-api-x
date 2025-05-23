"""
Plugins for DCApiX.

This package contains plugin interfaces and implementations for extending DCApiX
functionality.
"""

from .base import ApiPlugin, register_plugin
from .registry import (
    enable_plugins,
    get_adapter,
    get_api_response_hook,
    get_auth_provider,
    get_config_provider,
    get_data_provider,
    get_error_hook,
    get_pagination_provider,
    get_plugin,
    get_request_hook,
    get_response_hook,
    get_schema_provider,
    get_transform_provider,
    list_adapters,
    list_api_response_hooks,
    list_auth_providers,
    list_config_providers,
    list_data_providers,
    list_error_hooks,
    list_pagination_providers,
    list_plugins,
    list_request_hooks,
    list_response_hooks,
    list_schema_providers,
    list_transform_providers,
    load_plugins,
)

__all__ = [
    "ApiPlugin",
    "register_plugin",
    "get_plugin",
    "list_plugins",
    "enable_plugins",
    "load_plugins",
    "get_adapter",
    "get_auth_provider",
    "get_schema_provider",
    "get_request_hook",
    "get_response_hook",
    "get_error_hook",
    "get_config_provider",
    "get_data_provider",
    "get_pagination_provider",
    "get_transform_provider",
    "get_api_response_hook",
    "list_adapters",
    "list_auth_providers",
    "list_schema_providers",
    "list_request_hooks",
    "list_response_hooks",
    "list_error_hooks",
    "list_config_providers",
    "list_data_providers",
    "list_pagination_providers",
    "list_transform_providers",
    "list_api_response_hooks",
]
