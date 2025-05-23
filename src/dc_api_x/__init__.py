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

from typing import Any, Optional

from pydantic import BaseModel

# Import exceptions first to avoid circular imports
from . import exceptions
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

# Constants - moved from constants.py
# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_MULTIPLE_CHOICES = 300
HTTP_MOVED_PERMANENTLY = 301
HTTP_FOUND = 302
HTTP_NOT_MODIFIED = 304
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504

# Default client configuration
DEFAULT_TIMEOUT = 30  # Seconds
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_DELAY = 1.0  # Seconds
DEFAULT_RETRY_BACKOFF = 0.5  # Exponential backoff factor
DEFAULT_BACKOFF_FACTOR = 2.0  # Multiplier for backoff time
DEFAULT_BACKOFF_MAX = 60.0  # Maximum backoff time in seconds
DEFAULT_CONNECT_TIMEOUT = 10.0  # Connection timeout in seconds
DEFAULT_READ_TIMEOUT = 30.0  # Read timeout in seconds
DEFAULT_VERIFY_SSL = True

# Pagination
DEFAULT_PAGE_SIZE = 20
DEFAULT_PAGE = 1
MAX_PAGE_SIZE = 100
DEFAULT_TOTAL_PAGES_HEADER = "X-Total-Pages"
DEFAULT_TOTAL_COUNT_HEADER = "X-Total-Count"
DEFAULT_PAGE_HEADER = "X-Page"
DEFAULT_PAGE_SIZE_HEADER = "X-Page-Size"

# Encoding
DEFAULT_ENCODING = "utf-8"
DEFAULT_JSON_CONTENT_TYPE = "application/json"
DEFAULT_FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"
DEFAULT_MULTIPART_CONTENT_TYPE = "multipart/form-data"

# Cache
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
DEFAULT_CACHE_KEY_PREFIX = "dc_api_x:"

# Rate limiting
DEFAULT_RATE_LIMIT = 60  # Requests per minute
DEFAULT_RATE_LIMIT_PERIOD = 60  # Period in seconds

# Authentication
TOKEN_EXPIRY_MARGIN = 30  # Seconds before token expiry to refresh
DEFAULT_TOKEN_HEADER = "Authorization"  # noqa: S105, B105
DEFAULT_TOKEN_TYPE = "Bearer"  # noqa: S105, B105

# Logging
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"

# Configuration settings
CONFIG_URL_KEY = "url"
CONFIG_USERNAME_KEY = "username"
CONFIG_PASSWORD_KEY = "password"  # noqa: S105
CONFIG_TIMEOUT_KEY = "timeout"
CONFIG_VERIFY_SSL_KEY = "verify_ssl"
CONFIG_REQUIRED_KEYS = (CONFIG_URL_KEY, CONFIG_USERNAME_KEY, CONFIG_PASSWORD_KEY)
CONFIG_DEFAULT_ENV_FILE = ".env"
CONFIG_JSON_EXTENSION = ".json"
CONFIG_ENV_PREFIX = "API_"

# Error messages
INVALID_JSON_ERROR = "Content is not valid JSON: {}"
INVALID_JSON_UTF8_ERROR = "Content is not valid JSON or UTF-8: {}"
INVALID_TYPE_ERROR = "Cannot convert content of type {} to dict"

# Config error messages
URL_EMPTY_ERROR = "URL cannot be empty"
URL_FORMAT_ERROR = "URL must start with http:// or https://"
UNSUPPORTED_FORMAT_ERROR = "Unsupported file format: {}"
CONFIG_FILE_NOT_FOUND_ERROR = "Configuration file not found: {}"
PROFILE_ENV_FILE_NOT_FOUND_ERROR = "Profile environment file not found: {}"
INVALID_PROFILE_CONFIG_ERROR = "Invalid profile configuration: {}"

# CLI error messages
SCHEMA_ENTITY_NOT_SPECIFIED_ERROR = "Please specify an entity name or use --all flag."
SCHEMA_EXTRACTION_FAILED_ERROR = "Failed to extract schema for entity: {}"
INVALID_JSON_IN_ERROR = "Invalid JSON in {}: {}"

# Import remaining modules
from . import config, models, pagination, schema, utils
from .entity import EntityManager
from .entity.base import BaseEntity
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
    # Models
    "ApiRequest",
    "ApiResponse",
    "AuthResponse",
    "BaseModel",
    "ConfigurableBase",
    "DatabaseResult",
    "DirectoryEntry",
    "Error",
    "ErrorDetail",
    "GenericResponse",
    "Metadata",
    "QueueMessage",
    # Entity Classes
    "BaseEntity",
    "EntityManager",
    # Schema Classes
    "SchemaDefinition",
    "SchemaExtractor",
    "SchemaManager",
    # Pagination
    "paginate",
    # HTTP Status Codes
    "HTTP_BAD_REQUEST",
    "HTTP_CREATED",
    "HTTP_FORBIDDEN",
    "HTTP_INTERNAL_SERVER_ERROR",
    "HTTP_NOT_FOUND",
    "HTTP_OK",
    "HTTP_UNAUTHORIZED",
    # Configuration defaults
    "CONFIG_DEFAULT_ENV_FILE",
    "CONFIG_ENV_PREFIX",
    "CONFIG_FILE_NOT_FOUND_ERROR",
    "CONFIG_JSON_EXTENSION",
    "CONFIG_PASSWORD_KEY",
    "CONFIG_REQUIRED_KEYS",
    "CONFIG_TIMEOUT_KEY",
    "CONFIG_URL_KEY",
    "CONFIG_USERNAME_KEY",
    "CONFIG_VERIFY_SSL_KEY",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_ENCODING",
    "DEFAULT_JSON_CONTENT_TYPE",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_PAGE",
    "DEFAULT_RETRY_BACKOFF",
    "DEFAULT_TIMEOUT",
    "DEFAULT_VERIFY_SSL",
    "MAX_PAGE_SIZE",
    # Error messages
    "INVALID_JSON_ERROR",
    "INVALID_JSON_UTF8_ERROR",
    "INVALID_PROFILE_CONFIG_ERROR",
    "INVALID_TYPE_ERROR",
    "PROFILE_ENV_FILE_NOT_FOUND_ERROR",
    "SCHEMA_ENTITY_NOT_SPECIFIED_ERROR",
    "SCHEMA_EXTRACTION_FAILED_ERROR",
    "UNSUPPORTED_FORMAT_ERROR",
    "URL_EMPTY_ERROR",
    "URL_FORMAT_ERROR",
    # Exceptions
    "AdapterError",
    "AlreadyExistsError",
    "ApiConnectionError",
    "ApiError",
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
    "ApiTimeoutError",
    "ValidationError",
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
    # Plugin management
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
]

# Version info
__version__ = "0.2.0"
__author__ = "Data Center DC"
__email__ = "your.email@example.com"
__license__ = "MIT"
