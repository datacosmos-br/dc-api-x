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

# Standard library imports
from typing import Any, Optional

# Models
from pydantic import BaseModel  # Use pydantic's BaseModel directly

# Plugin management
from .plugin_manager import enable_plugins, get_adapter, list_adapters

# Base modules
from . import config, exceptions, models, pagination, schema, utils
from .client import ApiClient  # Client

# Extension interfaces
from .ext import (
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
    ConfigurableBase,  # ConfigurableBase instead of BaseModel
    DirectoryEntry,
    GenericResponse,
    QueueMessage,
)


# Define DatabaseResult since it's not in models.py
class DatabaseResult:
    """Database query result with rows and metadata."""

    def __init__(
        self,
        *,
        success: bool = True,
        rows: Optional[list[dict[str, Any]]] = None,
        query: str = "",
        params: Optional[dict[str, Any]] = None,
    ):
        """Initialize with query results.

        Args:
            success: Whether the query was successful
            rows: Result rows from the query
            query: The executed query string
            params: Parameters used in the query
        """
        self.success = success
        self.rows = rows or []
        self.query = query
        self.params = params or {}

    def __repr__(self) -> str:
        return f"DatabaseResult(success={self.success}, rows={len(self.rows)})"


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
    "ConfigurableBase",  # Add ConfigurableBase to __all__
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
