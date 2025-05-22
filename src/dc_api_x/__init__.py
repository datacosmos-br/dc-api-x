"""
DCApiX - Python API Extensions.

DCApiX provides utilities for working with APIs and other data protocols.

It provides a flexible foundation for building clients for various services,
including HTTP APIs, databases, LDAP directories, and message queues.

Features:
- Multi-protocol support (HTTP, Database, LDAP, Message Queues)
- Pluggable architecture with runtime-discovery of extensions
- Comprehensive error handling and reporting
- Flexible authentication mechanisms
- Data validation and transformation
- Schema-based API client generation
- Pagination support
- Logging and monitoring hooks
"""

from . import config, exceptions, models, pagination, schema, utils

# Client
from .client import ApiClient

# Extension interfaces
from .ext import (  # Auth; Providers; Adapters; Hooks
    ApiResponseHook,
    AuthProvider,
    BasicAuthProvider,
    BatchDataProvider,
    CacheAdapter,
    ConfigProvider,
    DatabaseAdapter,
    DataProvider,
    DirectoryAdapter,
    ErrorHook,
    HeadersHook,
    HttpAdapter,
    LoggingHook,
    MessageQueueAdapter,
    ProtocolAdapter,
    RequestHook,
    ResponseHook,
    SchemaProvider,
    TokenAuthProvider,
    TransformProvider,
)

# Models
from .models import (
    ApiResponse,
    BaseModel,
    DatabaseResult,
    DirectoryEntry,
    GenericResponse,
    QueueMessage,
)

# Plugin management
from .plugin_manager import enable_plugins, get_adapter, list_adapters

__all__ = [
    # Modules
    "config",
    "exceptions",
    "models",
    "pagination",
    "schema",
    "utils",
    # Client
    "ApiClient",
    # Models
    "ApiResponse",
    "BaseModel",
    "GenericResponse",
    "DatabaseResult",
    "DirectoryEntry",
    "QueueMessage",
    # Extension interfaces
    "AuthProvider",
    "BasicAuthProvider",
    "TokenAuthProvider",
    "RequestHook",
    "ResponseHook",
    "ApiResponseHook",
    "ErrorHook",
    "LoggingHook",
    "HeadersHook",
    "ProtocolAdapter",
    "HttpAdapter",
    "DatabaseAdapter",
    "DirectoryAdapter",
    "MessageQueueAdapter",
    "CacheAdapter",
    "DataProvider",
    "BatchDataProvider",
    "SchemaProvider",
    "TransformProvider",
    "ConfigProvider",
    # Plugin management
    "enable_plugins",
    "get_adapter",
    "list_adapters",
]

# Version info
__version__ = "0.2.0"
__author__ = "Data Center DC"
__email__ = "your.email@example.com"
__license__ = "MIT"
