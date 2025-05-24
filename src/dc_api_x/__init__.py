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
from typing import Any

# Import other modules after constants
from . import config, models, pagination, schema, utils
from . import utils as utils_module
from .entity import EntityManager
from .entity.base import BaseEntity

# Import concrete implementations from ext module
from .ext import (
    ApiResponseHook,
    AuthProvider,
    BasicAuthProvider,
    BatchDataProvider,
    CacheAdapter,
    ConfigProvider,
    DatabaseAdapter,
    DatabaseTransaction,
    DatabaseTransactionImpl,
    DataProvider,
    DirectoryAdapter,
    DirectoryAdapterImpl,
    ErrorHook,
    GenericDatabaseAdapter,
    HeadersHook,
    HttpAdapter,
    LoggingHook,
    MessageQueueAdapter,
    ProtocolAdapter,
    RequestHook,
    RequestsHttpAdapter,
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

# Import exceptions module
from .utils import exceptions  # Import exceptions module explicitly

# Import constants first to avoid circular imports
from .utils.constants import *  # noqa: F403 - Import all names for public API

# Import protocol types from types module
from .utils.definitions import (
    ApiResponseHookProtocol,
    ConnectionProtocol,
    DataProviderProtocol,
    EntityData,
    EntityId,
    EntityList,
    EntityProtocol,
    ErrorHookProtocol,
    FilterDict,
    Headers,
    HttpMethod,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    PathLike,
    RequestHookProtocol,
    ResponseHookProtocol,
    SchemaProviderProtocol,
    StatusCode,
    TextOrBinary,
    TransactionProtocol,
    TransformFunc,
    WebSocketProtocol,
    assert_type,
    check_type_compatibility,
    validate_with_pydantic,
)

# Import exceptions
from .utils.exceptions import (
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


# Define DatabaseResult since it's not in models.py
class DatabaseResult:
    """Database query result with rows and metadata."""

    def __init__(
        self,
        *,
        success: bool = True,
        rows: list[dict[str, Any]] | None = None,
        query: str = "",
        params: dict[str, Any] | None = None,
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
    "ApiResponseHookProtocol",
    "AuthProvider",
    "BasicAuthProvider",
    "BatchDataProvider",
    "CacheAdapter",
    "ConfigProvider",
    "DatabaseAdapter",
    "DatabaseTransaction",
    "DataProvider",
    "DataProviderProtocol",
    "DirectoryAdapter",
    "ErrorHook",
    "ErrorHookProtocol",
    "HeadersHook",
    "HttpAdapter",
    "LoggingHook",
    "MessageQueueAdapter",
    "ProtocolAdapter",
    "RequestHook",
    "RequestHookProtocol",
    "ResponseHook",
    "ResponseHookProtocol",
    "SchemaProvider",
    "SchemaProviderProtocol",
    "TokenAuthProvider",
    "TransformProvider",
    # Adapter implementations
    "RequestsHttpAdapter",
    "GenericDatabaseAdapter",
    "DatabaseTransactionImpl",
    "DirectoryAdapterImpl",
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
    # Type definitions
    "ConnectionProtocol",
    "EntityData",
    "EntityId",
    "EntityList",
    "EntityProtocol",
    "FilterDict",
    "Headers",
    "HttpMethod",
    "JsonArray",
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "PathLike",
    "StatusCode",
    "TextOrBinary",
    "TransactionProtocol",
    "TransformFunc",
    "WebSocketProtocol",
    "assert_type",
    "check_type_compatibility",
    "validate_with_pydantic",
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
