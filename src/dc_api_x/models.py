"""
Base models for DCApiX.

This module provides models for request and response data.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field

# Import constants directly from constants module instead of defining them locally
from .utils.constants import (
    HTTP_BAD_REQUEST,
    HTTP_MULTIPLE_CHOICES,
    HTTP_OK,
    INVALID_JSON_ERROR,
    INVALID_JSON_UTF8_ERROR,
    INVALID_TYPE_ERROR,
)

# Constants
MAX_STRING_PREVIEW_LENGTH = 20


# Exceções personalizadas para tratamento de erros no processamento de conteúdo
class ContentNotJSONError(ValueError):
    """Raised when content cannot be parsed as JSON."""

    def __init__(self, error: Exception) -> None:
        super().__init__(INVALID_JSON_ERROR.format(error))


class ContentNotUTF8Error(ValueError):
    """Raised when content cannot be decoded as UTF-8."""

    def __init__(self, error: Exception) -> None:
        super().__init__(INVALID_JSON_UTF8_ERROR.format(error))


class UnsupportedContentTypeError(ValueError):
    """Raised when content type is not supported for conversion."""

    def __init__(self, content_type: type) -> None:
        super().__init__(INVALID_TYPE_ERROR.format(content_type))


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
            return self.__dict__[field_name]

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
    count: int | None = None
    total: int | None = None
    page: int | None = None
    pages: int | None = None
    next_page: str | None = None
    prev_page: str | None = None

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
    details: dict[str, Any] | None = None
    field: str | None = None
    source: str | None = None


class Error(ConfigurableBase):
    """Error information for API responses."""

    type: str = "error"
    title: str = "Error"
    status: int = HTTP_BAD_REQUEST
    detail: str = ""
    errors: list[ErrorDetail] = Field(default_factory=list)

    def add_error(
        self,
        message: str,
        code: str = "",
        field: str | None = None,
    ) -> None:
        """Add an error detail to the errors list."""
        error_detail = ErrorDetail(code=code, message=message, field=field)
        self.errors.append(error_detail)


class GenericResponse(ConfigurableBase, Generic[T]):
    """Generic API response model that can hold any data type."""

    success: bool = True
    data: T | None = None
    error: Error | None = None
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
        meta: dict[str, Any] | None = None,
    ) -> GenericResponse[T]:
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
        error: str | Error,
        status: int | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> GenericResponse[T]:
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
    query_params: dict[str, Any] | None = None
    headers: dict[str, str] | None = None
    body: Any | None = None
    auth: dict[str, Any] | None = None

    def with_params(self, **params: Any) -> ApiRequest:
        """Return a new request with additional query parameters."""
        new_params = dict(self.query_params or {})
        new_params.update(params)
        return self.model_copy(update={"query_params": new_params})

    def with_headers(self, **headers: str) -> ApiRequest:
        """Return a new request with additional headers."""
        new_headers = dict(self.headers or {})
        new_headers.update(headers)
        return self.model_copy(update={"headers": new_headers})

    def with_body(self, body: Any) -> ApiRequest:
        """Return a new request with a body."""
        return self.model_copy(update={"body": body})

    def with_auth(self, **auth: Any) -> ApiRequest:
        """Return a new request with authentication information."""
        new_auth = dict(self.auth or {})
        new_auth.update(auth)
        return self.model_copy(update={"auth": new_auth})


class DirectoryEntry(ConfigurableBase):
    """Directory entry model for LDAP responses."""

    dn: str
    attributes: dict[str, list[str | bytes]]

    def get_attribute(self, name: str) -> list[str | bytes]:
        """Get a list of values for an attribute."""
        return self.attributes.get(name, [])

    def get_attribute_value(self, name: str) -> str | bytes | None:
        """Get the first value of an attribute or None if not found."""
        values = self.get_attribute(name)
        return values[0] if values else None


class AuthResponse(ConfigurableBase):
    """Authentication response model."""

    authenticated: bool = False
    token: str | None = None
    token_expiration: str | None = None
    username: str | None = None
    user_data: dict[str, Any] | None = None
    error: str | None = None
    error_description: str | None = None

    def is_valid(self) -> bool:
        """Check if the authentication response is valid."""
        return self.authenticated and self.token is not None


class ApiResponse(GenericResponse[dict[str, Any]]):
    """API response model with status code and headers."""

    status_code: int = HTTP_OK
    headers: dict[str, str] = Field(default_factory=dict)
    error_code: str | None = None

    def __init__(self, **data: Any) -> None:
        """Initialize the response with the provided data."""
        super().__init__(**data)
        # Set success flag based on status code if not explicitly set
        if "success" not in data:
            self.success = self.status_code < HTTP_BAD_REQUEST

    @classmethod
    def success(
        cls,
        data: Any,
        status_code: int = HTTP_OK,
        meta: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        """Create a success response.

        Args:
            data: The data to include in the response
            status_code: HTTP status code
            meta: Optional metadata for the response
            headers: Optional HTTP headers

        Returns:
            A successful response with the provided data
        """
        meta_obj = Metadata(**(meta or {}))
        return cls(
            success=True,
            data=data,
            meta=meta_obj,
            status_code=status_code,
            headers=headers or {},
        )

    @classmethod
    def create_success(
        cls,
        data: Any,
        status_code: int = HTTP_OK,
        meta: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        """Create a success response.

        Args:
            data: The data to include in the response
            status_code: HTTP status code
            meta: Optional metadata for the response
            headers: Optional HTTP headers

        Returns:
            A successful response with the provided data

        .. deprecated:: 0.1.0
            Use :meth:`success` instead.
        """
        return cls.success(data, status_code, meta, headers)

    @classmethod
    def error(
        cls,
        error: str | Error,
        status_code: int = HTTP_BAD_REQUEST,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        """Create an error response.

        Args:
            error: Error message or Error object
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            headers: Optional HTTP headers

        Returns:
            An error response with the provided information
        """
        if isinstance(error, str):
            error_obj = Error(detail=error)
            if error_code:
                error_obj.add_error(error, error_code)
            if details and error_obj.errors:
                error_obj.errors[0].details = details
        else:
            error_obj = error

        return cls(
            success=False,
            error=error_obj,
            data=None,
            status_code=status_code,
            headers=headers or {},
            error_code=error_code,
        )

    @classmethod
    def create_error(
        cls,
        error: str | Error,
        status_code: int = HTTP_BAD_REQUEST,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        """Create an error response.

        Args:
            error: Error message or Error object
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            headers: Optional HTTP headers

        Returns:
            An error response with the provided information

        .. deprecated:: 0.1.0
            Use :meth:`error` instead.
        """
        return cls.error(error, status_code, error_code, details, headers)

    def is_success(self) -> bool:
        """Check if the response indicates a successful request.

        Success is determined by status code and the success flag.

        Returns:
            True if the response is successful
        """
        return (
            self.success
            and self.status_code is not None
            and self.status_code >= HTTP_OK
            and self.status_code < HTTP_MULTIPLE_CHOICES
        )

    def __bool__(self) -> bool:
        """Convert the response to a boolean value.

        Returns:
            True if the response is successful, False otherwise
        """
        return self.is_success()

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary.

        Returns:
            Dictionary representation of the response
        """
        result = super().to_dict()
        result["status_code"] = self.status_code
        result["headers"] = self.headers

        # Format data nicely
        if "data" in result and result["data"] is None:
            result["data"] = {}

        # Format error nicely
        if "error" in result and result["error"] is not None:
            if hasattr(result["error"], "to_dict"):
                result["error"] = result["error"].to_dict()
            elif isinstance(result["error"], dict):
                pass  # Already a dict
            else:
                result["error"] = {"message": str(result["error"])}

        return result

    def to_json(self) -> str:
        """Convert the response to a JSON string.

        Returns:
            JSON string representation of the response
        """
        import json

        return json.dumps(self.to_dict())


