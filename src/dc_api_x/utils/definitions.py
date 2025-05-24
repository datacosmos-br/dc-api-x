"""
Type definitions for DCApiX.

This module centralizes type definitions used throughout DCApiX,
making it easier to maintain consistent typing and avoid circular imports.
"""

from __future__ import annotations

import datetime
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol, TypeVar, Union, cast

# Import Pydantic for enhanced type validation
from pydantic import (
    BaseModel,
)
from pydantic import (
    ValidationError as PydanticValidationError,
)

# Define type variables for generics
T = TypeVar("T")  # Generic type
R = TypeVar("R")  # Return type
K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type
M = TypeVar("M", bound=BaseModel)  # Pydantic model type

# -------------------------------------------------------
# JSON-related types
# -------------------------------------------------------
JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | dict[str, Any] | list[Any]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

# -------------------------------------------------------
# File and path related types
# -------------------------------------------------------
PathLike = str | Path
FileContent = str | bytes
TextOrBinary = str | bytes

# -------------------------------------------------------
# HTTP-related types
# -------------------------------------------------------
Headers = dict[str, str]
HttpMethod = str  # GET, POST, PUT, DELETE, PATCH, etc.
StatusCode = int
ContentType = str
Cookies = dict[str, str]
BasicAuth = tuple[str, str]  # (username, password)
BearerToken = str
Timeout = (
    int | float | tuple[int | float, int | float]
)  # (connect_timeout, read_timeout)
UserAgent = str

# -------------------------------------------------------
# Request/Response types
# -------------------------------------------------------
UrlParams = dict[str, str | int | float | bool | None]
QueryParams = dict[str, str | int | float | bool | list[str] | None]
FormData = dict[str, str | bytes | None]
RequestData = JsonObject | str | bytes | None
ResponseData = JsonObject | JsonArray | str | bytes | None
MultipartField = tuple[str, str | bytes, str | None]  # (name, content, content_type)
MultipartFormData = list[MultipartField]
OutputFormat = str  # json, yaml, xml, csv, etc.

# -------------------------------------------------------
# Entity-related types
# -------------------------------------------------------
EntityId = str | int
EntityData = JsonObject
EntityList = list[EntityData]
FilterDict = dict[str, Any]
SortOrder = list[tuple[str, bool]]  # [(field_name, is_ascending), ...]
EntityName = str
EntityType = str
EntityAttributes = dict[str, Any]

# -------------------------------------------------------
# Pagination types
# -------------------------------------------------------
PageInfo = dict[str, int]  # {'page': 1, 'page_size': 20, 'total': 100, ...}
PageNumber = int
PageSize = int
TotalCount = int
PaginationParams = dict[str, int]
PaginationMetadata = dict[str, int | str | None]

# -------------------------------------------------------
# Error types
# -------------------------------------------------------
ErrorDetail = dict[str, Any]
ErrorCode = str
ValidationResult = tuple[bool, str | None]  # (is_valid, error_message)
ExceptionInfo = tuple[
    type[Exception],
    Exception,
    Any,
]  # (exc_type, exc_value, traceback)
ErrorResponse = dict[str, Any]

# -------------------------------------------------------
# Transform and validator types
# -------------------------------------------------------
TransformFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[Any], bool]
FormatFunc = Callable[[Any], str]
FilterFunc = Callable[[Any], bool]
MapFunc = Callable[[Any], Any]
ReduceFunc = Callable[[Any, Any], Any]

# -------------------------------------------------------
# Cache related types
# -------------------------------------------------------
CacheKey = str
CacheValue = Any
CacheTTL = int  # Time-to-live in seconds
CacheBackend = str
CacheOptions = dict[str, Any]

# -------------------------------------------------------
# Config related types
# -------------------------------------------------------
ConfigValue = str | int | float | bool | list[Any] | dict[str, Any] | None
ConfigDict = dict[str, ConfigValue]
ConfigFilePath = str | Path
EnvironmentName = str
ProfileName = str

