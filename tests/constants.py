"""
Constants used in tests to avoid magic values.

This module centralizes all constants used across test modules to prevent
the use of magic values, which improves maintainability and passes linting
rules like PLR2004 (magic value used in comparison).
"""

# Timeout values (seconds)
DEFAULT_TIMEOUT = 30
CUSTOM_TIMEOUT = 45

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# Test IDs
TEST_USER_ID = 1
TEST_PRODUCT_ID = 101
TEST_ORDER_ID = 1001
TEST_CUSTOMER_ID = 2001

# Prices
PRODUCT_PRICE = 799.99
ORDER_TOTAL = 99.99
DISCOUNT_AMOUNT = 10.50

# Retry counts
MAX_RETRIES = 2
BACKOFF_FACTOR = 0.5

# Test ages
TEST_PERSON_AGE = 30
TEST_MIN_AGE = 18
TEST_MAX_AGE = 65

# Test user data
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass"  # noqa: S105
TEST_EMAIL = "test@example.com"

# Test URLs
TEST_API_URL = "https://api.example.com"
TEST_CALLBACK_URL = "https://callback.example.com"

# Test file paths
TEST_CONFIG_PATH = "config.json"
TEST_DATA_PATH = "data.csv"

# Pagination
TEST_PAGE_SIZE = 20
TEST_PAGE_NUMBER = 1

# Error messages for tests
INVALID_CONFIG_ERROR = "Invalid configuration"
CONNECTION_FAILED_ERROR = "Connection failed"
INVALID_DATA_ERROR = "Invalid data"
RESOURCE_NOT_FOUND_ERROR = "Resource not found"
FILE_NOT_FOUND_ERROR = "File not found"
API_ERROR_MESSAGE = "API error"
CLI_ERROR_MESSAGE = "CLI error"
INVALID_JSON_ERROR = "Invalid JSON"
NO_MOCK_RESPONSE_ERROR = "No mock response defined"

# Default test data for factories
DEFAULT_USER = {
    "id": 1,
    "name": "Test User",
    "email": "test@example.com",
    "role": "user",
    "active": True,
}

# Authentication test data
TEST_AUTH_TOKEN = "test-token"
TEST_AUTH_USERNAME = "test-user"
TEST_AUTH_PASSWORD = "test-password"  # noqa: S105

# Performance test data
TEST_ITERATIONS = 100
TEST_PERFORMANCE_ROUNDS = 5
EXPECTED_SUM_0_TO_99 = 4950  # Sum of numbers from 0 to 99

# Command line options for CLI tests
DEFAULT_GREETING = "World"
DEFAULT_NAME_OPTION = "--name"
DEFAULT_NAME_OPTION_SHORT = "-n"
DEFAULT_VERBOSE_OPTION = "--verbose"
DEFAULT_VERBOSE_OPTION_SHORT = "-v"

# Typer app test data
TEST_GREETING_FORMAT = "Hello {}!"
TEST_VERBOSE_MESSAGE = "Running hello with name={}"
