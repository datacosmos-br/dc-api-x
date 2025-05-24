"""
Logfire Hook.

A hook that uses Logfire for logging API interactions.
"""

import os
from typing import Any, Optional

import logfire

from dc_api_x.ext.hooks.logging import LoggingHook

# HTTP status code constants
HTTP_ERROR_STATUS_CODE = 400


class LogfireHook(LoggingHook):
    """Hook for logging API interactions using Logfire."""

    def __init__(
        self,
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """Initialize the LogfireHook.

        Args:
            service_name: Name of the service for logging
            environment: Environment name (prod, staging, etc)
        """
        # Initialize with defaults from environment if not provided
        self.service_name = service_name or os.environ.get(
            "LOGFIRE_SERVICE_NAME",
            "dcapix",
        )
        self.environment = environment or os.environ.get(
            "LOGFIRE_ENVIRONMENT",
            "development",
        )

        # Ensure logfire is configured
        if not service_name and not environment:
            logfire.configure(
                service_name=self.service_name,
                environment=self.environment,
            )

    def process_request(self, request) -> Any:
        """Log an API request.

        Args:
            request: The ApiRequest object

        Returns:
            The unchanged request object
        """
        # Log the request
        logfire.info(
            f"HTTP Request: {request.method} {request.url}",
            method=request.method,
            url=request.url,
            headers=self._sanitize_headers(request.headers or {}),
            params=request.params,
        )
        return request

    # Keep the original method for backward compatibility
    def process_request_old(self, method, url, kwargs) -> None:
        """Log an API request (legacy method).

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request arguments

        Returns:
            The unchanged kwargs
        """
        # Extract headers for sanitization
        headers = kwargs.get("headers", {})

        # Log the request with context
        with logfire.context(http_method=method, http_url=url):
            logfire.info(
                f"HTTP Request: {method} {url}",
                request_method=method,
                request_url=url,
                request_headers=self._sanitize_headers(headers),
                request_params=kwargs.get("params", {}),
            )

        return kwargs

    def process_response(self, response) -> None:
        """Log an API response.

        Args:
            response: The ApiResponse object

        Returns:
            The unchanged response object
        """
        # Extract method from the request
        method = response.request.method if response.request else "UNKNOWN"

        # Log the response
        logfire.info(
            f"HTTP Response: {response.status_code} from {method} {response.url}",
            status_code=response.status_code,
            url=response.url,
            headers=self._sanitize_headers(response.headers or {}),
            method=method,
            content_length=len(response.content) if response.content else 0,
        )
        return response

    # Keep the original method for backward compatibility
    def process_response_old(self, method, url, response) -> None:
        """Log an API response (legacy method).

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            The unchanged response
        """
        # Determine log level based on status code
        status_code = getattr(response, "status_code", 0)
        log_level = "error" if status_code >= HTTP_ERROR_STATUS_CODE else "info"

        # Calculate response time
        elapsed = getattr(response, "elapsed", None)
        response_time = elapsed.total_seconds() * 1000 if elapsed else 0

        # Extract and sanitize headers
        headers = getattr(response, "headers", {})

        # Log at the appropriate level
        with logfire.context(http_method=method, http_url=url, http_status=status_code):
            if log_level == "info":
                logfire.info(
                    f"HTTP Response: {status_code} from {method} {url}",
                    response_status=status_code,
                    response_time_ms=response_time,
                    response_headers=self._sanitize_headers(headers),
                    response_size=len(getattr(response, "content", b"") or b""),
                )
            else:
                logfire.error(
                    f"HTTP Error: {status_code} from {method} {url}",
                    response_status=status_code,
                    response_time_ms=response_time,
                    response_headers=self._sanitize_headers(headers),
                    response_size=len(getattr(response, "content", b"") or b""),
                )

        return response

    def log_error(self, error, context=None) -> None:
        """Log an API error.

        Args:
            error: The exception object
            context: Additional context for the error
        """
        # Log the error with context
        extra = {"error_type": type(error).__name__}
        if context:
            extra.update(context)

        logfire.error(str(error), exc_info=True, **extra)

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Sanitize headers to remove sensitive information.

        Args:
            headers: The headers to sanitize

        Returns:
            The sanitized headers
        """
        sensitive_headers = {
            "authorization",
            "x-api-key",
            "cookie",
            "set-cookie",
            "apikey",
            "token",
        }
        sanitized = {}

        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized
