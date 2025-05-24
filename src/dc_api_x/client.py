"""
API client for DCApiX.

This module provides the main ApiClient class that allows interacting with APIs.
"""

from dataclasses import dataclass, field
from typing import Any, TypeVar

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError

from .config import Config
from .ext.adapters import (
    HttpAdapter,
)
from .ext.hooks import (
    ApiResponseHook,
    ErrorHook,
    RequestHook,
    ResponseHook,
)
from .models import ApiResponse, GenericResponse
from .utils import (
    exceptions,
    logging,
)
from .utils.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
    MISSING_PASSWORD_ERROR,
    MISSING_URL_ERROR,
    MISSING_USERNAME_ERROR,
)
from .utils.definitions import (
    Headers,
    JsonObject,
)
from .utils.exceptions import ApiError, ConfigurationError

# Create logger using our unified logging module
logger = logging.get_logger(__name__)

# Define TypeVar for plugin type hints
P = TypeVar("P", bound="ApiPlugin")

# Use import alias for self-reference to avoid circular imports


@dataclass
class ClientConfig:
    """Configuration for API client initialization.

    This class holds all the configuration parameters for ApiClient to reduce
    the number of parameters in the constructor.
    """

    # Connection settings
    url: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int = DEFAULT_TIMEOUT
    verify_ssl: bool = True

    # Retry settings
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF

    # Debug mode
    debug: bool = False

    # Configuration object
    config: Config | None = None

    # Extensions
    plugins: list[type["ApiPlugin"]] = field(default_factory=list)
    adapter: Any | None = None  # Type ProtocolAdapter
    auth_provider: Any | None = None  # Type AuthProvider

    # Hooks
    request_hooks: list[RequestHook] = field(default_factory=list)
    response_hooks: list[ResponseHook] = field(default_factory=list)
    api_response_hooks: list[ApiResponseHook] = field(default_factory=list)
    error_hooks: list[ErrorHook] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls,
        config_dict: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "ClientConfig":
        """Create a ClientConfig from a dictionary and/or keyword arguments.

        Args:
            config_dict: Dictionary containing configuration parameters
            **kwargs: Additional parameters that override config_dict values

        Returns:
            ClientConfig object
        """
        # Start with empty dict if None provided
        config = config_dict or {}

        # Override with kwargs
        config.update(kwargs)

        # Extract basic parameters
        url = config.get("url")
        username = config.get("username")
        password = config.get("password")
        timeout = config.get("timeout", DEFAULT_TIMEOUT)
        verify_ssl = config.get("verify_ssl", True)
        max_retries = config.get("max_retries", DEFAULT_MAX_RETRIES)
        retry_backoff = config.get("retry_backoff", DEFAULT_RETRY_BACKOFF)
        debug = config.get("debug", False)
        cfg = config.get("config")

        # Extract extension parameters
        plugins = config.get("plugins", [])
        adapter = config.get("adapter")
        auth_provider = config.get("auth_provider")

        # Extract hook parameters
        request_hooks = config.get("request_hooks", [])
        response_hooks = config.get("response_hooks", [])
        api_response_hooks = config.get("api_response_hooks", [])
        error_hooks = config.get("error_hooks", [])

        return cls(
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


@dataclass
class InitParams:
    """Parameters for ApiClient initialization.

    This class helps reduce the number of parameters in the ApiClient constructor.
    """

    url: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int = DEFAULT_TIMEOUT
    verify_ssl: bool = True
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF
    debug: bool = False

    def apply_to_config(self, config: ClientConfig) -> None:
        """Apply these parameters to a ClientConfig object.

        Args:
            config: The configuration to update
        """
        # Apply non-None values
        if self.url is not None:
            config.url = self.url
        if self.username is not None:
            config.username = self.username
        if self.password is not None:
            config.password = self.password

        # Apply non-default values
        if self.timeout != DEFAULT_TIMEOUT:
            config.timeout = self.timeout
        if not self.verify_ssl:
            config.verify_ssl = self.verify_ssl
        if self.max_retries != DEFAULT_MAX_RETRIES:
            config.max_retries = self.max_retries
        if self.retry_backoff != DEFAULT_RETRY_BACKOFF:
            config.retry_backoff = self.retry_backoff
        if self.debug:
            config.debug = self.debug


@dataclass
class RequestConfig:
    """Configuration for HTTP requests.

    This class holds the parameters for making HTTP requests to reduce
    the number of parameters in HTTP methods.
    """

    # Request data
    params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    json_data: JsonObject | None = None
    headers: Headers | None = None
    files: dict[str, Any] | None = None

    # Response handling
    raw_response: bool = False

    # Extra keyword arguments
    extra_kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        config_dict: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "RequestConfig":
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


# Forward declare ApiClient for type annotations
class ApiClient:
    """API client for making HTTP requests."""


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
    ) -> ApiResponse | None:
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


