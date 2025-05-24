"""
HTTP adapter for DCApiX.

This module defines the HttpAdapter abstract class for HTTP communication.
"""

import abc
from typing import Any

from .protocol import ProtocolAdapter


class HttpAdapter(ProtocolAdapter):
    """Base interface for HTTP adapters."""

    @abc.abstractmethod
    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> tuple[int, dict[str, Any], bytes]:
        """
        return None  # Implement this method

        Make an HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Tuple of (status_code, headers, body)
        """
