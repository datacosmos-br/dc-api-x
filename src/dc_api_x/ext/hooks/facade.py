"""
Hook facade for DCApiX.

This module provides a simplified interface for working with hooks,
following the facade design pattern.
"""

import logging
from typing import Any, Optional, TypeVar, Union, cast

import requests

from dc_api_x.models import ApiResponse

from ..auth import AuthProvider, BasicAuthProvider, TokenAuthProvider
from .api_response import ApiResponseHook
from .auth import AuthHook
from .error import ErrorHook
from .logging import LoggingHook
from .protocol import RequestHook, ResponseHook
from .request import HeadersHook

T = TypeVar("T")

# Constants
AUTH_TUPLE_LENGTH = 2
AUTH_TYPE_ERROR_MSG = (
    "auth_provider must be an AuthProvider, a token string, "
    "or a (username, password) tuple"
)


class HookManager:
    """
    Facade for managing and registering hooks.

    This class provides a simplified interface for registering and
    managing hooks in a client or adapter.
    """

    def __init__(self) -> None:
        """Initialize the hook manager with empty hook lists."""
        self._request_hooks: list[RequestHook] = []
        self._response_hooks: list[ResponseHook] = []
        self._api_response_hooks: list[ApiResponseHook] = []
        self._error_hooks: list[ErrorHook] = []

    def add_request_hook(self, hook: RequestHook) -> None:
        """
        Add a request hook.

        Args:
            hook: Request hook to add
        """
        self._request_hooks.append(hook)

    def add_response_hook(self, hook: ResponseHook) -> None:
        """
        Add a response hook.

        Args:
            hook: Response hook to add
        """
        self._response_hooks.append(hook)

    def add_api_response_hook(self, hook: ApiResponseHook) -> None:
        """
        Add an API response hook.

        Args:
            hook: API response hook to add
        """
        self._api_response_hooks.append(hook)

    def add_error_hook(self, hook: ErrorHook) -> None:
        """
        Add an error hook.

        Args:
            hook: Error hook to add
        """
        self._error_hooks.append(hook)

    def add_hook(self, hook: Any) -> None:
        """
        Add a hook based on its type.

        This method will add the hook to the appropriate list based on
        the interfaces it implements.

        Args:
            hook: Hook to add
        """
        # Check if hook implements process_request method
        if hasattr(hook, "process_request") and callable(hook.process_request):
            self.add_request_hook(cast(RequestHook, hook))

        # Check if hook implements process_response method
        if hasattr(hook, "process_response") and callable(hook.process_response):
            self.add_response_hook(cast(ResponseHook, hook))

        # Check if hook implements process_api_response method
        if hasattr(hook, "process_api_response") and callable(
            hook.process_api_response,
        ):
            self.add_api_response_hook(cast(ApiResponseHook, hook))

        # Check if hook implements handle_error method
        if hasattr(hook, "handle_error") and callable(hook.handle_error):
            self.add_error_hook(cast(ErrorHook, hook))

    def add_logging(
        self,
        logger: Optional[Any] = None,
    ) -> LoggingHook:
        """
        Add a logging hook.

        Args:
            logger: Logger to use (defaults to a new logger)

        Returns:
            The created LoggingHook instance
        """
        logger = logger or logging.getLogger("dc_api_x")
        hook = LoggingHook(logger)
        self.add_hook(hook)
        return hook

    def add_headers(self, headers: dict[str, str]) -> HeadersHook:
        """
        Add a headers hook.

        Args:
            headers: Headers to add to requests

        Returns:
            The created HeadersHook instance
        """
        hook = HeadersHook(headers)
        self.add_hook(hook)
        return hook

    def add_auth(
        self,
        auth_provider: Union[AuthProvider, str, tuple[str, str]],
    ) -> AuthHook:
        """
        Add an authentication hook.

        Args:
            auth_provider: Can be an AuthProvider instance, a token string,
                          or a (username, password) tuple

        Returns:
            The created AuthHook instance
        """
        if isinstance(auth_provider, str):
            auth_provider = TokenAuthProvider(auth_provider)
        elif (
            isinstance(auth_provider, tuple[Any, ...])
            and len(auth_provider) == AUTH_TUPLE_LENGTH
        ):
            auth_provider = BasicAuthProvider(auth_provider[0], auth_provider[1])
        # Only check the attribute for non-tuple, non-string types
        elif not isinstance(auth_provider, AuthProvider):
            raise TypeError(AUTH_TYPE_ERROR_MSG)

        hook = AuthHook(auth_provider)
        self.add_hook(hook)
        return hook

    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a request through all request hooks.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified request kwargs
        """
        for hook in self._request_hooks:
            kwargs = hook.process_request(method, url, kwargs)
        return kwargs

    def process_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Process a response through all response hooks.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            Modified response object
        """
        for hook in self._response_hooks:
            response = hook.process_response(method, url, response)
        return response

    def process_api_response(
        self,
        method: str,
        url: str,
        raw_response: requests.Response,
        api_response: ApiResponse,
    ) -> ApiResponse:
        """
        Process an API response through all API response hooks.

        Args:
            method: HTTP method
            url: Request URL
            raw_response: Raw response object
            api_response: Processed API response object

        Returns:
            Modified API response object
        """
        for hook in self._api_response_hooks:
            api_response = hook.process_api_response(
                method,
                url,
                raw_response,
                api_response,
            )
        return api_response

    def handle_error(
        self,
        method: str,
        url: str,
        error: Exception,
    ) -> Optional[ApiResponse]:
        """
        Handle an error through all error hooks.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred

        Returns:
            Optional API response to return instead of raising the error,
            or None to propagate the error
        """
        for hook in self._error_hooks:
            response = hook.handle_error(method, url, error)
            if response is not None:
                return response
        return None

    def clear_hooks(self) -> None:
        """Clear all hooks."""
        self._request_hooks.clear()
        self._response_hooks.clear()
        self._api_response_hooks.clear()
        self._error_hooks.clear()


# Factory functions for creating common hooks


def create_logging_hook(logger: Optional[Any] = None) -> LoggingHook:
    """
    Create a logging hook.

    Args:
        logger: Logger to use (defaults to a new logger)

    Returns:
        LoggingHook instance
    """
    return LoggingHook(logger or logging.getLogger("dc_api_x"))


def create_headers_hook(headers: dict[str, str]) -> HeadersHook:
    """
    Create a headers hook.

    Args:
        headers: Headers to add to requests

    Returns:
        HeadersHook instance
    """
    return HeadersHook(headers)


def create_auth_hook(
    auth_provider: Union[AuthProvider, str, tuple[str, str]],
) -> AuthHook:
    """
    Create an authentication hook.

    Args:
        auth_provider: Can be an AuthProvider instance, a token string,
                      or a (username, password) tuple

    Returns:
        AuthHook instance
    """
    if isinstance(auth_provider, str):
        auth_provider = TokenAuthProvider(auth_provider)
    elif (
        isinstance(auth_provider, tuple[Any, ...])
        and len(auth_provider) == AUTH_TUPLE_LENGTH
    ):
        auth_provider = BasicAuthProvider(auth_provider[0], auth_provider[1])
    # Only check the attribute for non-tuple, non-string types
    elif not isinstance(auth_provider, AuthProvider):
        raise TypeError(AUTH_TYPE_ERROR_MSG)

    return AuthHook(auth_provider)
