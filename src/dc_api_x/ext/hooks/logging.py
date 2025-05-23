"""
Logging hook for DCApiX.

This module defines the LoggingHook implementation for request and response logging.
"""

from typing import Any

import requests

from .protocol import RequestHook, ResponseHook


class LoggingHook(RequestHook, ResponseHook):
    """
    Hook that logs requests and responses.

    This hook implements both RequestHook and ResponseHook interfaces to provide
    comprehensive logging of the entire request/response lifecycle.
    """

    def __init__(self, logger: Any) -> None:
        """
        Initialize with a logger.

        Args:
            logger: Logger to use for logging (any object with debug, info, warning methods)
        """
        self.logger = logger

    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Log the request and return unchanged kwargs.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Unmodified request kwargs
        """
        self.logger.debug("Request: %s %s\nParams: %s", method, url, kwargs)
        return kwargs

    def process_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Log the response and return unchanged response.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            Unmodified response object
        """
        self.logger.debug(
            "Response: %s %s\nStatus: %s",
            method,
            url,
            response.status_code,
        )
        return response
