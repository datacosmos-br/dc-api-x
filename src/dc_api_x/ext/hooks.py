"""
Request and response hook interfaces for DCApiX.

This module defines interfaces for request and response hooks that can be
implemented by external packages to modify requests and responses.
"""

import abc
from typing import Any, Optional, TypeVar

import requests

from dc_api_x.models import ApiResponse

T = TypeVar("T")


class RequestHook(abc.ABC):
    """
    Base interface for request hooks.

    Request hooks can modify requests before they are sent.
    """

    @abc.abstractmethod
    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a request before it is sent.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified kwargs for the request
        """


class ResponseHook(abc.ABC):
    """
    Base interface for response hooks.

    Response hooks can modify responses after they are received.
    """

    @abc.abstractmethod
    def process_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Process a response after it is received.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            Modified response object
        """


class ApiResponseHook(abc.ABC):
    """
    Base interface for API response hooks.

    API response hooks can modify ApiResponse objects before they are returned.
    """

    @abc.abstractmethod
    def process_api_response(
        self,
        method: str,
        url: str,
        raw_response: requests.Response,
        api_response: ApiResponse,
    ) -> ApiResponse:
        """
        Process an API response before it is returned.

        Args:
            method: HTTP method
            url: Request URL
            raw_response: Raw response object
            api_response: Processed API response object

        Returns:
            Modified API response object
        """


class ErrorHook(abc.ABC):
    """
    Base interface for error hooks.

    Error hooks can handle errors that occur during requests.
    """

    @abc.abstractmethod
    def handle_error(
        self,
        method: str,
        url: str,
        error: Exception,
    ) -> Optional[ApiResponse]:
        """
        Handle an error that occurred during a request.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred

        Returns:
            Optional API response to return instead of raising the error,
            or None to propagate the error
        """


# Common hook implementations


class LoggingHook(RequestHook, ResponseHook):
    """Hook that logs requests and responses."""

    def __init__(self, logger: Any) -> None:
        """
        Initialize with a logger.

        Args:
            logger: Logger to use for logging
        """
        self.logger = logger

    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Log the request and return unchanged kwargs."""
        self.logger.debug("Request: %s %s\nParams: %s", method, url, kwargs)
        return kwargs

    def process_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """Log the response and return unchanged response."""
        self.logger.debug(
            "Response: %s %s\nStatus: %s",
            method,
            url,
            response.status_code,
        )
        return response


class HeadersHook(RequestHook):
    """Hook that adds headers to requests."""

    def __init__(self, headers: dict[str, str]) -> None:
        """
        Initialize with headers.

        Args:
            headers: Headers to add to requests
        """
        self.headers = headers

    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Add headers to the request."""
        headers = kwargs.get("headers", {})
        headers.update(self.headers)
        kwargs["headers"] = headers
        return kwargs
