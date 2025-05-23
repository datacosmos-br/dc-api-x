"""
Constants used throughout the application.

This module defines constants used across the API client library,
including HTTP status codes, default configuration values, and other
common constants.
"""

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
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
DEFAULT_TIMEOUT = 60  # Seconds
DEFAULT_MAX_RETRIES = 3
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