# -------------------------------------------------------
# Database related types
# -------------------------------------------------------
ConnectionString = str
DbEngine = str
DbParams = dict[str, Any]
QueryResult = list[dict[str, Any]]
RowData = dict[str, Any]
SqlQuery = str
TableName = str
ColumnName = str
DbCredentials = dict[str, str]

# -------------------------------------------------------
# Plugin and adapter types
# -------------------------------------------------------
PluginName = str
AdapterName = str
PluginRegistry = dict[str, Any]
AdapterRegistry = dict[str, Any]
ProviderRegistry = dict[str, Any]
HookRegistry = dict[str, Any]

# -------------------------------------------------------
# Schema related types
# -------------------------------------------------------
SchemaDefinition = dict[str, Any]
SchemaType = str
SchemaFormat = str
SchemaField = dict[str, Any]
ValidationSchema = dict[str, Any]

# -------------------------------------------------------
# Callback types
# -------------------------------------------------------
RequestCallback = Callable[[str, str, dict[str, Any]], dict[str, Any]]
ResponseCallback = Callable[[Any, str, str], Any]
ErrorCallback = Callable[[Exception, str, str, dict[str, Any]], None]
SuccessCallback = Callable[[Any], None]
ProgressCallback = Callable[[int, int], None]
CompletionCallback = Callable[[], None]

# -------------------------------------------------------
# Logger types
# -------------------------------------------------------
LogLevel = str
LogHandler = Any
LoggerName = str
LogFormat = str
LogRecord = dict[str, Any]

# -------------------------------------------------------
# Date and time types
# -------------------------------------------------------
DateFormat = str
TimeFormat = str
DatetimeFormat = str
TimeDelta = datetime.timedelta
Timestamp = int | float

# Constants for type checking
DICT_ARG_COUNT = 2  # Number of expected type arguments for Dict[K, V]


def check_type_compatibility(value: Any, type_annotation: Any) -> bool:
    """Check if a value is compatible with a type annotation.

    Args:
        value: Value to check
        type_annotation: Type annotation to check against

    Returns:
        bool: True if value is compatible with the type annotation
    """
    return _check_type_compatibility_impl(value, type_annotation)


def _check_type_compatibility_impl(value: Any, type_annotation: Any) -> bool:
    """Implementation of type compatibility checking logic.

    This internal function contains the actual implementation to reduce
    the number of return statements in the public function.

    Args:
        value: Value to check
        type_annotation: Type annotation to check against

    Returns:
        bool: True if value is compatible with the type annotation
    """
    result = False

    # Handle Any type - always compatible
    if type_annotation is Any:
        result = True
    # Special case for None
    elif value is None:
        # Check if this is Optional[...] or Union[..., None]
        if (
            hasattr(type_annotation, "__origin__")
            and type_annotation.__origin__ is Union
        ):
            result = type(None) in type_annotation.__args__
        else:
            result = type_annotation is type(None)
    # Handle generic types (List, Dict, Union, etc.)
    elif hasattr(type_annotation, "__origin__"):
        origin = type_annotation.__origin__
        args = type_annotation.__args__

        # Handle Union types (including | operator in Python 3.10+)
        if origin is Union or (
            hasattr(types, "UnionType") and origin is types.UnionType
        ):
            result = any(_check_type_compatibility_impl(value, arg) for arg in args)
        # Handle container types
        elif isinstance(value, origin):
            # Handle empty containers
            if not value:
                result = True
            # Handle specific container types
            elif origin is list or origin is tuple:
                element_type = args[0] if len(args) == 1 else args
                result = all(
                    _check_type_compatibility_impl(item, element_type) for item in value
                )
            elif origin is dict and len(args) == DICT_ARG_COUNT:
                # Dict should have exactly 2 type arguments: key and value
                key_type, val_type = args
                keys_compatible = all(
                    _check_type_compatibility_impl(k, key_type) for k in value
                )
                values_compatible = all(
                    _check_type_compatibility_impl(v, val_type) for v in value.values()
                )
                result = keys_compatible and values_compatible
    # Simple case: direct isinstance check
    else:
        result = isinstance(value, type_annotation)

    return result


