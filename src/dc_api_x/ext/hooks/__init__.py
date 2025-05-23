"""
Hook interfaces for DCApiX.

This module contains base interfaces for request, response, and error hooks
that can be implemented by external packages.
"""

from .api_response import ApiResponseHook
from .auth import AuthHook
from .error import ErrorHook
from .facade import (
    HookManager,
    create_auth_hook,
    create_headers_hook,
    create_logging_hook,
)
from .logging import LoggingHook
from .protocol import RequestHook, ResponseHook
from .request import HeadersHook

__all__ = [
    # Interfaces
    "RequestHook",
    "ResponseHook",
    "ApiResponseHook",
    "ErrorHook",
    # Implementations
    "LoggingHook",
    "HeadersHook",
    "AuthHook",
    # Facade & Factory
    "HookManager",
    "create_auth_hook",
    "create_headers_hook",
    "create_logging_hook",
]
