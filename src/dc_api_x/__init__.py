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

# Mock logfire before anything else to avoid import issues
from typing import Any, Optional

# Import other modules after constants
from . import config, exceptions, models, pagination, schema, utils

# Import constants first to avoid circular imports
from .constants import *  # noqa: F403 - Import all names for public API
from .entity import EntityManager
from .entity.base import BaseEntity
from .exceptions import (
    AdapterError,
    AlreadyExistsError,
    ApiConnectionError,
    ApiError,
    ApiTimeoutError,
    AuthenticationError,
    AuthorizationError,
    BaseAPIError,
    CLIError,
    ConfigError,
    ConfigurationError,
    InvalidCredentialsError,
    InvalidOperationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
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
from .models import (
    ApiRequest,
    ApiResponse,
    AuthResponse,
    ConfigurableBase,
    DirectoryEntry,
    Error,
    ErrorDetail,
    GenericResponse,
    Metadata,
    QueueMessage,
)
from .pagination import paginate
from .plugins import (
    ApiPlugin,
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
    register_plugin,
)
from .schema import SchemaDefinition, SchemaExtractor, SchemaManager


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
    ) -> None:
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


# Import ApiClient after all dependencies are defined
from .client import ApiClient  # noqa: E402

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
    # Entity
    "EntityManager",
    "BaseEntity",
    # Extension interfaces
    "ApiResponseHook",
    "AuthProvider",
    "BasicAuthProvider",
    "BatchDataProvider",
    "CacheAdapter",
    "ConfigProvider",
    "DatabaseAdapter",
    "DataProvider",
    "DirectoryAdapter",
    "ErrorHook",
    "HeadersHook",
    "HttpAdapter",
    "LoggingHook",
    "MessageQueueAdapter",
    "ProtocolAdapter",
    "RequestHook",
    "ResponseHook",
    "SchemaProvider",
    "TokenAuthProvider",
    "TransformProvider",
    # Models
    "ApiRequest",
    "ApiResponse",
    "AuthResponse",
    "ConfigurableBase",
    "DatabaseResult",
    "DirectoryEntry",
    "Error",
    "ErrorDetail",
    "GenericResponse",
    "Metadata",
    "QueueMessage",
    # Pagination
    "paginate",
    # Plugin system
    "ApiPlugin",
    "enable_plugins",
    "get_adapter",
    "get_api_response_hook",
    "get_auth_provider",
    "get_config_provider",
    "get_data_provider",
    "get_error_hook",
    "get_pagination_provider",
    "get_plugin",
    "get_request_hook",
    "get_response_hook",
    "get_schema_provider",
    "get_transform_provider",
    "list_adapters",
    "list_api_response_hooks",
    "list_auth_providers",
    "list_config_providers",
    "list_data_providers",
    "list_error_hooks",
    "list_pagination_providers",
    "list_plugins",
    "list_request_hooks",
    "list_response_hooks",
    "list_schema_providers",
    "list_transform_providers",
    "load_plugins",
    "register_plugin",
    # Schema
    "SchemaDefinition",
    "SchemaExtractor",
    "SchemaManager",
    # Exceptions
    "AdapterError",
    "AlreadyExistsError",
    "ApiConnectionError",
    "ApiError",
    "ApiTimeoutError",
    "AuthenticationError",
    "AuthorizationError",
    "BaseAPIError",
    "CLIError",
    "ConfigError",
    "ConfigurationError",
    "InvalidCredentialsError",
    "InvalidOperationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]

# Version info
__version__ = "0.2.0"
__author__ = "Data Center DC"
__email__ = "your.email@example.com"
__license__ = "MIT"
