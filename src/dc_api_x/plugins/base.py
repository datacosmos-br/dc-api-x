"""
Base plugin infrastructure for DCApiX.

This module provides the base ApiPlugin class and core plugin infrastructure.
"""

from typing import Any, Optional, TypeVar

import requests

from dc_api_x.models import ApiResponse

P = TypeVar("P", bound="ApiPlugin")


class ApiPlugin:
    """
    Base class for API client plugins.

    Plugins can extend the functionality of the ApiClient by hooking into
    various extension points in the request lifecycle.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialize the plugin with a reference to the client.

        Args:
            client: API client instance
        """
        self.client = client

    def initialize(self) -> None:
        """
        Called when the plugin is registered with the client.

        Use this method to set up any resources needed by the plugin.
        """

    def before_request(
        self,
        _method: str,
        _url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Called before a request is made.

        Args:
            _method: HTTP method
            _url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified kwargs for the request
        """
        return kwargs

    def after_request(
        self,
        _method: str,
        _url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Called after a request is made but before it's processed.

        Args:
            _method: HTTP method
            _url: Request URL
            response: Response object

        Returns:
            Modified response object
        """
        return response

    def before_response_processed(
        self,
        _response: requests.Response,
        api_response: ApiResponse,
    ) -> ApiResponse:
        """
        Called after the response is converted to ApiResponse but before returning.

        Args:
            _response: Raw requests.Response object
            api_response: Processed ApiResponse object

        Returns:
            Modified ApiResponse object
        """
        return api_response

    def handle_error(
        self,
        _method: str,
        _url: str,
        _error: Exception,
    ) -> Optional[ApiResponse]:
        """
        Called when an error occurs during a request.

        Args:
            _method: HTTP method
            _url: Request URL
            _error: Exception that occurred

        Returns:
            Optional ApiResponse to return instead of raising the error
        """
        return None

    def create_session(
        self,
        session: requests.Session,
    ) -> requests.Session:
        """
        Called when creating a new session.

        Args:
            session: Session being configured

        Returns:
            Modified session
        """
        return session

    def shutdown(self) -> None:
        """
        Called when the client is being destroyed.

        Use this method to clean up any resources used by the plugin.
        """


# Global registry for plugin discovery
_PLUGINS: dict[str, type[ApiPlugin]] = {}


def register_plugin(plugin_class: type[ApiPlugin]) -> type[ApiPlugin]:
    """
    Register a plugin class for discovery.

    This can be used as a decorator:

    @register_plugin
    class MyPlugin(ApiPlugin):
        pass

    Args:
        plugin_class: Plugin class to register

    Returns:
        The plugin class (for decorator usage)
    """
    _PLUGINS[plugin_class.__name__] = plugin_class
    return plugin_class
