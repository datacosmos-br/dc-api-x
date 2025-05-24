"""
Constants for DCApiX.

This module contains all constants used across the DCApiX package.
Centralizing constants helps avoid circular imports and improves maintainability.
"""

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
DEFAULT_TOKEN_HEADER = "Authorization"  # noqa: S105
DEFAULT_TOKEN_TYPE = "Bearer"  # noqa: S105

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