# -------------------------------------------------------
# Protocol classes for interfaces
# -------------------------------------------------------
class ConnectionProtocol(Protocol):
    """Protocol for connection objects."""

    def connect(self) -> bool:
        """Establish a connection.

        Returns:
            bool: True if connection was successful
        """
        ...

    def disconnect(self) -> bool:
        """Close the connection.

        Returns:
            bool: True if disconnection was successful
        """
        ...

    def is_connected(self) -> bool:
        """Check if connected.

        Returns:
            bool: True if connected
        """
        ...


class TransactionProtocol(Protocol):
    """Protocol for transaction objects."""

    def __enter__(self) -> TransactionProtocol:
        """Enter the transaction context.

        Returns:
            TransactionProtocol: Self
        """
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the transaction context.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        ...

    def commit(self) -> None:
        """Commit the transaction."""
        ...

    def rollback(self) -> None:
        """Rollback the transaction."""
        ...


class AuthProviderProtocol(Protocol):
    """Protocol for authentication providers."""

    def authenticate(self) -> bool:
        """Authenticate with the service.

        Returns:
            bool: True if authentication was successful
        """
        ...

    def is_authenticated(self) -> bool:
        """Check if authenticated.

        Returns:
            bool: True if authenticated
        """
        ...

    def get_auth_header(self) -> Headers:
        """Get authentication headers.

        Returns:
            Headers: Authentication headers
        """
        ...

    def is_token_valid(self) -> bool:
        """Check if token is valid and not expired.

        Returns:
            bool: True if token is valid
        """
        ...

    def refresh_token(self) -> bool:
        """Refresh the authentication token.

        Returns:
            bool: True if token was refreshed successfully
        """
        ...


