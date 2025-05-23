"""
Request and response hook interfaces for DCApiX.

This module is deprecated. Please use the dc_api_x.ext.hooks package instead.
"""

# Re-export from hooks package
from .hooks.api_response import ApiResponseHook
from .hooks.auth import AuthHook
from .hooks.error import ErrorHook
from .hooks.facade import (
    HookManager,
    create_auth_hook,
    create_headers_hook,
    create_logging_hook,
)
from .hooks.logging import LoggingHook
from .hooks.protocol import RequestHook, ResponseHook
from .hooks.request import HeadersHook

__all__ = [
    "ApiResponseHook",
    "AuthHook",
    "ErrorHook",
    "HeadersHook",
    "HookManager",
    "LoggingHook",
    "RequestHook",
    "ResponseHook",
    "create_auth_hook",
    "create_headers_hook",
    "create_logging_hook",
]
