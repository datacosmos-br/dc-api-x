"""
Request hook implementations for DCApiX.

This module contains concrete implementations of request hook interfaces.
"""

from typing import Any

from .protocol import RequestHook


class HeadersHook(RequestHook):
    """
    Hook that adds headers to requests.

    This hook implements the RequestHook interface to inject custom headers
    into each request.
    """

    def __init__(self, headers: dict[str, str]) -> None:
        """
        Initialize with headers.

        Args:
            headers: Headers to add to every request
        """
        self.headers = headers

    def process_request(
        self,
        _method: str,
        _url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add headers to the request.

        This method merges the hook's headers with any existing headers
        in the request, giving precedence to existing headers in case
        of conflicts.

        Args:
            _method: HTTP method
            _url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified request kwargs with updated headers
        """
        headers = kwargs.get("headers", {})
        headers.update(self.headers)
        kwargs["headers"] = headers
        return kwargs
