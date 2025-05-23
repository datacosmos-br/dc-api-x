"""
Client interface for DCApiX.

This module provides a generic client interface that can work with different
protocols (HTTP, database, LDAP, etc.) using protocol adapters and plugins.
"""

import logging
from typing import Any, Optional, TypeVar, Union, cast

import requests

from dc_api_x.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
)

from .config import Config, load_config_from_env
from .exceptions import (
    ApiConnectionError,
    ApiError,
    AuthenticationError,
    ConfigurationError,
    RequestError,
)
from .ext.adapters import (
    DatabaseAdapter,
    DirectoryAdapter,
    HttpAdapter,
    MessageQueueAdapter,
    ProtocolAdapter,
)
from .ext.auth import AuthProvider
from .ext.hooks import ApiResponseHook, ErrorHook, RequestHook, ResponseHook
from .models import ApiResponse, DatabaseResult, DirectoryEntry, GenericResponse

# Set up logger
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")
P = TypeVar("P", bound="ApiPlugin")


# Custom exception for adapter type errors
class AdapterTypeError(TypeError):
    """Raised when an operation requires a specific adapter type."""

    DATABASE_REQUIRED = "Query execution requires a DatabaseAdapter"
    DIRECTORY_REQUIRED = "Directory search requires a DirectoryAdapter"
    MESSAGE_QUEUE_REQUIRED = "Message publishing requires a MessageQueueAdapter"


class ApiPlugin:
    """
    Base class for API client plugins.

    Plugins can extend the functionality of the ApiClient by hooking into
    various extension points in the request lifecycle.
    """

    def __init__(self, client: "ApiClient") -> None:
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
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Called before a request is made.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified kwargs for the request
        """
        return kwargs

    def after_request(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Called after a request is made but before it's processed.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            Modified response object
        """
        return response

    def before_response_processed(
        self,
        response: requests.Response,
        api_response: ApiResponse,
    ) -> ApiResponse:
        """
        Called after the response is converted to ApiResponse but before returning.

        Args:
            response: Raw requests.Response object
            api_response: Processed ApiResponse object

        Returns:
            Modified ApiResponse object
        """
        return api_response

    def on_error(
        self,
        method: str,
        url: str,
        error: Exception,
        kwargs: dict[str, Any],
    ) -> Optional[ApiResponse]:
        """
        Called when an error occurs during request.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred
            kwargs: Request kwargs

        Returns:
            ApiResponse to use instead of raising the error, or None to raise
        """
        return None