class EntityProtocol(Protocol):
    """Protocol for entity classes."""

    name: str
    id_field: str

    def get(self, entity_id: EntityId) -> EntityData:
        """Get an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            EntityData: Entity data
        """
        ...

    def list(
        self,
        filters: FilterDict | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> EntityList:
        """List entities.

        Args:
            filters: Filters to apply
            page: Page number
            page_size: Page size

        Returns:
            EntityList: List of entities
        """
        ...

    def create(self, data: EntityData) -> EntityData:
        """Create a new entity.

        Args:
            data: Entity data

        Returns:
            EntityData: Created entity
        """
        ...

    def update(self, entity_id: EntityId, data: EntityData) -> EntityData:
        """Update an entity.

        Args:
            entity_id: Entity ID
            data: Updated entity data

        Returns:
            EntityData: Updated entity
        """
        ...

    def delete(self, entity_id: EntityId) -> bool:
        """Delete an entity.

        Args:
            entity_id: Entity ID

        Returns:
            bool: True if deletion was successful
        """
        ...


class DataProviderProtocol(Protocol):
    """Protocol for data provider objects."""

    def get_data(self, **kwargs: Any) -> ResponseData:
        """Get data from the provider.

        Args:
            **kwargs: Additional parameters for the data request

        Returns:
            ResponseData: Response data
        """
        ...


class RequestHookProtocol(Protocol):
    """Protocol for request hook objects."""

    def process_request(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Process a request before it is sent.

        Args:
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs

        Returns:
            Modified kwargs for the request
        """
        ...


class ResponseHookProtocol(Protocol):
    """Protocol for response hook objects."""

    def process_response(
        self,
        method: str,
        url: str,
        response: Any,
    ) -> Any:
        """Process a response after it is received.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object

        Returns:
            Modified response
        """
        ...


class ErrorHookProtocol(Protocol):
    """Protocol for error hook objects."""

    def process_error(
        self,
        error: Exception,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> None:
        """Process when an error occurs.

        Args:
            error: Exception that occurred
            method: HTTP method
            url: Request URL
            kwargs: Request kwargs
        """
        ...


class ApiResponseHookProtocol(Protocol):
    """Protocol for API response hook objects."""

    def process_response(
        self,
        http_response: Any,
        api_response: Any,
    ) -> Any:
        """Process an API response.

        Args:
            http_response: HTTP response object
            api_response: API response object

        Returns:
            Any: Modified API response
        """
        ...


class SchemaProviderProtocol(Protocol):
    """Protocol for schema provider objects."""

    def get_schema(self, entity_name: str) -> SchemaDefinition | None:
        """Get schema for an entity.

        Args:
            entity_name: Name of the entity

        Returns:
            SchemaDefinition: Schema definition or None if not found
        """
        ...

    def validate(self, entity_name: str, data: EntityData) -> ValidationResult:
        """Validate data against schema.

        Args:
            entity_name: Name of the entity
            data: Data to validate

        Returns:
            ValidationResult: Validation result
        """
        ...


class WebSocketProtocol(Protocol):
    """Protocol for WebSocket adapter objects."""

    def connect_websocket(self, url: str, **kwargs: Any) -> bool:
        """Connect to a WebSocket endpoint.

        Args:
            url: WebSocket URL
            **kwargs: Additional connection parameters

        Returns:
            bool: True if connection was successful
        """
        ...

    def disconnect_websocket(self) -> bool:
        """Disconnect from the WebSocket endpoint.

        Returns:
            bool: True if disconnection was successful
        """
        ...

    def send(self, data: str | bytes | dict[str, Any]) -> bool:
        """Send data through the WebSocket connection.

        Args:
            data: Data to send

        Returns:
            bool: True if send was successful
        """
        ...

    def receive(self, timeout: float | None = None) -> str | bytes | None:
        """Receive data from the WebSocket connection.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Data received or None if no data received
        """
        ...


# -------------------------------------------------------
# Type checking and validation functions
# -------------------------------------------------------
class TypeMismatchError(TypeError):
    """Error raised when a value does not match the expected type."""

    def __init__(self, expected_type: type, actual_type: type) -> None:
        """Initialize the error with expected and actual types.

        Args:
            expected_type: The expected type
            actual_type: The actual type of the value
        """
        super().__init__(
            f"Expected {expected_type.__name__}, got {actual_type.__name__}",
        )


def assert_type(value: Any, expected_type: type[T]) -> T:
    """Assert that a value is of the expected type.

    Args:
        value: Value to check
        expected_type: Expected type

    Returns:
        The value, typed as the expected type

    Raises:
        TypeMismatchError: If the value is not of the expected type
    """
    if not isinstance(value, expected_type):
        raise TypeMismatchError(expected_type, type(value))
    return cast(T, value)


def validate_with_pydantic(data: Any, model_cls: type[M]) -> tuple[bool, M | str]:
    """Validate data against a Pydantic model.

    Args:
        data: Data to validate
        model_cls: Pydantic model class

    Returns:
        tuple: (is_valid, model_instance or error_message)
    """
    try:
        model_instance = model_cls.model_validate(data)
    except PydanticValidationError as e:
        return False, str(e)
    else:
        return True, model_instance


# -------------------------------------------------------
# Protocol aliases for backward compatibility - these match the actual implementations
# -------------------------------------------------------

# The type annotations used in __init__.py and imported by client code
# We're using a naming pattern to distinguish between the protocol (typing)
# and implementation versions to prevent conflicts
ApiResponseHook = ApiResponseHookProtocol  # For type checking compatibility
ErrorHook = ErrorHookProtocol  # For type checking compatibility
RequestHook = RequestHookProtocol  # For type checking compatibility
ResponseHook = ResponseHookProtocol  # For type checking compatibility
