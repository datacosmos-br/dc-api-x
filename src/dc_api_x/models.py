"""
Data models for DCApiX.

This module provides base classes for data models with validation.
"""

from typing import (
    Any,
    Generic,
    Optional,
    TypeVar,
    Union,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field

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
    status: int = 400
    detail: str = ""
    errors: list[ErrorDetail] = Field(default_factory=list)

    def add_error(
        self,
        message: str,
        code: str = "",
        field: Optional[str] = None,
    ) -> None:
        """Add an error detail to the errors list."""
        error_detail = ErrorDetail(code=code, message=message, field=field)
        self.errors.append(error_detail)


class GenericResponse(Generic[T], ConfigurableBase):
    """Generic API response model that can hold any data type."""

    success: bool = True
    data: Optional[T] = None
    error: Optional[Error] = None
    meta: Metadata = Field(default_factory=Metadata)

    def __init__(self, **data: Any):
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

    status_code: int = 200
    headers: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        data: Any,
        status_code: int = 200,
        meta: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> "ApiResponse":
        """Create a success response.

        Args:
            data: Response data
            status_code: HTTP status code
            meta: Response metadata
            headers: Response headers

        Returns:
            A successful API response
        """
        response = cls.from_data(data, meta)
        response.status_code = status_code
        if headers:
            response.headers = headers
        return response

    @classmethod
    def create_error(
        cls,
        error: Union[str, Error],
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> "ApiResponse":
        """Create an error response.

        Args:
            error: Error message or Error object
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            headers: Response headers

        Returns:
            An error API response
        """
        if isinstance(error, str):
            error_obj = Error(
                detail=error,
                status=status_code,
            )
            if error_code:
                error_obj.add_error(error, error_code)
            if details and error_obj.errors:
                error_obj.errors[0].details = details
        else:
            error_obj = error

        response = cls(
            data=None,
            meta=Metadata(),
            success=False,
            error=error_obj,
            status_code=status_code,
            headers=headers or {},
        )
        
        return response

    def is_success(self) -> bool:
        """Check if the response is successful.

        Returns:
            True if the response is successful, False otherwise
        """
        return self.success and 200 <= self.status_code < 300

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary.

        Returns:
            Dictionary representation of the response
        """
        error_dict = None
        if self.error:
            error_dict = self.error.model_dump()

        return {
            "data": self.data,
            "meta": self.meta or {},
            "success": self.success,
            "error": error_dict,
        }

    def to_json(self) -> str:
        """Convert the response to a JSON string.

        Returns:
            JSON string representation of the response
        """
        import json

        return json.dumps(self.to_dict())


class QueueMessage:
    """
    Message queue message.
    """

    def __init__(
        self,
        content: Union[str, bytes, dict[str, Any]],
        topic: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        """
        Initialize QueueMessage.

        Args:
            content: Message content
            topic: Topic the message was published to
            message_id: Message ID
            timestamp: Message timestamp
            headers: Message headers
        """
        self.content = content
        self.topic = topic
        self.message_id = message_id
        self.timestamp = timestamp
        self.headers = headers or {}

    def get_content_as_dict(self) -> dict[str, Any]:
        """
        Get message content as a dictionary.

        Returns:
            Message content as dictionary
        """
        import json

        if isinstance(self.content, dict):
            return self.content
        if isinstance(self.content, str):
            return json.loads(self.content)
        if isinstance(self.content, bytes):
            return json.loads(self.content.decode("utf-8"))

        def _type_error():
            return TypeError(
                f"Cannot convert content of type {type(self.content)} to dict",
            )

        raise _type_error()

    def __str__(self) -> str:
        """Return string representation of the message."""
        return f"QueueMessage(topic={self.topic}, id={self.message_id})"