class ApiClient:
    """
    Generic client for various protocols.

    This client handles communication with different services using adapters,
    authentication providers, and hooks.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        *,
        verify_ssl: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        debug: bool = False,
        config: Optional[Config] = None,
        plugins: Optional[list[type[ApiPlugin]]] = None,
        adapter: Optional[ProtocolAdapter] = None,
        auth_provider: Optional[AuthProvider] = None,
        request_hooks: Optional[list[RequestHook]] = None,
        response_hooks: Optional[list[ResponseHook]] = None,
        api_response_hooks: Optional[list[ApiResponseHook]] = None,
        error_hooks: Optional[list[ErrorHook]] = None,
    ):
        """
        Initialize API client.

        You can provide configuration either through individual parameters or
        through a Config object. If both are provided, individual parameters
        take precedence.

        Args:
            url: API base URL (optional if config is provided)
            username: API username (optional if config is provided)
            password: API password (optional if config is provided)
            timeout: Request timeout in seconds (default: DEFAULT_TIMEOUT)
            verify_ssl: Whether to verify SSL certificates (default: True)
            max_retries: Maximum number of retry attempts (default: DEFAULT_MAX_RETRIES)
            retry_backoff: Exponential backoff factor for retries (default: DEFAULT_RETRY_BACKOFF)
            debug: Enable debug mode (default: False)
            config: Configuration object (optional)
            plugins: List of plugin classes to register (optional)
            adapter: Protocol adapter (optional, default is HTTP)
            auth_provider: Authentication provider (optional)
            request_hooks: List of request hooks (optional)
            response_hooks: List of response hooks (optional)
            api_response_hooks: List of API response hooks (optional)
            error_hooks: List of error hooks (optional)
        """
        # Use config object if provided
        if config is None and (url is None or username is None or password is None):
            # If individual parameters are not provided, load from environment
            config = load_config_from_env()

        # Set up configuration
        self.url = url or (config.url if config else None)
        self.username = username or (config.username if config else None)
        self.password = password or (
            config.password.get_secret_value() if config else None
        )
        self.timeout = (
            timeout
            if timeout is not None
            else (config.timeout if config else DEFAULT_TIMEOUT)
        )
        self.verify_ssl = (
            verify_ssl
            if verify_ssl is not None
            else (config.verify_ssl if config else True)
        )
        self.max_retries = (
            max_retries
            if max_retries is not None
            else (config.max_retries if config else DEFAULT_MAX_RETRIES)
        )
        self.retry_backoff = (
            retry_backoff
            if retry_backoff is not None
            else (config.retry_backoff if config else DEFAULT_RETRY_BACKOFF)
        )
        self.debug = debug if debug is not None else (config.debug if config else False)

        # Validate configuration
        if not self.url:

            def _url_required_error():
                return ConfigurationError("API URL is required")

            raise _url_required_error()

        if not self.username:

            def _username_required_error():
                return ConfigurationError("API username is required")

            raise _username_required_error()

        if not self.password:

            def _password_required_error():
                return ConfigurationError("API password is required")

            raise _password_required_error()

        # Initialize hooks
        self._request_hooks = request_hooks or []
        self._response_hooks = response_hooks or []
        self._api_response_hooks = api_response_hooks or []
        self._error_hooks = error_hooks or []

        # Initialize auth provider
        if auth_provider is None:
            from .ext.auth import BasicAuthProvider

            auth_provider = BasicAuthProvider(self.username, self.password)
        self.auth_provider = auth_provider

        # Initialize plugins
        self._plugins: list[ApiPlugin] = []
        if plugins:
            for plugin_class in plugins:
                self.register_plugin(plugin_class)

        # Initialize adapter
        if adapter is None:
            # Create default HTTP adapter
            adapter = self._create_default_http_adapter()
        self.adapter = adapter

        # Connect adapter
        self.adapter.connect()

        # Debug logging
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Initialized API client for %s", self.url)

    def _create_default_http_adapter(self) -> HttpAdapter:
        """
        Create a default HTTP adapter based on requests.

        Returns:
            HttpAdapter implementation
        """
        from .utils.adapters import RequestsHttpAdapter

        return RequestsHttpAdapter(
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
            max_retries=self.max_retries,
            retry_backoff=self.retry_backoff,
            auth_provider=self.auth_provider,
        )

    def register_plugin(self, plugin_class: type[ApiPlugin]) -> ApiPlugin:
        """
        Register a plugin with the client.

        Args:
            plugin_class: Plugin class to register

        Returns:
            Initialized plugin instance
        """
        plugin = plugin_class(self)
        plugin.initialize()
        self._plugins.append(plugin)
        return plugin

    def get_plugin(self, plugin_class: type[P]) -> Optional[P]:
        """
        Get a registered plugin by class.

        Args:
            plugin_class: Plugin class to find

        Returns:
            Plugin instance or None if not found
        """
        for plugin in self._plugins:
            if isinstance(plugin, plugin_class):
                return cast(P, plugin)
        return None

    def _make_http_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        files: Optional[dict[str, Any]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            params: Query parameters (optional)
            data: Form data (optional)
            json_data: JSON data (optional)
            headers: Additional headers (optional)
            files: Files to upload (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response

        Raises:
            RequestError: If there's an error making the request
            ResponseError: If the response contains an error
            AuthenticationError: If authentication fails
            ConnectionError: If there's an error connecting to the API
        """
        # Build full URL
        if endpoint.startswith(("http://", "https://")):
            url = endpoint
        else:
            # Normalize URL and endpoint path
            base_url = self.url.rstrip("/")
            endpoint_path = endpoint.lstrip("/")
            url = f"{base_url}/{endpoint_path}"

        # Set up request kwargs
        request_kwargs: dict[str, Any] = {
            "params": params,
            "data": data,
            "json": json_data,
            "headers": headers or {},
            "files": files,
            **kwargs,
        }

        # Run request hooks
        for hook in self._request_hooks:
            request_kwargs = hook(method, url, request_kwargs)

        # Run plugin before_request hooks
        for plugin in self._plugins:
            request_kwargs = plugin.before_request(method, url, request_kwargs)

        try:
            logger.debug("Making %s request to %s", method, url)
            logger.debug("Request kwargs: %s", request_kwargs)

            # Make the request
            response = self.adapter.request(method, url, **request_kwargs)

            # Run plugin after_request hooks
            for plugin in self._plugins:
                response = plugin.after_request(method, url, response)

            # Run response hooks
            for hook in self._response_hooks:
                response = hook(method, url, response)

            # Return raw response if requested
            if raw_response:
                return ApiResponse(
                    success=response.status_code < HTTP_BAD_REQUEST,
                    status_code=response.status_code,
                    data=response,
                )

            # Process response
            if response.status_code == HTTP_UNAUTHORIZED:

                def _auth_failed_error():
                    return AuthenticationError("Authentication failed")

                raise _auth_failed_error()

            # Convert response to ApiResponse
            api_response = self._process_response(response)

            # Run plugin before_response_processed hooks
            for plugin in self._plugins:
                api_response = plugin.before_response_processed(response, api_response)

            # Run api_response hooks
            for hook in self._api_response_hooks:
                api_response = hook(method, url, response, api_response)

            return api_response

        except AuthenticationError:
            # Re-raise authentication errors
            raise
        except ApiConnectionError as e:
            # Log connection errors and re-raise
            logger.exception("Connection error: %s", str(e))

            # Run error hooks
            for hook in self._error_hooks:
                result = hook(method, url, e, request_kwargs)
                if result is not None:
                    return result

            # Run plugin on_error hooks
            for plugin in self._plugins:
                result = plugin.on_error(method, url, e, request_kwargs)
                if result is not None:
                    return result

            raise
        except Exception as e:
            # Log other errors
            logger.error(
                "Error making %s request to %s: %s",
                method,
                url,
                str(e),
                exc_info=True,
            )

            # Run error hooks
            for hook in self._error_hooks:
                result = hook(method, url, e, request_kwargs)
                if result is not None:
                    return result

            # Run plugin on_error hooks
            for plugin in self._plugins:
                result = plugin.on_error(method, url, e, request_kwargs)
                if result is not None:
                    return result

            # Convert to appropriate error type
            if isinstance(e, requests.RequestException):
                raise RequestError(f"Request error: {str(e)}") from e
        else:
            return api_response

    def _process_response(self, response: requests.Response) -> ApiResponse:
        """
        Process HTTP response into ApiResponse.

        Args:
            response: HTTP response

        Returns:
            ApiResponse: Processed API response
        """
        try:
            # Try to parse JSON response
            data = response.json()
        except ValueError:
            # If not JSON, use text
            data = response.text

        # Check if response is successful
        success = response.status_code < HTTP_BAD_REQUEST

        if not success:
            # Try to extract error details
            error = None
            error_code = None
            error_details = None

            if isinstance(data, dict):
                # Extract error information from dictionary
                error = data.get("error") or data.get("message") or data.get("msg")
                error_code = data.get("code") or data.get("error_code")
                error_details = data.get("details") or data.get("error_details")

            if not error:
                # Use status code description as fallback
                error = f"HTTP {response.status_code}: {response.reason}"

            # Handle common error status codes
            if response.status_code == HTTP_NOT_FOUND:
                logger.warning("Resource not found: %s", response.url)
            elif response.status_code >= HTTP_INTERNAL_SERVER_ERROR:
                logger.error("Server error: %s", error or response.reason)

            return ApiResponse(
                success=False,
                status_code=response.status_code,
                data=data,
                error=error,
                error_code=error_code,
                error_details=error_details,
            )

        # Successful response
        return ApiResponse(
            success=True,
            status_code=response.status_code,
            data=data,
        )

    def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make GET request to API.

        Args:
            endpoint: API endpoint path
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response
        """
        return self._make_http_request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make POST request to API.

        Args:
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response
        """
        return self._make_http_request(
            "POST",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make PUT request to API.

        Args:
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response
        """
        return self._make_http_request(
            "PUT",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make DELETE request to API.

        Args:
            endpoint: API endpoint path
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response
        """
        return self._make_http_request(
            "DELETE",
            endpoint,
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def patch(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make PATCH request to API.

        Args:
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
            ApiResponse: API response
        """
        return self._make_http_request(
            "PATCH",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    @classmethod
    def from_profile(
        cls,
        profile_name: str,
        plugins: Optional[list[type[ApiPlugin]]] = None,
        adapter: Optional[ProtocolAdapter] = None,
        auth_provider: Optional[AuthProvider] = None,
    ) -> "ApiClient":
        """
        Create API client from configuration profile.

        Args:
            profile_name: Name of the profile to load
            plugins: List of plugin classes to register (optional)
            adapter: Protocol adapter (optional)
            auth_provider: Authentication provider (optional)

        Returns:
            ApiClient: API client instance

        Raises:
            ValueError: If the profile doesn't exist or is invalid
        """
        from .config import Config

        config = Config.from_profile(profile_name)
        return cls(
            config=config,
            plugins=plugins,
            adapter=adapter,
            auth_provider=auth_provider,
        )

    def test_connection(self) -> tuple[bool, str]:
        """
        Test connection to API.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Try a simple request to test connection
            response = self.get("ping", raw_response=True)
        except ApiError as e:
            return False, f"Connection failed: {str(e)}"
        else:
            return True, f"Connection successful (status {response.status_code})"

    def execute_query(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> GenericResponse:
        """
        Execute a database query (requires DatabaseAdapter).

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            GenericResponse with query results
        """
        if not isinstance(self.adapter, DatabaseAdapter):

            def _db_adapter_required_error():
                return AdapterTypeError(AdapterTypeError.DATABASE_REQUIRED)

            raise _db_adapter_required_error()

        try:
            results = self.adapter.execute(query, params)
            return GenericResponse.success(
                DatabaseResult(
                    success=True,
                    rows=results,
                    query=query,
                    params=params,
                ),
            )
        except ValueError as e:
            return GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )
        except (TypeError, AttributeError) as e:
            return GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )
        except Exception as e:  # Keep this catch-all, but add From
            return GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )

    def search_directory(
        self,
        base_dn: str,
        search_filter: str,
        attributes: Optional[list[str]] = None,
        scope: str = "subtree",
    ) -> GenericResponse:
        """
        Search a directory (requires DirectoryAdapter).

        Args:
            base_dn: Base DN for the search
            search_filter: Search filter
            attributes: Attributes to return
            scope: Search scope

        Returns:
            GenericResponse with search results
        """
        if not isinstance(self.adapter, DirectoryAdapter):

            def _dir_adapter_required_error():
                return AdapterTypeError(AdapterTypeError.DIRECTORY_REQUIRED)

            raise _dir_adapter_required_error()

        try:
            results = self.adapter.search(base_dn, search_filter, attributes, scope)
            entries = [DirectoryEntry(dn, attrs) for dn, attrs in results]
            return GenericResponse.success(entries)
        except ValueError as e:
            return GenericResponse.error(
                str(e),
                error_code="SEARCH_FAILED",
                error_details={
                    "base_dn": base_dn,
                    "filter": search_filter,
                },
            )
        except Exception as e:  # Keep this catch-all, but add From
            return GenericResponse.error(
                str(e),
                error_code="SEARCH_FAILED",
                error_details={
                    "base_dn": base_dn,
                    "filter": search_filter,
                },
            )

    def publish_message(
        self,
        topic: str,
        message: Union[str, bytes, dict[str, Any]],
        **kwargs: Any,
    ) -> GenericResponse:
        """
        Publish a message (requires MessageQueueAdapter).

        Args:
            topic: Topic to publish to
            message: Message to publish
            **kwargs: Additional parameters

        Returns:
            GenericResponse indicating success or failure
        """
        if not isinstance(self.adapter, MessageQueueAdapter):

            def _mq_adapter_required_error():
                return AdapterTypeError(AdapterTypeError.MESSAGE_QUEUE_REQUIRED)

            raise _mq_adapter_required_error()

        try:
            self.adapter.publish(topic, message, **kwargs)
            return GenericResponse.success({"topic": topic})
        except ValueError as e:
            return GenericResponse.error(
                str(e),
                error_code="PUBLISH_FAILED",
                error_details={"topic": topic},
            )
        except Exception as e:  # Keep this catch-all, but add From
            return GenericResponse.error(
                str(e),
                error_code="PUBLISH_FAILED",
                error_details={"topic": topic},
            )

    def __del__(self) -> None:
        """
        Clean up resources when the client is destroyed.
        """
        # Disconnect the adapter
        try:
            if hasattr(self, "adapter") and self.adapter is not None:
                self.adapter.disconnect()
        except (AttributeError, TypeError):
            if self.debug:
                logger.exception("Error disconnecting adapter")
        except Exception:  # Keep this catch-all for safety
            if self.debug:
                logger.exception("Error disconnecting adapter")

        # Allow plugins to clean up
        if hasattr(self, "_plugins"):
            for plugin in self._plugins:
                try:
                    plugin.shutdown()
                except (AttributeError, TypeError):
                    if self.debug:
                        logger.exception(
                            "Error shutting down plugin %s",
                            plugin.__class__.__name__,
                        )
                except Exception:  # Keep this catch-all for safety
                    if self.debug:
                        logger.exception(
                            "Error shutting down plugin %s",
                            plugin.__class__.__name__,
                        )
