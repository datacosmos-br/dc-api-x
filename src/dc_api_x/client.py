"""
API client implementation.

This module provides client implementations for various protocols to
interact with different types of services.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Union

import requests

import dc_api_x as apix

from . import exceptions
from .config import Config

# Set up logging
logger = logging.getLogger(__name__)

# Type aliases for hooks
RequestHook = Callable[[str, str, dict[str, Any]], dict[str, Any]]
ResponseHook = Callable[[str, str, requests.Response], requests.Response]
ApiResponseHook = Callable[[requests.Response, "apix.ApiResponse"], "apix.ApiResponse"]
ErrorHook = Callable[
    [str, str, Exception, dict[str, Any]],
    Optional["apix.ApiResponse"],
]

# Type variables for plugins
P = TypeVar("P", bound="apix.ApiPlugin")


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
    timeout: int = apix.DEFAULT_TIMEOUT
    verify_ssl: bool = True

    # Retry settings
    max_retries: int = apix.DEFAULT_MAX_RETRIES
    retry_backoff: float = apix.DEFAULT_RETRY_BACKOFF

    # Debug mode
    debug: bool = False

    # Configuration object


if apix is not None:
    config: Optional[apix.Config] = None
else:
    # Handle None case appropriately
    # TODO: Implement proper None handling

    # Extensions
    plugins: list[type[apix.ApiPlugin]] = field(default_factory=list[Any])
if apix is not None:
    adapter: Optional[apix.ProtocolAdapter] = None
else:
    # Handle None case appropriately
    pass  # TODO: Implement proper None handling
if apix is not None:
    auth_provider: Optional[apix.AuthProvider] = None
else:
    # Handle None case appropriately
    # TODO: Implement proper None handling

    # Hooks
    request_hooks: list[RequestHook] = field(default_factory=list[Any])
    response_hooks: list[ResponseHook] = field(default_factory=list[Any])
    api_response_hooks: list[ApiResponseHook] = field(default_factory=list[Any])
    error_hooks: list[ErrorHook] = field(default_factory=list[Any])


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
    extra_kwargs: dict[str, Any] = field(default_factory=dict[str, Any])

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
        api_response: apix.ApiResponse,
    ) -> apix.ApiResponse:
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
    ) -> Optional[apix.ApiResponse]:
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
    API client for making HTTP requests.

    This client handles authentication, request/response processing, and
    error handling for API interactions.
    """

    def __init__(
        self,
        client_config: Optional[ClientConfig] = None,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = apix.DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        max_retries: int = apix.DEFAULT_MAX_RETRIES,
        retry_backoff: float = apix.DEFAULT_RETRY_BACKOFF,
        debug: bool = False,
    ) -> None:
        """
        Initialize the API client.

        Args:
            client_config: Configuration for the client
            url: API base URL (overrides client_config)
            username: API username (overrides client_config)
            password: API password (overrides client_config)
            timeout: Request timeout in seconds (overrides client_config)
            verify_ssl: Whether to verify SSL certificates (overrides client_config)
            max_retries: Maximum number of retries (overrides client_config)
            retry_backoff: Backoff factor for retries (overrides client_config)
            debug: Enable debug logging (overrides client_config)
        """
        # If direct parameters are provided, create a ClientConfig
        if client_config is None:
            client_config = ClientConfig(
                url=url,
                username=username,
                password=password,
                timeout=timeout,
                verify_ssl=verify_ssl,
                max_retries=max_retries,
                retry_backoff=retry_backoff,
                debug=debug,
            )
        # If direct parameters are provided, override client_config
        else:
            if url is not None:
                client_config.url = url
            if username is not None:
                client_config.username = username
            if password is not None:
                client_config.password = password
            if timeout != apix.DEFAULT_TIMEOUT:
                client_config.timeout = timeout
            if not verify_ssl:
                client_config.verify_ssl = verify_ssl
            if max_retries != apix.DEFAULT_MAX_RETRIES:
                client_config.max_retries = max_retries
            if retry_backoff != apix.DEFAULT_RETRY_BACKOFF:
                client_config.retry_backoff = retry_backoff
            if debug:
                client_config.debug = debug

        # Validate required parameters
        if client_config.url is None:
            raise MissingUrlError()
        if client_config.username is None:
            raise MissingUsernameError()
        if client_config.password is None:
            raise MissingPasswordError()

        # Store configuration
        self.config = client_config

        # Set up logging
        self.debug = client_config.debug
        if self.debug:
            logger.setLevel(logging.DEBUG)

        # Initialize auth provider
        self.auth_provider = client_config.auth_provider
        if self.auth_provider is None:
            from dc_api_x.ext.auth.basic import BasicAuthProvider

            self.auth_provider = BasicAuthProvider(
                client_config.username,
                client_config.password,
            )

        # Initialize adapter
        self.adapter = client_config.adapter or self._create_default_http_adapter()

        # Initialize hooks
        self.request_hooks = client_config.request_hooks.copy()
        self.response_hooks = client_config.response_hooks.copy()
        self.api_response_hooks = client_config.api_response_hooks.copy()
        self.error_hooks = client_config.error_hooks.copy()

        # Initialize plugins
        self.plugins: dict[type[apix.ApiPlugin], apix.ApiPlugin] = {}
        for plugin_class in client_config.plugins:
            self.register_plugin(plugin_class)

        # Log initialization
        logger.debug(
            "ApiClient initialized with URL %s and username %s",
            client_config.url,
            client_config.username,
        )

    @property
    def url(self) -> str:
        """Get the base URL for the API.

        Returns:
            The base URL for the API
        """
        return self.config.url

    @property
    def username(self) -> str:
        """Get the username used for authentication.

        Returns:
            The username for API authentication
        """
        return self.config.username

    @property
    def password(self) -> str:
        """Get the password used for authentication.

        Returns:
            The password for API authentication
        """
        if hasattr(self.config.password, "get_secret_value"):
            return self.config.password.get_secret_value()
        return self.config.password

    @property
    def timeout(self) -> int:
        """Get the timeout value for requests.

        Returns:
            The timeout value in seconds
        """
        return self.config.timeout

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
        timeout = config.get("timeout", apix.DEFAULT_TIMEOUT)
        verify_ssl = config.get("verify_ssl", True)
        max_retries = config.get("max_retries", apix.DEFAULT_MAX_RETRIES)
        retry_backoff = config.get("retry_backoff", apix.DEFAULT_RETRY_BACKOFF)
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

    def _create_default_http_adapter(self) -> apix.HttpAdapter:
        """
        Create a default HTTP adapter based on requests.

        Returns:
            HttpAdapter implementation
        """
        from dc_api_x.utils.adapters import RequestsHttpAdapter

        return RequestsHttpAdapter(
            timeout=self.config.timeout,
            verify_ssl=self.config.verify_ssl,
            max_retries=self.config.max_retries,
            retry_backoff=self.config.retry_backoff,
            auth_provider=self.auth_provider,
        )

    def register_plugin(self, plugin_class: type[apix.ApiPlugin]) -> apix.ApiPlugin:
        """
        Register a plugin with the client.

        Args:
            plugin_class: Plugin class to register

        Returns:
            Initialized plugin instance
        """
        plugin = plugin_class(self)
        plugin.initialize()
        self.plugins[plugin_class] = plugin
        return plugin

    def get_plugin(self, plugin_class: type[P]) -> Optional[P]:
        """
        Get a registered plugin by class.

        Args:
            plugin_class: Plugin class to find

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_class)

    def _make_http_request(  # noqa: PLR0912
        self,
        method: str,
        endpoint: str,
        request_config: Optional[RequestConfig] = None,
    ) -> apix.ApiResponse:
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
        for hook in self.request_hooks:
            kwargs = hook(method, url, kwargs)

        # Apply plugin request hooks
        for plugin in self.plugins.values():
            kwargs = plugin.before_request(method, url, kwargs)

        try:
            # Make the request
            response = self.adapter.request(method, url, **kwargs)

            # Apply response hooks (modify response)
            for hook in self.response_hooks:
                response = hook(method, url, response)

            # Apply plugin response hooks
            for plugin in self.plugins.values():
                response = plugin.after_request(method, url, response)

            # Process response
            api_response = self._process_response(response)

            # Apply API response hooks
            for hook in self.api_response_hooks:
                api_response = hook(response, api_response)

            # Apply plugin API response hooks
            for plugin in self.plugins.values():
                api_response = plugin.before_response_processed(response, api_response)

            # Return raw response if requested
            if request_config.raw_response:
                return api_response

            # Handle response errors
            if (
                not api_response.success
                and api_response.status_code is not None
                and api_response.status_code >= apix.HTTP_BAD_REQUEST
            ):
                # Extract error details
                error_msg = (
                    api_response.error or f"API error: {api_response.status_code}"
                )
                error_details = (
                    api_response.data
                    if isinstance(api_response.data, dict[str, Any])
                    else None
                )
                self._handle_error_response(api_response, error_msg, error_details)
            else:
                return api_response

        except (apix.ApiTimeoutError, apix.AuthenticationError):
            # Re-raise API exceptions without wrapping
            raise
        except apix.ApiConnectionError as e:
            # Call error hooks
            for hook in self.error_hooks:
                hook_response = hook(method, url, e, kwargs)
                if hook_response is not None:
                    return hook_response

            # Apply plugin error hooks
            for plugin in self.plugins.values():
                plugin_response = plugin.on_error(method, url, e, kwargs)
                if plugin_response is not None:
                    return plugin_response

            # Re-raise exception
            raise
        except Exception as e:
            # Call error hooks
            for hook in self.error_hooks:
                hook_response = hook(method, url, e, kwargs)
                if hook_response is not None:
                    return hook_response

            # Apply plugin error hooks
            for plugin in self.plugins.values():
                plugin_response = plugin.on_error(method, url, e, kwargs)
                if plugin_response is not None:
                    return plugin_response

            # Wrap exception
            if isinstance(e, requests.Timeout):
                raise exceptions.ConnectionTimeoutError(
                    self.config.timeout,
                    details={"url": url, "method": method},
                ) from e
            if isinstance(e, requests.ConnectionError):
                raise exceptions.ConnectionFailedError(
                    e,
                    details={"url": url, "method": method},
                ) from e
            raise exceptions.RequestFailedError(
                e,
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
    ) -> apix.ApiResponse:
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
    ) -> apix.ApiResponse:
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
    ) -> apix.ApiResponse:
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
    ) -> apix.ApiResponse:
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
    ) -> apix.ApiResponse:
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
        plugins: Optional[list[type[apix.ApiPlugin]]] = None,
        adapter: Optional[apix.HttpAdapter] = None,
        auth_provider: Optional[apix.AuthProvider] = None,
    ) -> ApiClient:
        """
        Create an API client from a profile.

        Args:
            profile_name: Name of the profile to load
            plugins: List of plugin classes to register
            adapter: Custom adapter to use
            auth_provider: Custom auth provider to use

        Returns:
            ApiClient instance

        Raises:
            ConfigError: If profile cannot be loaded
        """
        # Load configuration from profile
        config = Config.from_profile(profile_name)

        # Get password value (could be string or SecretStr)
        password = config.password
        if hasattr(password, "get_secret_value"):
            password = password.get_secret_value()

        # Create client config
        client_config = ClientConfig(
            url=config.url,
            username=config.username,
            password=password,
            timeout=config.timeout,
            verify_ssl=config.verify_ssl,
            max_retries=config.max_retries,
            retry_backoff=config.retry_backoff,
            debug=config.debug,
            plugins=plugins or [],
            adapter=adapter,
            auth_provider=auth_provider,
        )

        # Create and return client
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
            return True, f"Connection successful (status {response.status_code})"
        except apix.ApiError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Connection failed with unexpected error: {str(e)}"

    def execute_query(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> apix.GenericResponse[Any]:
        """
        Execute a database query (requires DatabaseAdapter).

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            GenericResponse with query results
        """
        if not isinstance(self.adapter, apix.DatabaseAdapter):

            def _db_adapter_required_error() -> None:
                return AdapterTypeError(AdapterTypeError.DATABASE_REQUIRED)

            raise _db_adapter_required_error()

        try:
            results = self.adapter.execute(query, params)
            return apix.GenericResponse.success(
                apix.DatabaseResult(
                    success=True,
                    rows=results,
                    query=query,
                    params=params,
                ),
            )
        except ValueError as e:
            return apix.GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )
        except (TypeError, AttributeError) as e:
            return apix.GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )
        except (apix.ClientError, OSError) as e:  # More specific exceptions
            return apix.GenericResponse.error(
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
    ) -> apix.GenericResponse[Any]:
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
        if not isinstance(self.adapter, apix.DirectoryAdapter):

            def _dir_adapter_required_error() -> None:
                return AdapterTypeError(AdapterTypeError.DIRECTORY_REQUIRED)

            raise _dir_adapter_required_error()

        try:
            results = self.adapter.search(base_dn, search_filter, attributes, scope)
            entries = [apix.DirectoryEntry(dn, attrs) for dn, attrs in results]
            return apix.GenericResponse.success(entries)
        except ValueError as e:
            return apix.GenericResponse.error(
                str(e),
                error_code="SEARCH_FAILED",
                error_details={
                    "base_dn": base_dn,
                    "filter": search_filter,
                },
            )
        except (apix.ClientError, OSError) as e:  # More specific exceptions
            return apix.GenericResponse.error(
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
    ) -> apix.GenericResponse[Any]:
        """
        Publish a message (requires MessageQueueAdapter).

        Args:
            topic: Topic to publish to
            message: Message to publish
            **kwargs: Additional parameters

        Returns:
            GenericResponse indicating success or failure
        """
        if not isinstance(self.adapter, apix.MessageQueueAdapter):

            def _mq_adapter_required_error() -> None:
                return AdapterTypeError(AdapterTypeError.MESSAGE_QUEUE_REQUIRED)

            raise _mq_adapter_required_error()

        try:
            self.adapter.publish(topic, message, **kwargs)
            return apix.GenericResponse.success({"topic": topic})
        except ValueError as e:
            return apix.GenericResponse.error(
                str(e),
                error_code="PUBLISH_FAILED",
                error_details={"topic": topic},
            )
        except (apix.ClientError, OSError) as e:  # More specific exceptions
            return apix.GenericResponse.error(
                str(e),
                error_code="PUBLISH_FAILED",
                error_details={"topic": topic},
            )

    def __del__(self) -> None:
        """Clean up resources on object deletion."""
        try:
            if self is not None:
                if hasattr(self, "adapter") and self.adapter is not None:
                    self.adapter.disconnect()
        except (AttributeError, TypeError):
            # Ignore errors during cleanup
            pass

        # Allow plugins to clean up
        if hasattr(self, "plugins"):
            for plugin in self.plugins.values():
                try:
                    plugin.shutdown()
                except (AttributeError, TypeError):
                    if self.debug:
                        logger.exception(
                            "Error shutting down plugin %s",
                            plugin.__class__.__name__,
                        )
                except (apix.ClientError, OSError):  # More specific exceptions
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
        base_url = self.config.url.rstrip("/")
        endpoint_path = endpoint.lstrip("/")
        return f"{base_url}/{endpoint_path}"

    def _process_response(self, response: requests.Response) -> apix.ApiResponse:
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
        success = response.status_code < apix.HTTP_BAD_REQUEST

        if not success:
            # Try to extract error details
            error = None
            error_code = None
            error_details = None

            if isinstance(data, dict[str, Any]):
                # Extract error information from dictionary
                error = data.get("error") or data.get("message") or data.get("msg")
                error_code = data.get("code") or data.get("error_code")
                error_details = data.get("details") or data.get("error_details")

            if not error:
                # Use status code description as fallback
                error = f"HTTP {response.status_code}: {response.reason}"

            # Handle common error status codes
            if response.status_code == apix.HTTP_NOT_FOUND:
                logger.warning("Resource not found: %s", response.url)
            elif response.status_code >= apix.HTTP_INTERNAL_SERVER_ERROR:
                logger.error("Server error: %s", error or response.reason)

            return apix.ApiResponse(
                success=False,
                status_code=response.status_code,
                data=data,
                error=error,
                error_code=error_code,
                error_details=error_details,
            )

        # Successful response
        return apix.ApiResponse(
            success=True,
            status_code=response.status_code,
            data=data,
        )

    def _handle_error_response(
        self,
        api_response: apix.ApiResponse,
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
            and api_response.status_code >= apix.HTTP_BAD_REQUEST
        ):
            # Handle different error types
            if api_response.status_code == apix.HTTP_UNAUTHORIZED:
                raise apix.AuthenticationError(error_msg, error_details)

            raise exceptions.RequestError(
                error_msg,
                details=error_details,
                status_code=api_response.status_code,
            )


class ClientError(apix.ApiError):
    """Base exception for client errors."""


class MissingUrlError(apix.ConfigurationError):
    """Raised when API URL is missing."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("API base URL is required")


class MissingUsernameError(apix.ConfigurationError):
    """Raised when API username is missing."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("API username is required")


class MissingPasswordError(apix.ConfigurationError):
    """Raised when API password is missing."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("API password is required")
