"""
Exception classes for DCApiX.

This module defines all exception classes used by the DCApiX library.
"""

from typing import Any

from .constants import (
    API_REQUEST_FAILED_MSG,
    CONNECTION_FAILED_MSG,
    CONNECTION_TIMEOUT_MSG,
    HTTP_ERROR_MSG,
    INVALID_JSON_IN_ERROR,
    SCHEMA_ENTITY_NOT_SPECIFIED_ERROR,
    SCHEMA_EXTRACTION_FAILED_ERROR,
)
from .definitions import EntityName, ErrorCode, OutputFormat, PathLike


class BaseAPIError(Exception):
    """Base exception for all API exceptions."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            code: Optional error code
            details: Optional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code or "error"
        self.details = details or {}


#
# General API Exceptions
#


class ConfigurationError(BaseAPIError):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "configuration_error", details)


class ValidationError(BaseAPIError):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "validation_error", details)


class AuthenticationError(BaseAPIError):
    """Exception raised for authentication errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "authentication_error", details)


class AuthorizationError(BaseAPIError):
    """Exception raised for authorization errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "authorization_error", details)


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""

    def __init__(
        self,
        message: str = "Invalid credentials",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, details)
        self.code = "invalid_credentials"


class ApiConnectionError(BaseAPIError):
    """Exception raised for API connection errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "connection_error", details)


class AdapterError(BaseAPIError):
    """Exception raised for adapter errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "adapter_error", details)


class InvalidOperationError(BaseAPIError):
    """Exception raised for invalid operations."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "invalid_operation", details)


class NotFoundError(BaseAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "not_found", details)


class AlreadyExistsError(BaseAPIError):
    """Exception raised when a resource already exists."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "already_exists", details)


class ApiTimeoutError(BaseAPIError):
    """Exception raised when an operation times out."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "timeout", details)


class RateLimitError(BaseAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "rate_limit", details)


class ServerError(BaseAPIError):
    """Exception raised for server errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "server_error", details)


class UnknownError(BaseAPIError):
    """Exception raised for unknown errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "unknown_error", details)


#
# CLI-specific Exceptions
#


class CLIError(BaseAPIError):
    """Exception raised for CLI-specific errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "cli_error", details)


class SchemaEntityNotSpecifiedError(CLIError):
    """Exception raised when an entity is required but not specified."""

    def __init__(self) -> None:
        super().__init__(SCHEMA_ENTITY_NOT_SPECIFIED_ERROR)


class SchemaExtractionFailedError(CLIError):
    """Exception raised when schema extraction fails."""

    def __init__(self, entity_name: EntityName) -> None:
        super().__init__(SCHEMA_EXTRACTION_FAILED_ERROR.format(entity_name))


class JsonValidationError(CLIError):
    """Exception raised when JSON validation fails."""

    DATA_FILE: ErrorCode = "data file"
    DATA_STRING: ErrorCode = "data string"

    def __init__(self, source: str, error: Exception) -> None:
        """Initialize exception.

        Args:
            source: Source of the JSON data (file or string)
            error: Underlying error
        """
        super().__init__(INVALID_JSON_IN_ERROR.format(source, str(error)))


class ConfigFileNotFoundError(CLIError):
    """Exception raised when a configuration file is not found."""

    def __init__(self, path: PathLike) -> None:
        """Initialize exception.

        Args:
            path: Path to the config file that was not found
        """
        super().__init__(f"Config file not found: {path}")


class DirectoryNotFoundError(CLIError):
    """Exception raised when a directory is not found."""

    def __init__(
        self,
        path: PathLike,
        message: str = "Directory does not exist",
    ) -> None:
        """Initialize exception.

        Args:
            path: Path to the directory that was not found
            message: Custom error message prefix
        """
        super().__init__(f"{message}: {path}")


class FilePathNotDirectoryError(CLIError):
    """Exception raised when a path exists but is not a directory."""

    def __init__(self, path: PathLike) -> None:
        """Initialize exception.

        Args:
            path: Path that exists but is not a directory
        """
        super().__init__(f"Path exists but is not a directory: {path}")


class InvalidOutputFormatError(CLIError):
    """Exception raised when an unsupported output format is requested."""

    def __init__(self, format: OutputFormat) -> None:
        """Initialize exception.

        Args:
            format: The unsupported output format
        """
        super().__init__(f"Unsupported output format: {format}")


class UnsupportedJsonTypeError(CLIError):
    """Exception raised when an unsupported JSON type is provided."""

    def __init__(self, type_name: str) -> None:
        """Initialize exception.

        Args:
            type_name: Name of the unsupported type
        """
        super().__init__(f"Expected JSON string or file path, got {type_name}")


class MissingEnvironmentVariableError(CLIError):
    """Exception raised when a required environment variable is missing."""

    def __init__(self, var_name: str, prefix: str = "") -> None:
        """Initialize exception.

        Args:
            var_name: Name of the missing environment variable
            prefix: Optional prefix used for the environment variable
        """
        full_name = f"{prefix}{var_name}"
        super().__init__(f"{full_name} environment variable is required")


class InvalidParameterFormatError(CLIError):
    """Exception raised when a parameter has an invalid format."""

    def __init__(self, param: str, param_type: str = "param") -> None:
        """Initialize exception.

        Args:
            param: The invalid parameter
            param_type: Type of parameter (filter, param, etc.)
        """
        super().__init__(f"Invalid {param_type} format: {param}. Expected key=value")


#
# Legacy Exceptions for backwards compatibility
#


# Manter compatibilidade com código existente
ConfigError = ConfigurationError


class ApiError(Exception):
    """Legacy API Error for backwards compatibility."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
        self.status_code = status_code
        self.headers = headers

    def __str__(self) -> str:
        return self.message


class ResponseError(ApiError):
    """Exception raised for HTTP response errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            status_code: HTTP status code
            response_data: Optional response data
            headers: Optional HTTP headers
        """
        code = f"http_{status_code}"
        details = {"response_data": response_data} if response_data else None
        super().__init__(message, code, details, status_code, headers)


class SchemaError(ApiError):
    """Error raised when a schema is invalid."""


class EntityError(ApiError):
    """Error raised when an entity operation fails."""


class ConnectionTimeoutError(ApiConnectionError):
    """Raised when a request times out."""

    def __init__(self, timeout: int, details: dict[str, Any] | None = None) -> None:
        """Initialize the error.

        Args:
            timeout: The timeout duration in seconds
            details: Additional error details
        """
        super().__init__(CONNECTION_TIMEOUT_MSG.format(timeout), details=details)


class ConnectionFailedError(ApiConnectionError):
    """Raised when a connection to the API fails."""

    def __init__(
        self,
        error: Exception,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            error: The underlying error
            details: Additional error details
        """
        super().__init__(CONNECTION_FAILED_MSG.format(str(error)), details=details)


class RequestFailedError(ApiConnectionError):
    """Raised when an API request fails for any reason."""

    def __init__(
        self,
        error: Exception,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            error: The underlying error
            details: Additional error details
        """
        super().__init__(API_REQUEST_FAILED_MSG.format(str(error)), details=details)


class RequestError(ApiError):
    """Exception raised for HTTP request errors."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
            status_code: HTTP status code
        """
        code = f"http_{status_code}" if status_code else "request_error"
        super().__init__(message, code, details, status_code)

    def __str__(self) -> str:
        """Return string representation of the error.

        Returns:
            Error message with status code if available
        """
        if self.status_code:
            return HTTP_ERROR_MSG.format(self.status_code, self.message)
        return self.message
