"""
Exception classes for DCApiX.

This module defines all exception classes used by the DCApiX library.
"""

from typing import Any, Dict, Optional


class ApiError(Exception):
    """Base class for all API client exceptions."""

    URL_REQUIRED = "API base URL is required"
    USERNAME_REQUIRED = "API username is required"
    PASSWORD_REQUIRED = "API password is required"
    PROFILE_NOT_FOUND = "Configuration profile not found"
    INVALID_CONFIG = "Invalid configuration"
    DIRECTORY_NOT_FOUND = "Directory not found"
    SCHEMA_NOT_FOUND = "Schema not found"
    ADAPTER_NOT_FOUND = "Adapter not found"
    AUTH_PROVIDER_NOT_FOUND = "Authentication provider not found"

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize API error.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class AuthenticationError(ApiError):
    """Raised when authentication fails."""


class ConfigError(ApiError):
    """Raised when there is a configuration error."""

    URL_REQUIRED = "API base URL is required"
    USERNAME_REQUIRED = "API username is required"
    PASSWORD_REQUIRED = "API password is required"
    PROFILE_NOT_FOUND = "Configuration profile not found"
    INVALID_CONFIG = "Invalid configuration"


# Alias for ConfigError for backward compatibility
ConfigurationError = ConfigError


# Renamed from ConnectionError to ApiConnectionError to avoid shadowing the builtin
class ApiConnectionError(ApiError):
    """Raised when connection to the API fails."""

    CONNECTION_FAILED = "Failed to connect to API"
    REQUEST_TIMEOUT = "Request timed out"


class RequestError(ApiError):
    """Raised when there is an error with the request."""

    REQUEST_FAILED = "Request failed"


class ResponseError(ApiError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ):
        """
        Initialize response error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_body: Response body
            headers: Response headers
            **kwargs: Additional arguments for ApiError
        """
        details = kwargs.pop("details", {})
        details.update(
            {
                "status_code": status_code,
                "response_body": response_body,
                "headers": headers,
            },
        )
        super().__init__(message, details=details, **kwargs)
        self.status_code = status_code
        self.response_body = response_body
        self.headers = headers


class ValidationError(ApiError):
    """Raised when data validation fails."""


class SchemaError(ApiError):
    """Raised when schema operations fail."""
