"""
Base models for DCApiX.

This module provides models for request and response data.
"""

from typing import Any, Generic, Optional, TypeVar, Union, cast

from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field

# Import constants directly from constants module instead of defining them locally
from .constants import (
    HTTP_BAD_REQUEST,
    HTTP_MULTIPLE_CHOICES,
    HTTP_OK,
)


# Exceções personalizadas para tratamento de erros no processamento de conteúdo
class ContentNotJSONError(ValueError):
    """Raised when content cannot be parsed as JSON."""

    def __init__(self, error: Exception) -> None:
        super().__init__(f"Content is not valid JSON: {error}")


class ContentNotUTF8Error(ValueError):
    """Raised when content cannot be decoded as UTF-8."""

    def __init__(self, error: Exception) -> None:
        super().__init__(f"Content is not valid JSON or UTF-8: {error}")


class UnsupportedContentTypeError(ValueError):
    """Raised when content type is not supported for conversion."""

    def __init__(self, content_type: type) -> None:
        super().__init__(f"Cannot convert content of type {content_type} to dict")


# Exportar PydanticBaseModel como BaseModel para compatibilidade com os testes
class BaseModel(PydanticBaseModel):
    """Base model with additional utility methods."""

    def get(self, field_name: str, default: Any = None) -> Any:
        """Get a field value by name (case-insensitive).

        Args:
            field_name: Field name to get
            default: Default value if field is not found

        Returns:
            Field value or default if not found
        """
        # Try exact match first
        if field_name in self.__dict__:
            self.__dict__[field_name]

        # Try case-insensitive match
        field_name_lower = field_name.lower()
        for key in self.__dict__:
            if key.lower() == field_name_lower:
                return self.__dict__[key]

        return default

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary.

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump()

    def to_json(self) -> str:
        """Convert the model to a JSON string.

        Returns:
            JSON string representation of the model
        """
        import json

        return json.dumps(self.to_dict())


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class ConfigurableBase(PydanticBaseModel):
    """Base class for configurable models with support for custom settings."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        populate_by_name=True,
        frozen=False,
    )


class Metadata(ConfigurableBase):
    """Metadata information for API responses."""

    version: str = "1.0.0"
    timestamp: str = ""
    count: Optional[int] = None
    total: Optional[int] = None
    page: Optional[int] = None
    pages: Optional[int] = None
    next_page: Optional[str] = None
    prev_page: Optional[str] = None

    @property
    def has_more(self) -> bool:
        """Check if there are more pages available."""
        if self.page is None or self.pages is None:
            return False
        return self.page < self.pages


class ErrorDetail(ConfigurableBase):
    """Detailed error information."""

    code: str = ""
    message: str = ""
    details: Optional[dict[str, Any]] = None
    field: Optional[str] = None
    source: Optional[str] = None


class Error(ConfigurableBase):
    """Error information for API responses."""

    type: str = "error"
    title: str = "Error"
    status: int = HTTP_BAD_REQUEST
    detail: str = ""
    errors: list[ErrorDetail] = Field(default_factory=list[Any])

    def add_error(
        self,
        message: str,
        code: str = "",
        field: Optional[str] = None,
    ) -> None:
        """Add an error detail to the errors list."""
        error_detail = ErrorDetail(code=code, message=message, field=field)
        self.errors.append(error_detail)


class GenericResponse(ConfigurableBase, Generic[T]):
    """Generic API response model that can hold any data type."""

    success: bool = True
    data: Optional[T] = None
    error: Optional[Error] = None
    meta: Metadata = Field(default_factory=Metadata)

    def __init__(self, **data: Any) -> None:
        """Initialize the response with the provided data."""
        super().__init__(**data)
        self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default values for the response."""
        if self.error and not self.data:
            self.success = False

        # Create metadata if not provided
        if not self.meta:
            self.meta = Metadata()

        # Create empty error object if success is False but no error is provided
        if not self.success and not self.error:
            self.error = Error()

    @classmethod
    def from_data(
        cls,
        data: T,
        meta: Optional[dict[str, Any]] = None,
    ) -> "GenericResponse[T]":
        """Create a success response from data.

        Args:
            data: The data to include in the response
            meta: Optional metadata for the response

        Returns:
            A successful response with the provided data
        """
        meta_obj = Metadata(**(meta or {}))
        return cls(success=True, data=data, meta=meta_obj)

    @classmethod
    def from_error(
        cls,
        error: Union[str, Error],
        status: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> "GenericResponse[T]":
        """Create an error response.

        Args:
            error: Error message or Error object
            status: HTTP status code (default: 400)
            error_code: Application-specific error code
            details: Additional error details

        Returns:
            An error response with the provided information
        """
        if isinstance(error, str):
            error_obj = Error(detail=error)
            if status is not None:
                error_obj.status = status
            if error_code:
                error_obj.add_error(error, error_code)
            if details and error_obj.errors:
                error_obj.errors[0].details = details
        else:
            error_obj = error

        return cls(success=False, error=error_obj, data=None)


class ApiRequest(ConfigurableBase):
    """API request model with method, path, query parameters, and headers."""

    method: str = "GET"
    path: str = "/"
    query_params: Optional[dict[str, Any]] = None
    headers: Optional[dict[str, str]] = None
    body: Optional[Any] = None
    auth: Optional[dict[str, Any]] = None

    def with_params(self, **params: Any) -> "ApiRequest":
        """Return a new request with additional query parameters."""
        new_params = dict(self.query_params or {})
        new_params.update(params)
        return self.model_copy(update={"query_params": new_params})

    def with_headers(self, **headers: str) -> "ApiRequest":
        """Return a new request with additional headers."""
        new_headers = dict(self.headers or {})
        new_headers.update(headers)
        return self.model_copy(update={"headers": new_headers})

    def with_body(self, body: Any) -> "ApiRequest":
        """Return a new request with the specified body."""
        return self.model_copy(update={"body": body})

    def with_auth(self, **auth: Any) -> "ApiRequest":
        """Return a new request with the specified authentication."""
        new_auth = dict(self.auth or {})
        new_auth.update(auth)
        return self.model_copy(update={"auth": new_auth})


class DirectoryEntry(ConfigurableBase):
    """Directory entry model for LDAP responses."""

    dn: str
    attributes: dict[str, list[Union[str, bytes]]]

    def get_attribute(self, name: str) -> list[Union[str, bytes]]:
        """Get attribute values by name."""
        return self.attributes.get(name, [])

    def get_attribute_value(self, name: str) -> Optional[Union[str, bytes]]:
        """Get the first value of an attribute."""
        values = self.get_attribute(name)
        return values[0] if values else None


class AuthResponse(ConfigurableBase):
    """Authentication response model."""

    authenticated: bool = False
    token: Optional[str] = None
    token_expiration: Optional[str] = None
    username: Optional[str] = None
    user_data: Optional[dict[str, Any]] = None

    def is_valid(self) -> bool:
        """Check if the authentication response is valid."""
        return self.authenticated and self.token is not None


class ApiResponse(GenericResponse[dict[str, Any]]):
    """API response model with status code and headers."""

    status_code: int = HTTP_OK
    headers: dict[str, str] = Field(default_factory=dict[str, Any])

    def __init__(self, **data: Any) -> None:
        """Initialize the response with the provided data."""
        # Convert string error to Error object
        if "error" in data and isinstance(data["error"], str):
            data["error"] = Error(detail=data["error"])
        super().__init__(**data)

    @classmethod
    def create_success(
        cls,
        data: Any,
        status_code: int = HTTP_OK,
        meta: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> "ApiResponse":
        """Create a success response.

        Args:
            data: The data to include in the response
            status_code: HTTP status code (default: 200)
            meta: Optional metadata for the response
            headers: Optional response headers

        Returns:
            A successful API response with the provided data
        """
        if not meta:
            meta = {}

        # Set count if data is a list
        if isinstance(data, list[Any]) and "count" not in meta:
            meta["count"] = len(data)

        response = cls.from_data(data, meta)
        response.status_code = status_code
        response.headers = headers or {}
        return response

    @classmethod
    def create_error(
        cls,
        error: Union[str, Error],
        status_code: int = HTTP_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> "ApiResponse":
        """Create an error response.

        Args:
            error: Error message or Error object
            status_code: HTTP status code (default: 400)
            error_code: Application-specific error code
            details: Additional error details
            headers: Optional response headers

        Returns:
            An error API response with the provided information
        """
        response = cast(
            ApiResponse,
            cls.from_error(error, status_code, error_code, details),
        )
        response.status_code = status_code
        response.headers = headers or {}

        # Set error status to match response status code if not already set
        if response.error and response.error.status != status_code:
            response.error.status = status_code

        return response

    def is_success(self) -> bool:
        """Check if the response is successful.

        A successful response has:
        - success flag set to True
        - status code in the 2xx range (200-299)

        Returns:
            True if the response is successful, False otherwise
        """
        return self.success and HTTP_OK <= self.status_code < HTTP_MULTIPLE_CHOICES

    def __bool__(self) -> bool:
        """
        Convert to boolean.

        A response is considered "truthy" if it is successful.

        Returns:
            True if the response is successful, False otherwise
        """
        return self.is_success()

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary.

        Returns:
            Dictionary representation of the response
        """
        result = {
            "success": self.success,
            "meta": self.meta.model_dump() if self.meta else {},
        }

        # Add data or error based on response type
        if self.success and self.data is not None:
            if isinstance(self.data, dict[str, Any]):
                result["data"] = self.data
            elif hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            elif hasattr(self.data, "model_dump"):
                result["data"] = self.data.model_dump()
            else:
                result["data"] = self.data
        elif self.error:
            result["error"] = self.error.model_dump()

        return result

    def to_json(self) -> str:
        """Convert the response to a JSON string.

        Returns:
            JSON string representation of the response
        """
        import json

        return json.dumps(self.to_dict())


class QueueMessage:
    """Queue message model for message queue operations."""

    def __init__(
        self,
        content: Union[str, bytes, dict[str, Any]],
        topic: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize the queue message.

        Args:
            content: Message content
            topic: Message topic or queue name
            message_id: Unique message identifier
            timestamp: Message timestamp (default: current time)
            headers: Message headers
        """
        self.content = content
        self.topic = topic
        self.message_id = message_id
        self.timestamp = timestamp or self._get_timestamp()
        self.headers = headers or {}

    def _get_timestamp(self) -> float:
        """Get current timestamp in seconds since epoch.

        Returns:
            Current timestamp
        """
        import time

        return time.time()

    def get_content_as_dict(self) -> dict[str, Any]:
        """Get message content as a dictionary.

        Returns:
            Content as dictionary

        Raises:
            ContentNotJSONError: If content cannot be parsed as JSON
            ContentNotUTF8Error: If content cannot be decoded as UTF-8
            UnsupportedContentTypeError: If content type is not supported
        """
        import json

        if isinstance(self.content, dict[str, Any]):
            return self.content

        if isinstance(self.content, str):
            try:
                return json.loads(self.content)
            except json.JSONDecodeError as e:
                raise ContentNotJSONError(e) from e

        if isinstance(self.content, bytes):
            try:
                return json.loads(self.content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise ContentNotUTF8Error(e) from e

        raise UnsupportedContentTypeError(type(self.content))

    def __str__(self) -> str:
        """Return string representation of the message."""
        if isinstance(self.content, dict[str, Any]):
            content_str = str(self.content)
        elif isinstance(self.content, bytes):
            content_str = f"bytes[{len(self.content)}]"
        else:
            content_str = str(self.content)

        return f"QueueMessage(topic={self.topic}, id={self.message_id}, content={content_str})"
