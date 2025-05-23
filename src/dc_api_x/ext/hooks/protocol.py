"""
Base protocol hooks for DCApiX.

This module defines the base hook abstract classes that all
specific hooks must inherit from.
"""

from typing import Any, Protocol, TypeVar, runtime_checkable

import requests

T = TypeVar("T")


@runtime_checkable
class RequestHook(Protocol):
    """
    Base interface for request hooks.

    Request hooks can modify requests before they are sent. They are executed
    in order of registration, with each hook receiving the modified request
    from the previous hook.
    """

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
        ...


@runtime_checkable
class ResponseHook(Protocol):
    """
    Base interface for response hooks.

    Response hooks can modify responses after they are received. They are executed
    in order of registration, with each hook receiving the modified response
    from the previous hook.
    """

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
        ...