class QueueMessage:
    """Message for message queue operations."""

    def __init__(
        self,
        content: str | bytes | dict[str, Any],
        topic: str | None = None,
        message_id: str | None = None,
        timestamp: float | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize a new queue message.

        Args:
            content: Message content
            topic: Optional topic or queue name
            message_id: Optional message ID
            timestamp: Optional timestamp
            headers: Optional message headers
        """
        self.content = content
        self.topic = topic
        self.message_id = message_id
        self.timestamp = timestamp or self._get_timestamp()
        self.headers = headers or {}

    def _get_timestamp(self) -> float:
        """Get the current timestamp.

        Returns:
            Current timestamp as a float
        """
        import time

        return time.time()

    def get_content_as_dict(self) -> dict[str, Any]:
        """Get the content as a dictionary.

        If the content is a string, it's parsed as JSON.
        If the content is bytes, it's decoded as UTF-8 and parsed as JSON.
        If the content is already a dictionary, it's returned as is.

        Returns:
            Content as a dictionary

        Raises:
            ContentNotJSONError: If content cannot be parsed as JSON
            ContentNotUTF8Error: If content cannot be decoded as UTF-8
            UnsupportedContentTypeError: If content type is not supported
        """
        if isinstance(self.content, dict):
            return self.content

        if isinstance(self.content, str):
            try:
                import json

                return json.loads(self.content)
            except json.JSONDecodeError as e:
                raise ContentNotJSONError(e) from e

        if isinstance(self.content, bytes):
            try:
                content_str = self.content.decode("utf-8")
                try:
                    import json

                    return json.loads(content_str)
                except json.JSONDecodeError as e:
                    raise ContentNotJSONError(e) from e
            except UnicodeDecodeError as e:
                raise ContentNotUTF8Error(e) from e

        raise UnsupportedContentTypeError(type(self.content))

    def __str__(self) -> str:
        """Convert the message to a string.

        Returns:
            String representation of the message
        """
        if isinstance(self.content, dict):
            content_repr = "..."
        elif isinstance(self.content, str):
            content_repr = (
                self.content[:MAX_STRING_PREVIEW_LENGTH] + "..."
                if len(self.content) > MAX_STRING_PREVIEW_LENGTH
                else self.content
            )
        else:
            content_repr = f"<{type(self.content).__name__}>"

        return (
            f"QueueMessage(topic={self.topic!r}, "
            f"id={self.message_id!r}, "
            f"content={content_repr!r})"
        )
