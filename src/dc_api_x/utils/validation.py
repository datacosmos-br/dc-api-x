"""
Validation utilities for DCApiX.

This module provides utility functions for validating various data types.
"""

import datetime
import re
import uuid
from collections.abc import Callable
from typing import Any, TypeVar, Union

# Type variable for generic type validation
T = TypeVar("T")
R = TypeVar("R")


def validate_url(url: str) -> tuple[bool, str | None]:
    """
    Validate a URL for basic URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Basic URL regex pattern (simplified)
    pattern = r"^(http|https)://([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+|localhost)(:\d+)?(/[-a-zA-Z0-9%_.~#+]*)*(\?[-a-zA-Z0-9%_.~+=&;]+)?(#[-a-zA-Z0-9]*)?$"

    if not re.match(pattern, url):
        return False, "Invalid URL format"

    return True, None


def validate_email(email: str) -> tuple[bool, str | None]:
    """
    Validate an email address for basic email format.

    Args:
        email: Email to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_uuid(uuid_str: str) -> tuple[bool, str | None]:
    """
    Validate a UUID string.

    Args:
        uuid_str: UUID string to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Attempt to parse the UUID string
        uuid.UUID(uuid_str)
    except ValueError:
        return False, "Invalid UUID format"
    else:
        return True, None


def validate_date(
    date_str: str,
    format_str: str = "%Y-%m-%d",
) -> tuple[bool, str | None]:
    """
    Validate a date string against a specified format.

    Args:
        date_str: Date string to validate
        format_str: Expected date format (default: %Y-%m-%d)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Try to parse date
    try:
        # Parse the date string to validate format
        # Use _ to ignore the result since we don't need it
        _ = datetime.datetime.strptime(date_str, format_str)  # noqa: DTZ007
    except ValueError:
        return False, f"Invalid date format, expected {format_str}"
    else:
        return True, None


def validate_required_fields(
    data: dict[str, Any],
    required_fields: list[str],
) -> tuple[bool, str | None]:
    """
    Validate that all required fields are present in data.

    Args:
        data: Data to validate
        required_fields: list of required field names

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check each required field
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    # Return result
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None


def validate_enum_field(value: Any, valid_values: list[T]) -> tuple[bool, str | None]:
    """
    Validate that a value is in a list of valid values.

    Args:
        value: Value to validate
        valid_values: list of valid values

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if value is in valid values
    if value not in valid_values:
        return (
            False,
            f"Invalid value: {value}, expected one of: {', '.join(str(v) for v in valid_values)}",
        )

    return True, None


def validate_min_max(
    value: Union[int, float],
    min_value: Union[int, float, None] = None,
    max_value: Union[int, float, None] = None,
) -> tuple[bool, str | None]:
    """
    Validate that a numeric value is within a range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check minimum value
    if min_value is not None and value < min_value:
        return False, f"Value {value} is less than the minimum {min_value}"

    # Check maximum value
    if max_value is not None and value > max_value:
        return False, f"Value {value} is greater than the maximum {max_value}"

    return True, None


def validate_not_empty(value: str, field_name: str) -> None:
    """Validate that a string is not empty.

    Args:
        value: String value to validate
        field_name: Name of the field being validated

    Raises:
        ValueError: If the value is empty
    """
    if not value:

        def _empty_field_error() -> None:
            return ValueError(f"{field_name} cannot be empty")

        raise _empty_field_error()


def validate_type(value: Any, expected_type: type[T], field_name: str) -> T:
    """Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Name of the field being validated

    Returns:
        The validated value

    Raises:
        TypeError: If the value is not of the expected type
    """
    if not isinstance(value, expected_type):

        def _type_error() -> None:
            return TypeError(
                f"{field_name} must be of type {expected_type.__name__}, "
                f"got {type(value).__name__}",
            )

        raise _type_error()
    return value


def validate_dict(
    value: dict[str, Any],
    required_keys: list[str],
    field_name: str,
) -> dict[str, Any]:
    """Validate that a dictionary contains required keys.

    Args:
        value: Dictionary to validate
        required_keys: List of required keys
        field_name: Name of the field being validated

    Returns:
        The validated dictionary

    Raises:
        ValueError: If the dictionary is missing required keys
    """
    missing_keys = [key for key in required_keys if key not in value]
    if missing_keys:

        def _missing_keys_error() -> None:
            return ValueError(
                f"{field_name} is missing required keys: {', '.join(missing_keys)}",
            )

        raise _missing_keys_error()
    return value


def validate_list(value: list[Any], min_length: int, field_name: str) -> list[Any]:
    """Validate that a list has at least a minimum length.

    Args:
        value: List to validate
        min_length: Minimum length
        field_name: Name of the field being validated

    Returns:
        The validated list

    Raises:
        ValueError: If the list is shorter than the minimum length
    """
    if len(value) < min_length:

        def _list_length_error() -> None:
            return ValueError(
                f"{field_name} must have at least {min_length} items, got {len(value)}",
            )

        raise _list_length_error()
    return value


def validate_one_of(value: Any, valid_values: list[Any], field_name: str) -> Any:
    """Validate that a value is one of a set of valid values.

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of the field being validated

    Returns:
        The validated value

    Raises:
        ValueError: If the value is not one of the valid values
    """
    if value not in valid_values:

        def _invalid_value_error() -> None:
            return ValueError(
                f"{field_name} must be one of {valid_values}, got {value}",
            )

        raise _invalid_value_error()
    return value


def validate_callable(value: Callable[..., R], field_name: str) -> Callable[..., R]:
    """Validate that a value is callable.

    Args:
        value: Value to validate
        field_name: Name of the field being validated

    Returns:
        The validated callable

    Raises:
        TypeError: If the value is not callable
    """
    if not callable(value):

        def _not_callable_error() -> None:
            return TypeError(
                f"{field_name} must be callable, got {type(value).__name__}",
            )

        raise _not_callable_error()
    return value
