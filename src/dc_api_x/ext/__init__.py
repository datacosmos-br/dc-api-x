"""
Extension interfaces for DCApiX.

This module provides interfaces and base classes that can be implemented
by external packages to extend DCApiX functionality.

These interfaces define clear extension points without including any
specific implementations for external systems.
"""

from .adapters import (
    CacheAdapter,
    DatabaseAdapter,
    DatabaseTransaction,
    DirectoryAdapter,
    HttpAdapter,
    MessageQueueAdapter,
    ProtocolAdapter,
)
from .auth import AuthProvider, BasicAuthProvider, TokenAuthProvider
from .hooks import (
    ApiResponseHook,
    ErrorHook,
    HeadersHook,
    LoggingHook,
    RequestHook,
    ResponseHook,
)
from .providers import (
    BatchDataProvider,
    ConfigProvider,
    DataProvider,
    SchemaProvider,
    TransformProvider,
)

__all__ = [
    # Auth providers
    "AuthProvider",
    "BasicAuthProvider",
    "TokenAuthProvider",
    # Hooks
    "RequestHook",
    "ResponseHook",
    "ApiResponseHook",
    "ErrorHook",
    "LoggingHook",
    "HeadersHook",
    # Adapters
    "ProtocolAdapter",
    "HttpAdapter",
    "DatabaseAdapter",
    "DatabaseTransaction",
    "DirectoryAdapter",
    "MessageQueueAdapter",
    "CacheAdapter",
    # Providers
    "DataProvider",
    "BatchDataProvider",
    "SchemaProvider",
    "TransformProvider",
    "ConfigProvider",
]
