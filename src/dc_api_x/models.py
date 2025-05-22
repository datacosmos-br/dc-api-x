"""
Data models for DCApiX.

This module provides base classes for data models with validation.
"""

from typing import Any, ClassVar, Generic, Optional, TypeVar, Union, Dict, List, Iterator

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class BaseModel(PydanticBaseModel):
    """
    Base model for API data models.

    This class extends Pydantic's BaseModel with API-specific utilities.
    """

    model_config: ClassVar[ConfigDict] = {
        "extra": "ignore",  # Ignore extra fields not defined in model
        "validate_assignment": True,  # Validate values on assignment
        "arbitrary_types_allowed": True,  # Allow custom types
        "populate_by_name": True,  # Allow populating by field name
    }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dict representation of the model
        """
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """
        Convert model to JSON string.

        Args:
            **kwargs: Arguments to pass to model_dump_json

        Returns:
            JSON string representation of the model
        """
        return self.model_dump_json(**kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get attribute by key with fallback to default.

        Args:
            key: Attribute name
            default: Default value if attribute does not exist

        Returns:
            Attribute value or default
        """
        return getattr(self, key, default)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "BaseModel":
        """
        Validate and create a model instance from an object.

        Args:
            obj: Object to validate
            **kwargs: Additional arguments for model validation

        Returns:
            Validated model instance
        """
        return super().model_validate(obj, **kwargs)


