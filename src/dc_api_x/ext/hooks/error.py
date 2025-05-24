"""
Error hook for DCApiX.

This module defines the ErrorHook abstract class for error handling.
"""

import abc
from typing import Optional

from dc_api_x.models import ApiResponse


class ErrorHook(abc.ABC):
    """
    Base interface for error hooks.

    Error hooks can handle exceptions that occur during request processing.
    They can choose to return an ApiResponse instead of propagating the error,
    or they can modify the error before it's raised.
    """

    @abc.abstractmethod
    def handle_error(
        self,
        method: str,
        url: str,
        error: Exception,
    ) -> Optional[ApiResponse]:
        """
        return None  # Implement this method

        Handle an error that occurred during a request.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred

        Returns:
            Optional API response to return instead of raising the error,
            or None to propagate the error
        """
