"""
Exception classes for DCApiX.

This module defines all exception classes used by the DCApiX library.
"""

from typing import Any, Optional


class BaseAPIException(Exception):
    """Base exception for all API exceptions."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
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


class ConfigurationError(BaseAPIException):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "configuration_error", details)


class ValidationError(BaseAPIException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "validation_error", details)


class AuthenticationError(BaseAPIException):
    """Exception raised for authentication errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "authentication_error", details)


class AuthorizationError(BaseAPIException):
    """Exception raised for authorization errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
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
    ):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, details)
        self.code = "invalid_credentials"


class ApiConnectionError(BaseAPIException):
    """Exception raised for API connection errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "connection_error", details)


class AdapterError(BaseAPIException):
    """Exception raised for adapter errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "adapter_error", details)


class InvalidOperationError(BaseAPIException):
    """Exception raised for invalid operations."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "invalid_operation", details)


class NotFoundError(BaseAPIException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "not_found", details)


class AlreadyExistsError(BaseAPIException):
    """Exception raised when a resource already exists."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "already_exists", details)


class TimeoutError(BaseAPIException):
    """Exception raised when an operation times out."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "timeout", details)


class RateLimitError(BaseAPIException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "rate_limit", details)


class ServerError(BaseAPIException):
    """Exception raised for server errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Exception message
            details: Optional error details
        """
        super().__init__(message, "server_error", details)


class UnknownError(BaseAPIException):
    """Exception raised for unknown errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
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
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
        self.status_code = status_code
        self.headers = headers

    def __str__(self) -> str:
        return self.message


class SchemaError(ApiError):
    """Error raised when a schema is invalid."""


class EntityError(ApiError):
    """Error raised when an entity operation fails."""
