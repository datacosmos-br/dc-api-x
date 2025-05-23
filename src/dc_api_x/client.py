"""
API client implementation.

This module provides client implementations for various protocols to
interact with different types of services.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Optional, TypeVar, Union, cast

import requests

from .config import Config, load_config_from_env
from .exceptions import (
    ApiConnectionError,
    ApiError,
    AuthenticationError,
    ConfigurationError,
    RequestError,
)
from .response import ApiResponse, GenericResponse
from .utils.adapters import HttpAdapter
from .utils.auth import AuthProvider
from .utils.proto import (
    DatabaseAdapter,
    DatabaseResult,
    DirectoryAdapter,
    DirectoryEntry,
    MessageQueueAdapter,
    ProtocolAdapter,
)

# Type variables for plugins
P = TypeVar("P", bound="ApiPlugin")

# Default configuration values
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 0.5

# HTTP status codes
HTTP_BAD_REQUEST = HTTPStatus.BAD_REQUEST
HTTP_UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

# Set up logging
logger = logging.getLogger(__name__)

# Type aliases for hooks
RequestHook = Callable[[str, str, dict[str, Any]], dict[str, Any]]
ResponseHook = Callable[[str, str, requests.Response], requests.Response]
ApiResponseHook = Callable[[requests.Response, ApiResponse], ApiResponse]
ErrorHook = Callable[[str, str, Exception, dict[str, Any]], Optional[ApiResponse]]


@dataclass
class ClientConfig:
    """Configuration for API client initialization.

    This class holds all the configuration parameters for ApiClient to reduce
    the number of parameters in the constructor.
    """

    # Connection settings
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = DEFAULT_TIMEOUT
    verify_ssl: bool = True

    # Retry settings
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF

    # Debug mode
    debug: bool = False

    # Configuration object
    config: Optional[Config] = None

    # Extensions
    plugins: list[type[ApiPlugin]] = field(default_factory=list)
    adapter: Optional[ProtocolAdapter] = None
    auth_provider: Optional[AuthProvider] = None

    # Hooks
    request_hooks: list[RequestHook] = field(default_factory=list)
    response_hooks: list[ResponseHook] = field(default_factory=list)
    api_response_hooks: list[ApiResponseHook] = field(default_factory=list)
    error_hooks: list[ErrorHook] = field(default_factory=list)


@dataclass
class RequestConfig:
    """Configuration for HTTP requests.

    This class holds the parameters for making HTTP requests to reduce
    the number of parameters in HTTP methods.
    """

    # Request data
    params: Optional[dict[str, Any]] = None
    data: Optional[dict[str, Any]] = None
    json_data: Optional[dict[str, Any]] = None
    headers: Optional[dict[str, str]] = None
    files: Optional[dict[str, Any]] = None

    # Response handling
    raw_response: bool = False

    # Extra keyword arguments
    extra_kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        config_dict: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> RequestConfig:
        """Create a RequestConfig instance from a dictionary and/or keyword arguments.

        This factory method helps reduce the parameter count in methods that
        would otherwise have too many parameters.

        Args:
            config_dict: Dictionary containing configuration parameters
            **kwargs: Additional parameters that override config_dict values

        Returns:
            RequestConfig object
        """
        # Start with empty dict if None provided
        config = config_dict or {}

        # Override with kwargs
        config.update(kwargs)

        # Extract parameters
        params = config.get("params")
        data = config.get("data")
        json_data = config.get("json_data")
        headers = config.get("headers")
        files = config.get("files")
        raw_response = config.get("raw_response", False)

        # Get any remaining kwargs
        extra_kwargs = {
            k: v
            for k, v in config.items()
            if k
            not in ("params", "data", "json_data", "headers", "files", "raw_response")
        }

        return cls(
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            files=files,
            raw_response=raw_response,
            extra_kwargs=extra_kwargs,
        )


class AdapterTypeError(TypeError):
    """Raised when an operation requires a specific adapter type."""

    DATABASE_REQUIRED = "Query execution requires a DatabaseAdapter"
    DIRECTORY_REQUIRED = "Directory search requires a DirectoryAdapter"
    MESSAGE_QUEUE_REQUIRED = "Message publishing requires a MessageQueueAdapter"


class ApiPlugin:
    """
    Base class for API client plugins.

    Plugins can modify request/response behavior and add functionality to
    the API client.
    """

    def __init__(self, client: ApiClient) -> None:
        """
        Initialize the plugin.

        Args:
            client: ApiClient instance this plugin is attached to
        """
        self.client = client

    def initialize(self) -> None:
        """
        Initialize the plugin (called after __init__).

        Override this method to perform setup tasks.
        """

    def before_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process request parameters before sending.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request keyword arguments

        Returns:
            Modified request keyword arguments
        """
        return kwargs

    def after_request(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> requests.Response:
        """
        Process response before conversion to ApiResponse.

        Args:
            method: HTTP method
            url: Request URL
            response: HTTP response

        Returns:
            Modified HTTP response
        """
        return response

    def before_response_processed(
        self,
        response: requests.Response,
        api_response: ApiResponse,
    ) -> ApiResponse:
        """
        Process ApiResponse before returning to caller.

        Args:
            response: HTTP response
            api_response: Converted API response

        Returns:
            Modified API response
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
        Handle request errors.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred
            kwargs: Request keyword arguments

        Returns:
            ApiResponse to use instead of raising error, or None to raise error
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
        client_config: ClientConfig,
    ):
        """
        Initialize API client using a configuration object.

        Args:
            client_config: Configuration parameters object
        """
        cfg = client_config

        # Use config object if needed
        if cfg.config is None and (
            cfg.url is None or cfg.username is None or cfg.password is None
        ):
            # If individual parameters are not provided, load from environment
            cfg.config = load_config_from_env()

        # Set up configuration
        self.url = cfg.url or (cfg.config.url if cfg.config else None)
        self.username = cfg.username or (cfg.config.username if cfg.config else None)
        self.password = cfg.password or (
            cfg.config.password.get_secret_value() if cfg.config else None
        )
        self.timeout = (
            cfg.timeout
            if cfg.timeout is not None
            else (cfg.config.timeout if cfg.config else DEFAULT_TIMEOUT)
        )
        self.verify_ssl = (
            cfg.verify_ssl
            if cfg.verify_ssl is not None
            else (cfg.config.verify_ssl if cfg.config else True)
        )
        self.max_retries = (
            cfg.max_retries
            if cfg.max_retries is not None
            else (cfg.config.max_retries if cfg.config else DEFAULT_MAX_RETRIES)
        )
        self.retry_backoff = (
            cfg.retry_backoff
            if cfg.retry_backoff is not None
            else (cfg.config.retry_backoff if cfg.config else DEFAULT_RETRY_BACKOFF)
        )
        self.debug = (
            cfg.debug
            if cfg.debug is not None
            else (cfg.config.debug if cfg.config else False)
        )

        # Validate configuration
        if not self.url:
            raise ConfigurationError("API URL is required")

        if not self.username:
            raise ConfigurationError("API username is required")

        if not self.password:
            raise ConfigurationError("API password is required")

        # Initialize hooks
        self._request_hooks = cfg.request_hooks or []
        self._response_hooks = cfg.response_hooks or []
        self._api_response_hooks = cfg.api_response_hooks or []
        self._error_hooks = cfg.error_hooks or []

        # Initialize auth provider
        if cfg.auth_provider is None:
            from .ext.auth import BasicAuthProvider

            cfg.auth_provider = BasicAuthProvider(self.username, self.password)
        self.auth_provider = cfg.auth_provider

        # Initialize plugins
        self._plugins: list[ApiPlugin] = []
        if cfg.plugins:
            for plugin_class in cfg.plugins:
                self.register_plugin(plugin_class)

        # Initialize adapter
        if cfg.adapter is None:
            # Create default HTTP adapter
            cfg.adapter = self._create_default_http_adapter()
        self.adapter = cfg.adapter

        # Connect adapter
        self.adapter.connect()

        # Debug logging
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Initialized API client for %s", self.url)

    @classmethod
    def create(
        cls,
        config_dict: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ApiClient:
        """
        Create an API client with configuration parameters.

        This factory method helps reduce the parameter count in the constructor.

        Args:
            config_dict: Dictionary containing configuration parameters
            **kwargs: Additional parameters that override config_dict values

        Returns:
            ApiClient instance

        Example:
            ```python
            client = ApiClient.create({
                "url": "https://api.example.com",
                "username": "user",
                "password": "pass",
                "timeout": 30,
            })
            ```
        """
        # Start with empty dict if None provided
        config = config_dict or {}

        # Override with kwargs
        config.update(kwargs)

        # Extract parameters
        url = config.get("url")
        username = config.get("username")
        password = config.get("password")
        timeout = config.get("timeout", DEFAULT_TIMEOUT)
        verify_ssl = config.get("verify_ssl", True)
        max_retries = config.get("max_retries", DEFAULT_MAX_RETRIES)
        retry_backoff = config.get("retry_backoff", DEFAULT_RETRY_BACKOFF)
        debug = config.get("debug", False)
        cfg = config.get("config")
        plugins = config.get("plugins", [])
        adapter = config.get("adapter")
        auth_provider = config.get("auth_provider")
        request_hooks = config.get("request_hooks", [])
        response_hooks = config.get("response_hooks", [])
        api_response_hooks = config.get("api_response_hooks", [])
        error_hooks = config.get("error_hooks", [])

        client_config = ClientConfig(
            url=url,
            username=username,
            password=password,
            timeout=timeout,
            verify_ssl=verify_ssl,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            debug=debug,
            config=cfg,
            plugins=plugins,
            adapter=adapter,
            auth_provider=auth_provider,
            request_hooks=request_hooks,
            response_hooks=response_hooks,
            api_response_hooks=api_response_hooks,
            error_hooks=error_hooks,
        )
        return cls(client_config)

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
        request_config: Optional[RequestConfig] = None,
    ) -> ApiResponse:
        """
        Make an HTTP request using the HTTP adapter.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint to call
            request_config: Request configuration parameters

        Returns:
            API response

        Raises:
            ApiConnectionError: If the request fails
            AuthenticationError: If authentication fails
        """
        # Initialize request config if not provided
        if request_config is None:
            request_config = RequestConfig.create()

        # Build full URL
        url = self._build_url(endpoint)

        # Prepare request kwargs
        kwargs = {
            "params": request_config.params,
            "data": request_config.data,
            "json": request_config.json_data,
            "headers": request_config.headers or {},
            "files": request_config.files,
            **request_config.extra_kwargs,
        }

        # Filter out None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Debug logging
        if self.debug:
            logger.debug(
                "Making %s request to %s with kwargs: %s",
                method,
                url,
                {k: v for k, v in kwargs.items() if k != "headers"},
            )
            if kwargs.get("headers"):
                logger.debug(
                    "Request headers: %s",
                    {
                        k: v if k.lower() != "authorization" else "[REDACTED]"
                        for k, v in kwargs["headers"].items()
                    },
                )

        # Apply request hooks (modify kwargs)
        for hook in self._request_hooks:
            kwargs = hook(method, url, kwargs)

        # Apply plugin request hooks
        for plugin in self._plugins:
            kwargs = plugin.before_request(method, url, kwargs)

        try:
            # Make the request
            response = self.adapter.request(method, url, **kwargs)

            # Apply response hooks (modify response)
            for hook in self._response_hooks:
                response = hook(method, url, response)

            # Apply plugin response hooks
            for plugin in self._plugins:
                response = plugin.after_request(method, url, response)

            # Process response
            api_response = self._process_response(response)

            # Apply API response hooks
            for hook in self._api_response_hooks:
                api_response = hook(response, api_response)

            # Apply plugin API response hooks
            for plugin in self._plugins:
                api_response = plugin.before_response_processed(response, api_response)

            # Return raw response if requested
            if request_config.raw_response:
                return api_response

            # Handle response errors
            if (
                not api_response.success
                and api_response.status_code is not None
                and api_response.status_code >= HTTP_BAD_REQUEST
            ):
                # Extract error details
                error_msg = (
                    api_response.error or f"API error: {api_response.status_code}"
                )
                error_details = (
                    api_response.data if isinstance(api_response.data, dict) else None
                )
                self._handle_error_response(api_response, error_msg, error_details)
            else:
                return api_response

        except (RequestError, AuthenticationError):
            # Re-raise API exceptions without wrapping
            raise
        except ApiConnectionError as e:
            # Call error hooks
            for hook in self._error_hooks:
                hook_response = hook(method, url, e, kwargs)
                if hook_response is not None:
                    return hook_response

            # Apply plugin error hooks
            for plugin in self._plugins:
                plugin_response = plugin.on_error(method, url, e, kwargs)
                if plugin_response is not None:
                    return plugin_response

            # Re-raise exception
            raise
        except Exception as e:
            # Call error hooks
            for hook in self._error_hooks:
                hook_response = hook(method, url, e, kwargs)
                if hook_response is not None:
                    return hook_response

            # Apply plugin error hooks
            for plugin in self._plugins:
                plugin_response = plugin.on_error(method, url, e, kwargs)
                if plugin_response is not None:
                    return plugin_response

            # Wrap exception
            if isinstance(e, requests.Timeout):
                raise ApiConnectionError(
                    f"Request timed out after {self.timeout} seconds",
                    details={"url": url, "method": method},
                ) from e
            if isinstance(e, requests.ConnectionError):
                raise ApiConnectionError(
                    f"Failed to connect to API: {str(e)}",
                    details={"url": url, "method": method},
                ) from e
            raise ApiConnectionError(
                f"API request failed: {str(e)}",
                details={"url": url, "method": method},
            ) from e

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
        Make a GET request to the API.

        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Request headers
            raw_response: Whether to return the raw response without error handling
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        request_config = RequestConfig.create(
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )
        return self._make_http_request("GET", endpoint, request_config)

    def post(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint to call
            **kwargs: Request parameters including:
                data: Form data
                json_data: JSON data
                params: Query parameters
                headers: Request headers
                raw_response: Whether to return the raw response without error handling

        Returns:
            API response
        """
        request_config = RequestConfig.create(**kwargs)
        return self._make_http_request("POST", endpoint, request_config)

    def put(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make a PUT request to the API.

        Args:
            endpoint: API endpoint to call
            **kwargs: Request parameters including:
                data: Form data
                json_data: JSON data
                params: Query parameters
                headers: Request headers
                raw_response: Whether to return the raw response without error handling

        Returns:
            API response
        """
        request_config = RequestConfig.create(**kwargs)
        return self._make_http_request("PUT", endpoint, request_config)

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
        Make a DELETE request to the API.

        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Request headers
            raw_response: Whether to return the raw response without error handling
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        request_config = RequestConfig.create(
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )
        return self._make_http_request("DELETE", endpoint, request_config)

    def patch(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        Make a PATCH request to the API.

        Args:
            endpoint: API endpoint to call
            **kwargs: Request parameters including:
                data: Form data
                json_data: JSON data
                params: Query parameters
                headers: Request headers
                raw_response: Whether to return the raw response without error handling

        Returns:
            API response
        """
        request_config = RequestConfig.create(**kwargs)
        return self._make_http_request("PATCH", endpoint, request_config)

    @classmethod
    def from_profile(
        cls,
        profile_name: str,
        plugins: Optional[list[type[ApiPlugin]]] = None,
        adapter: Optional[ProtocolAdapter] = None,
        auth_provider: Optional[AuthProvider] = None,
    ) -> ApiClient:
        """
        Create API client from named profile.

        Args:
            profile_name: Name of the profile to use
            plugins: List of plugin classes to register (optional)
            adapter: Protocol adapter (optional)
            auth_provider: Authentication provider (optional)

        Returns:
            ApiClient: API client instance
        """
        # Load configuration from profile
        config = Config.from_profile(profile_name)

        # Create client with configuration
        client_config = ClientConfig(
            config=config,
            plugins=plugins or [],
            adapter=adapter,
            auth_provider=auth_provider,
        )
        return cls(client_config)

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

    def _build_url(self, endpoint: str) -> str:
        """
        Build the full URL for an API endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL
        """
        if endpoint.startswith(("http://", "https://")):
            return endpoint

        # Normalize URL and endpoint path
        base_url = self.url.rstrip("/")
        endpoint_path = endpoint.lstrip("/")
        return f"{base_url}/{endpoint_path}"

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

    def _handle_error_response(
        self,
        api_response: ApiResponse,
        error_msg: str,
        error_details: Optional[dict[str, Any]],
    ) -> None:
        """
        Handle error responses from the API by raising appropriate exceptions.

        Args:
            api_response: The API response
            error_msg: Error message
            error_details: Error details dictionary

        Raises:
            AuthenticationError: If unauthorized
            RequestError: For other error responses
        """
        if (
            not api_response.success
            and api_response.status_code is not None
            and api_response.status_code >= HTTP_BAD_REQUEST
        ):
            # Handle different error types
            if api_response.status_code == HTTP_UNAUTHORIZED:
                raise AuthenticationError(error_msg, error_details)

            raise RequestError(
                error_msg,
                details=error_details,
                status_code=api_response.status_code,
            )
