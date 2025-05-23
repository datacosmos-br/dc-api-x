"""
API response hook for DCApiX.

This module defines the ApiResponseHook abstract class for API response processing.
"""

import abc

import requests

from dc_api_x.models import ApiResponse


class ApiResponseHook(abc.ABC):
    """
    Base interface for API response hooks.

    API response hooks can modify ApiResponse objects before they are returned
    to the caller. They run after the raw HTTP response has been converted to
    an ApiResponse but before the response is returned to the client.
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