# Redefine the ApiClient class with the actual implementation
class ApiClient:
    """
    API client for making HTTP requests.

    This client handles authentication, request/response processing, and
    error handling for API interactions.
    """

    def __init__(
        self,
        client_config: ClientConfig | None = None,
        *,  # Make remaining parameters keyword-only
        params: InitParams | None = None,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """
        Initialize the API client.

        Args:
            client_config: Configuration for the client
            params: Initialization parameters (alternative to individual parameters)
            url: API base URL (overrides client_config and params)
            username: API username (overrides client_config and params)
            password: API password (overrides client_config and params)
        """
        # Create or update the configuration
        self.config = self._initialize_config(
            client_config,
            params,
            url,
            username,
            password,
        )

        # Set up logging
        self.debug = self.config.debug
        if self.debug:
            logger.setLevel(logging.DEBUG)

        # Initialize auth provider
        self.auth_provider = self.config.auth_provider
        if self.auth_provider is None:
            from dc_api_x.ext.auth.basic import BasicAuthProvider

            self.auth_provider = BasicAuthProvider(
                self.config.username,
                self.config.password,
            )

        # Initialize adapter
        self.adapter = self.config.adapter or self._create_default_http_adapter()

        # Initialize hooks
        self.request_hooks = self.config.request_hooks.copy()
        self.response_hooks = self.config.response_hooks.copy()
        self.api_response_hooks = self.config.api_response_hooks.copy()
        self.error_hooks = self.config.error_hooks.copy()

        # Initialize plugins
        self.plugins: dict[type[ApiPlugin], ApiPlugin] = {}
        for plugin_class in self.config.plugins:
            self.register_plugin(plugin_class)

        # Log initialization
        logger.debug(
            "ApiClient initialized with URL %s and username %s",
            self.config.url,
            self.config.username,
        )

    def _initialize_config(
        self,
        client_config: ClientConfig | None,
        params: InitParams | None,
        url: str | None,
        username: str | None,
        password: str | None,
    ) -> ClientConfig:
        """Initialize and validate the client configuration.

        Args:
            client_config: Base configuration or None
            params: Additional parameters to apply
            url: URL to override
            username: Username to override
            password: Password to override

        Returns:
            Complete ClientConfig with all settings

        Raises:
            MissingUrlError: If URL is missing
            MissingUsernameError: If username is missing
            MissingPasswordError: If password is missing
        """
        # Start with client_config if provided, otherwise create new one
        config = client_config or ClientConfig()

        # Apply params if provided
        if params is not None:
            params.apply_to_config(config)

        # Apply direct overrides (highest priority)
        if url is not None:
            config.url = url
        if username is not None:
            config.username = username
        if password is not None:
            config.password = password

        # Validate required parameters
        if config.url is None:
            raise MissingUrlError()
        if config.username is None:
            raise MissingUsernameError()
        if config.password is None:
            raise MissingPasswordError()

        return config

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
        config_dict: dict[str, Any] | None = None,
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
        from dc_api_x.ext.adapters import RequestsHttpAdapter

        return RequestsHttpAdapter(
            timeout=self.config.timeout,
            verify_ssl=self.config.verify_ssl,
            max_retries=self.config.max_retries,
            retry_backoff=self.config.retry_backoff,
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
        self.plugins[plugin_class] = plugin
        return plugin

    def get_plugin(self, plugin_class: type[P]) -> P | None:
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
        request_config: RequestConfig | None = None,
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
        kwargs = self._prepare_request_kwargs(request_config)

        # Use Logfire context for request tracing
        with logging.with_tags(
            method=method,
            url=url,
            endpoint=endpoint,
            params=request_config.params,
        ):
            # Debug logging
            self._log_request_debug(method, url, kwargs)

            # Apply request hooks and plugin hooks
            kwargs = self._apply_request_hooks(method, url, kwargs)

            try:
                # Make the request and process response
                response = self._perform_request(method, url, kwargs)
                api_response = self._process_request_response(method, url, response)

                # Return raw response if requested
                if request_config.raw_response:
                    return api_response

                # Handle error responses
                if self._is_error_response(api_response):
                    self._handle_error_response_with_logging(api_response)
                else:
                    return api_response

            except self._get_connection_exceptions() as e:
                return self._handle_connection_error(method, url, e, kwargs)

    def _prepare_request_kwargs(self, request_config: RequestConfig) -> dict[str, Any]:
        """Prepare request kwargs from config.

        Args:
            request_config: Request configuration

        Returns:
            Dict of request kwargs with None values filtered out
        """
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
        return {k: v for k, v in kwargs.items() if v is not None}

    def _log_request_debug(self, method: str, url: str, kwargs: dict[str, Any]) -> None:
        """Log debug information about the request.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs
        """
        if not self.debug:
            return

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
        # Log with Logfire
        logging.debug(
            f"Making {method} request",
            endpoint=url,
            client_id=id(self),
        )

    def _apply_request_hooks(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply request hooks to modify request parameters.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified kwargs after applying hooks
        """
        # Apply request hooks (modify kwargs)
        for hook in self.request_hooks:
            kwargs = hook(method, url, kwargs)

        # Apply plugin request hooks
        for plugin in self.plugins.values():
            kwargs = plugin.before_request(method, url, kwargs)

        return kwargs

    def _perform_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> requests.Response:
        """Perform the actual HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            HTTP response
        """
        # Use RequestTimer for performance tracking
        with logging.RequestTimer(method, url):
            # Make the request
            return self.adapter.request(method, url, **kwargs)

    def _process_request_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
    ) -> ApiResponse:
        """Process the HTTP response.

        Args:
            method: HTTP method
            url: Request URL
            response: HTTP response

        Returns:
            Processed API response
        """
        # Apply response hooks (modify response)
        for hook in self.response_hooks:
            response = hook(method, url, response)

        # Apply plugin response hooks
        for plugin in self.plugins.values():
            response = plugin.after_request(method, url, response)

        # Process response
        api_response = self._process_response(response)

        # Log response
        logging.debug(
            f"Received {method} response",
            status_code=api_response.status_code,
            success=api_response.success,
        )

        # Apply API response hooks
        for hook in self.api_response_hooks:
            api_response = hook(response, api_response)

        # Apply plugin API response hooks
        for plugin in self.plugins.values():
            api_response = plugin.before_response_processed(
                response,
                api_response,
            )

        return api_response

    def _is_error_response(self, api_response: ApiResponse) -> bool:
        """Check if an API response indicates an error.

        Args:
            api_response: API response to check

        Returns:
            True if the response indicates an error
        """
        return (
            not api_response.success
            and api_response.status_code is not None
            and api_response.status_code >= HTTP_BAD_REQUEST
        )

    def _handle_error_response_with_logging(
        self,
        api_response: ApiResponse,
    ) -> None:
        """Handle error responses from the API with proper logging.

        Args:
            api_response: Error API response

        Raises:
            Various API exceptions based on the error
        """
        # Extract error details
        error_msg = api_response.error or f"API error: {api_response.status_code}"
        error_details = (
            api_response.data if isinstance(api_response.data, dict[str, Any]) else None
        )

        # Log the error
        logging.error(
            "API error response",
            status_code=api_response.status_code,
            error=error_msg,
        )

        self._handle_error_response(api_response, error_msg, error_details)

    def _get_connection_exceptions(self) -> tuple[type[Exception], ...]:
        """Get the exception types to catch for connection errors.

        Returns:
            Tuple of exception types
        """
        # Import locally to avoid circular imports
        from dc_api_x.utils.exceptions import (
            ApiConnectionError,
            ApiTimeoutError,
            AuthenticationError,
        )

        return (
            ApiTimeoutError,
            AuthenticationError,
            ApiConnectionError,
            RequestsConnectionError,
            TimeoutError,
            OSError,
        )

    def _handle_connection_error(
        self,
        method: str,
        url: str,
        e: Exception,
        kwargs: dict[str, Any],
    ) -> ApiResponse:
        """Handle connection errors with proper logging and hooks.

        Args:
            method: HTTP method
            url: Request URL
            e: Exception that occurred
            kwargs: Request kwargs

        Returns:
            API response if a hook provides one, otherwise re-raises the exception

        Raises:
            The original exception if no hook handles it
        """
        # Import locally to avoid circular imports
        from dc_api_x.utils.exceptions import (
            ApiConnectionError,
            ApiTimeoutError,
            AuthenticationError,
            ConnectionFailedError,
            ConnectionTimeoutError,
            RequestFailedError,
        )

        # Special handling for API-specific exceptions
        if isinstance(e, ApiTimeoutError | AuthenticationError):
            # Log with Logfire
            logging.exception(
                "API request exception",
                error_type=type(e).__name__,
                error=str(e),
            )
            # Re-raise API exceptions without wrapping
            raise e  # Explicitly re-raise the caught exception

        # Log with Logfire
        logging.exception(
            (
                "API connection error"
                if isinstance(e, ApiConnectionError)
                else "Unexpected API error"
            ),
            error_type=type(e).__name__,
            error=str(e),
        )

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

        # Re-raise exception with proper wrapping if needed
        if isinstance(e, requests.Timeout):
            raise ConnectionTimeoutError(
                self.config.timeout,
                details={"url": url, "method": method},
            ) from e
        if isinstance(e, requests.ConnectionError):
            raise ConnectionFailedError(
                e,
                details={"url": url, "method": method},
            ) from e

        # For other exceptions
        raise RequestFailedError(
            e,
            details={"url": url, "method": method},
        ) from e

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: Headers | None = None,
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
        params: dict[str, Any] | None = None,
        headers: Headers | None = None,
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
        plugins: list[type[ApiPlugin]] | None = None,
        adapter: HttpAdapter | None = None,
        auth_provider: Any | None = None,  # Type: AuthProvider
    ) -> ApiClient:
        """
        Create an ApiClient from a profile.

        Profiles can be defined as environment variables or .env files.
        Profile-specific variables are loaded from .env.{profile_name} file.

        Args:
            profile_name: Name of the profile to load
            plugins: List of plugin classes to register
            adapter: HTTP adapter to use
            auth_provider: Authentication provider to use

        Returns:
            Configured ApiClient instance

        Raises:
            ConfigurationError: If required config is missing
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
        Test the connection to the API.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Try a simple request to test connection
            response = self.get("ping", raw_response=True)
        except exceptions.ApiError as e:
            return False, f"Connection failed: {str(e)}"
        except (RequestsConnectionError, TimeoutError, OSError) as e:
            # Handle specific network-related exceptions
            return False, f"Connection failed with network error: {str(e)}"
        else:
            return True, f"Connection successful (status {response.status_code})"

    def execute_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> GenericResponse[Any]:
        """
        Execute a database query (requires DatabaseAdapter).

        Args:
            query: Query to execute
            params: Query parameters

        Returns:
            GenericResponse with query results
        """
        from .ext.adapters import DatabaseAdapter

        if not isinstance(self.adapter, DatabaseAdapter):

            def _db_adapter_required_error() -> None:
                return AdapterTypeError(AdapterTypeError.DATABASE_REQUIRED)

            raise _db_adapter_required_error()

        try:
            results = self.adapter.execute(query, params)
            from . import DatabaseResult

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
        except (exceptions.ClientError, OSError) as e:  # More specific exceptions
            return GenericResponse.error(
                str(e),
                error_code="QUERY_FAILED",
                error_details={"query": query, "params": params},
            )

    def search_directory(
        self,
        base_dn: str,
        search_filter: str,
        attributes: list[str] | None = None,
        scope: str = "subtree",
    ) -> GenericResponse[Any]:
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
        from .ext.adapters import DirectoryAdapter
        from .models import DirectoryEntry

        if not isinstance(self.adapter, DirectoryAdapter):

            def _dir_adapter_required_error() -> None:
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
        except (exceptions.ClientError, OSError) as e:  # More specific exceptions
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
        message: str | bytes | dict[str, Any],
        **kwargs: Any,
    ) -> GenericResponse[Any]:
        """
        Publish a message (requires MessageQueueAdapter).

        Args:
            topic: Topic to publish to
            message: Message to publish
            **kwargs: Additional parameters

        Returns:
            GenericResponse indicating success or failure
        """
        from .ext.adapters import MessageQueueAdapter

        if not isinstance(self.adapter, MessageQueueAdapter):

            def _mq_adapter_required_error() -> None:
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
        except (exceptions.ClientError, OSError) as e:  # More specific exceptions
            return GenericResponse.error(
                str(e),
                error_code="PUBLISH_FAILED",
                error_details={"topic": topic},
            )

    def __del__(self) -> None:
        """Clean up resources on object deletion."""
        try:
            # Combine nested ifs into a single condition
            if (
                self is not None
                and hasattr(self, "adapter")
                and self.adapter is not None
            ):
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
                except (exceptions.ClientError, OSError):  # More specific exceptions
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

            if isinstance(data, dict[str, Any]):
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
        error_details: dict[str, Any] | None,
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
                raise exceptions.AuthenticationError(error_msg, error_details)

            raise exceptions.RequestError(
                error_msg,
                details=error_details,
                status_code=api_response.status_code,
            )


class ClientError(ApiError):
    """Base class for client-specific errors."""


class MissingUrlError(ConfigurationError):
    """Raised when URL is required but missing."""

    def __init__(self) -> None:
        super().__init__(MISSING_URL_ERROR)


class MissingUsernameError(ConfigurationError):
    """Raised when username is required but missing."""

    def __init__(self) -> None:
        super().__init__(MISSING_USERNAME_ERROR)


class MissingPasswordError(ConfigurationError):
    """Raised when password is required but missing."""

    def __init__(self) -> None:
        super().__init__(MISSING_PASSWORD_ERROR)