class ApiResponse:
    """
    API response data.

    This class encapsulates the response from an API request, including
    status, data, and error information.
    """

    def __init__(
        self,
        *,
        success: bool = True,
        status_code: int = 200,
        data: Any = None,
        error: str | None = None,
        error_code: str | None = None,
        error_details: dict[str, Any] | None = None,
    ):
        """
        Initialize ApiResponse.

        Args:
            success: Whether the request was successful
            status_code: HTTP status code
            data: Response data
            error: Error message (if any)
            error_code: Error code (if any)
            error_details: Additional error details (if any)
        """
        self.success = success
        self.status_code = status_code
        self.data = data
        self.error = error
        self.error_code = error_code
        self.error_details = error_details or {}

    @classmethod
    def success_response(cls, data: Any, status_code: int = 200) -> "ApiResponse":
        """
        Create a successful response.

        Args:
            data: Response data
            status_code: HTTP status code

        Returns:
            ApiResponse: Successful response
        """
        return cls(
            success=True,
            status_code=status_code,
            data=data,
        )

    @classmethod
    def error_response(
        cls,
        error: str,
        status_code: int = 400,
        error_code: str | None = None,
        error_details: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """
        Create an error response.

        Args:
            error: Error message
            status_code: HTTP status code
            error_code: Error code
            error_details: Additional error details

        Returns:
            ApiResponse: Error response
        """
        return cls(
            success=False,
            status_code=status_code,
            error=error,
            error_code=error_code,
            error_details=error_details,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert response to dictionary.

        Returns:
            dict[str, Any]: Response as dictionary
        """
        result = {
            "success": self.success,
            "status_code": self.status_code,
        }

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code
            if self.error_details:
                result["error_details"] = self.error_details

        return result

    def __str__(self) -> str:
        """Return string representation of the response."""
        if self.success:
            return f"ApiResponse(success={self.success}, status_code={self.status_code}, data={self.data})"
        return f"ApiResponse(success={self.success}, status_code={self.status_code}, error={self.error})"

    def __bool__(self) -> bool:
        """Return boolean representation of the response (success status)."""
        return self.success


class GenericResponse(Generic[T]):
    """
    Generic response for any protocol.

    This class can be used to encapsulate responses from any protocol,
    not just HTTP APIs.
    """

    def __init__(
        self,
        *,
        success: bool = True,
        data: Optional[T] = None,
        error: Optional[str] = None,
        error_code: Optional[str] = None,
        error_details: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize GenericResponse.

        Args:
            success: Whether the operation was successful
            data: Response data
            error: Error message (if any)
            error_code: Error code (if any)
            error_details: Additional error details (if any)
            metadata: Additional metadata about the response
        """
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.error_details = error_details or {}
        self.metadata = metadata or {}
        # Initialize methods as instance attributes to avoid mypy errors
        self._success_data: Optional[T] = None
        self._error_message: Optional[str] = None
        self._error_code: Optional[str] = None
        self._error_details: Optional[dict[str, Any]] = None
        self._metadata: Optional[dict[str, Any]] = None

    @classmethod
    def success(
        cls,
        data: T,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "GenericResponse[T]":
        """
        Create a successful response.

        Args:
            data: Response data
            metadata: Additional metadata

        Returns:
            Successful response
        """
        return cls(
            success=True,
            data=data,
            metadata=metadata,
        )

    @classmethod
    def error(
        cls,
        error: str,
        error_code: Optional[str] = None,
        error_details: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "GenericResponse[T]":
        """
        Create an error response.

        Args:
            error: Error message
            error_code: Error code
            error_details: Additional error details
            metadata: Additional metadata

        Returns:
            Error response
        """
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            error_details=error_details,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert response to dictionary.

        Returns:
            Response as dictionary
        """
        result = {
            "success": self.success,
        }

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code
            if self.error_details:
                result["error_details"] = self.error_details

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def __bool__(self) -> bool:
        """Return boolean representation of the response (success status)."""
        return self.success


class DatabaseResult(Generic[T]):
    """
    Result of a database operation.
    """

    def __init__(
        self,
        *,
        success: bool = True,
        rows: Optional[list[T]] = None,
        affected_rows: int = 0,
        error: Optional[str] = None,
        query: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize DatabaseResult.

        Args:
            success: Whether the operation was successful
            rows: Query result rows
            affected_rows: Number of affected rows for write operations
            error: Error message (if any)
            query: Query that was executed
            params: Parameters used in the query
        """
        self.success = success
        self.rows = rows or []
        self.affected_rows = affected_rows
        self.error = error
        self.query = query
        self.params = params

    @property
    def first(self) -> Optional[T]:
        """
        Get the first result row, or None if there are no results.

        Returns:
            First result row or None
        """
        return self.rows[0] if self.rows else None

    def __bool__(self) -> bool:
        """Return boolean representation of the result (success status)."""
        return self.success

    def __len__(self) -> int:
        """Return number of result rows."""
        return len(self.rows)

    def __iter__(self) -> Iterator[T]:
        """Iterate over result rows."""
        return iter(self.rows)


class DirectoryEntry:
    """
    Directory (LDAP) entry.
    """

    def __init__(
        self,
        dn: str,
        attributes: dict[str, list[Union[str, bytes]]],
    ):
        """
        Initialize DirectoryEntry.

        Args:
            dn: Distinguished name
            attributes: Entry attributes
        """
        self.dn = dn
        self.attributes = attributes

    def get_attribute(
        self,
        name: str,
        default: Any = None,
        *,
        as_string: bool = True,
    ) -> Any:
        """
        Get an attribute value.

        Args:
            name: Attribute name
            default: Default value if attribute doesn't exist
            as_string: Whether to convert bytes to strings

        Returns:
            Attribute value or default
        """
        values = self.attributes.get(name, [])
        if not values:
            return default

        value = values[0]
        if as_string and isinstance(value, bytes):
            return value.decode("utf-8")

        return value

    def get_attribute_values(
        self,
        name: str,
        *,
        as_string: bool = True,
    ) -> list[Any]:
        """
        Get all values of an attribute.

        Args:
            name: Attribute name
            as_string: Whether to convert bytes to strings

        Returns:
            List of attribute values
        """
        values = self.attributes.get(name, [])

        if as_string:
            return [
                value.decode("utf-8") if isinstance(value, bytes) else value
                for value in values
            ]

        return values

    def to_dict(self, *, as_string: bool = True) -> dict[str, Any]:
        """
        Convert entry to dictionary.

        Args:
            as_string: Whether to convert bytes to strings

        Returns:
            Entry as dictionary
        """
        result: dict[str, Any] = {"dn": self.dn}

        for key, values in self.attributes.items():
            if as_string:
                result[key] = [
                    value.decode("utf-8") if isinstance(value, bytes) else value
                    for value in values
                ]
            else:
                result[key] = values

        return result


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
        raise TypeError(
            f"Cannot convert content of type {type(self.content)} to dict",
        )

    def __str__(self) -> str:
        """Return string representation of the message."""
        return f"QueueMessage(topic={self.topic}, id={self.message_id})"
