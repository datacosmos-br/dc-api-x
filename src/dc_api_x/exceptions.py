"""
Exception classes for DCApiX.

This module defines all exception classes used by the DCApiX library.
"""

from typing import Any, Optional


class BaseAPIError(Exception):
    """Base exception for all API exceptions."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
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


class ConfigurationError(BaseAPIError):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "configuration_error", details)


class ValidationError(BaseAPIError):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "validation_error", details)


class AuthenticationError(BaseAPIError):
    """Exception raised for authentication errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "authentication_error", details)


class AuthorizationError(BaseAPIError):
    """Exception raised for authorization errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
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
        details: Optional[dict[str, Any]] = None,
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

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "connection_error", details)


class AdapterError(BaseAPIError):
    """Exception raised for adapter errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "adapter_error", details)


class InvalidOperationError(BaseAPIError):
    """Exception raised for invalid operations."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "invalid_operation", details)


class NotFoundError(BaseAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "not_found", details)


class AlreadyExistsError(BaseAPIError):
    """Exception raised when a resource already exists."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "already_exists", details)


class ApiTimeoutError(BaseAPIError):
    """Exception raised when an operation times out."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "timeout", details)


class RateLimitError(BaseAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "rate_limit", details)


class ServerError(BaseAPIError):
    """Exception raised for server errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "server_error", details)


class UnknownError(BaseAPIError):
    """Exception raised for unknown errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "unknown_error", details)


# Manter compatibilidade com código existente
ConfigError = ConfigurationError


# Legacy classes for backwards compatibility
class ApiError(Exception):
    """Legacy API Error for backwards compatibility."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        status_code: Optional[int] = None,
        headers: Optional[dict[str, str]] = None,
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
        response_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
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


class CLIError(BaseAPIError):
    """Exception raised for CLI-specific errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "cli_error", details)


class SchemaError(ApiError):
    """Error raised when a schema is invalid."""


class EntityError(ApiError):
    """Error raised when an entity operation fails."""


class ConnectionTimeoutError(ApiConnectionError):
    """Raised when a request times out."""

    def __init__(self, timeout: int, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the error.

        Args:
            timeout: The timeout duration in seconds
            details: Additional error details
        """
        super().__init__(f"Request timed out after {timeout} seconds", details=details)


class ConnectionFailedError(ApiConnectionError):
    """Raised when a connection to the API fails."""

    def __init__(
        self,
        error: Exception,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            error: The underlying error
            details: Additional error details
        """
        super().__init__(f"Failed to connect to API: {str(error)}", details=details)


class RequestFailedError(ApiConnectionError):
    """Raised when an API request fails for any reason."""

    def __init__(
        self,
        error: Exception,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            error: The underlying error
            details: Additional error details
        """
        super().__init__(f"API request failed: {str(error)}", details=details)


class RequestError(ApiError):
    """Exception raised for HTTP request errors."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: Optional[int] = None,
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
            return f"{self.message} (HTTP {self.status_code})"
        return self.message
