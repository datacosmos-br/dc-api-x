"""
Validation utilities for DCApiX.

This module provides utility functions for validating various data types.
"""

import datetime
import re
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

# Type variable for generic type validation
T = TypeVar("T")
R = TypeVar("R")

# Import logging for validation errors
from dc_api_x.utils import logging

# We no longer need to check if logfire is available since
# our logging module handles that transparently


def log_validation_error(
    field_name: str,
    error_message: str,
    value: Any = None,
) -> None:
    """
    Log a validation error with the logging module.

    Args:
        field_name: Name of the field that failed validation
        error_message: Error message
        value: Optional value that failed validation
    """
    # Don't log actual values for potentially sensitive fields
    sensitive_fields = ["password", "token", "key", "secret", "credential", "auth"]
    should_log_value = not any(
        sensitive in field_name.lower() for sensitive in sensitive_fields
    )

    # Log with logging module
    logging.warning(
        "Validation error",
        field=field_name,
        error=error_message,
        **({"value": value} if should_log_value and value is not None else {}),
    )


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
        error_msg = "Invalid URL format"
        log_validation_error("url", error_msg, url)
        return False, error_msg

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
        error_msg = "Invalid email format"
        log_validation_error("email", error_msg, email)
        return False, error_msg

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
        error_msg = "Invalid UUID format"
        log_validation_error("uuid", error_msg, uuid_str)
        return False, error_msg
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
        error_msg = f"Invalid date format, expected {format_str}"
        log_validation_error("date", error_msg, date_str)
        return False, error_msg
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
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        logging.warning(
            "Required fields missing",
            missing_fields=missing_fields,
            required_fields=required_fields,
        )
        return False, error_msg

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
        error_msg = f"Invalid value: {value}, expected one of: {', '.join(str(v) for v in valid_values)}"
        log_validation_error("enum_field", error_msg, value)
        return False, error_msg

    return True, None


def validate_min_max(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
) -> tuple[bool, str | None]:
    """
    Validate that a numeric value is within a specified range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check min value
    if min_value is not None and value < min_value:
        error_msg = f"Value {value} is less than minimum allowed value {min_value}"
        log_validation_error("min_value", error_msg, value)
        return False, error_msg

    # Check max value
    if max_value is not None and value > max_value:
        error_msg = f"Value {value} is greater than maximum allowed value {max_value}"
        log_validation_error("max_value", error_msg, value)
        return False, error_msg

    # Value is within range
    return True, None


def validate_not_empty(value: str, field_name: str) -> None:
    """
    Validate that a string value is not empty.

    Args:
        value: String to validate
        field_name: Name of the field for error messages

    Raises:
        ValueError: If the value is empty
    """
    if not value:
        error_msg = f"{field_name} cannot be empty"
        log_validation_error(field_name, error_msg, value)

        def _empty_field_error() -> None:
            return ValueError(error_msg)

        raise _empty_field_error()


def validate_type(value: Any, expected_type: type[T], field_name: str) -> T:
    """
    Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        TypeError: If the value is not of the expected type
    """
    # Special case for None when type is optional
    if value is None:
        return value

    # Check type
    if not isinstance(value, expected_type):
        actual_type = type(value).__name__
        expected_name = expected_type.__name__
        error_msg = f"{field_name} must be of type {expected_name}, got {actual_type}"
        log_validation_error(field_name, error_msg, value)

        def _type_error() -> None:
            return TypeError(error_msg)

        raise _type_error()

    return value


def validate_dict(
    value: dict[str, Any],
    required_keys: list[str],
    field_name: str,
) -> dict[str, Any]:
    """
    Validate that a dictionary contains required keys.

    Args:
        value: Dictionary to validate
        required_keys: List of required keys
        field_name: Name of the field for error messages

    Returns:
        The validated dictionary

    Raises:
        ValueError: If the dictionary is missing required keys
    """
    # Validate type
    validate_type(value, dict, field_name)

    # Check required keys
    missing_keys = [key for key in required_keys if key not in value]
    if missing_keys:
        error_msg = f"{field_name} is missing required keys: {', '.join(missing_keys)}"
        log_validation_error(field_name, error_msg, value)

        def _missing_keys_error() -> None:
            return ValueError(error_msg)

        raise _missing_keys_error()

    return value


def validate_list(value: list[Any], min_length: int, field_name: str) -> list[Any]:
    """
    Validate that a list has at least the specified minimum length.

    Args:
        value: List to validate
        min_length: Minimum required length
        field_name: Name of the field for error messages

    Returns:
        The validated list

    Raises:
        ValueError: If the list is shorter than the minimum length
    """
    # Validate type
    validate_type(value, list, field_name)

    # Check minimum length
    if len(value) < min_length:
        error_msg = (
            f"{field_name} must contain at least {min_length} items, got {len(value)}"
        )
        log_validation_error(field_name, error_msg, value)

        def _list_length_error() -> None:
            return ValueError(error_msg)

        raise _list_length_error()

    return value


def validate_one_of(value: Any, valid_values: list[Any], field_name: str) -> Any:
    """
    Validate that a value is one of the specified valid values.

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValueError: If the value is not in the list of valid values
    """
    # Check if value is in valid values
    if value not in valid_values:
        error_msg = f"{field_name} must be one of {valid_values}, got {value}"
        log_validation_error(field_name, error_msg, value)

        def _invalid_value_error() -> None:
            return ValueError(error_msg)

        raise _invalid_value_error()

    return value


def validate_callable(value: Callable[..., R], field_name: str) -> Callable[..., R]:
    """
    Validate that a value is callable.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated callable

    Raises:
        TypeError: If the value is not callable
    """
    # Check if value is callable
    if not callable(value):
        actual_type = type(value).__name__
        error_msg = f"{field_name} must be callable, got {actual_type}"
        log_validation_error(field_name, error_msg, value)

        def _not_callable_error() -> None:
            return TypeError(error_msg)

        raise _not_callable_error()

    return value


def validate_dir_path(path: str | Path) -> Path:
    """
    Validate that a path is a directory that exists.

    Args:
        path: Path to validate

    Returns:
        Path: Validated Path object

    Raises:
        DirectoryNotFoundError: If the directory does not exist
        FilePathNotDirectoryError: If the path is not a directory
    """
    from dc_api_x.utils.exceptions import (
        DirectoryNotFoundError,
        FilePathNotDirectoryError,
    )

    path_obj = Path(path)

    if not path_obj.exists():
        raise DirectoryNotFoundError(f"Directory not found: {path}")

    if not path_obj.is_dir():
        raise FilePathNotDirectoryError(f"Path is not a directory: {path}")

    return path_obj
