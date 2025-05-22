"""
Validation utilities for the API client.

This module provides functions for validating data, including URLs, emails,
UUIDs, and dates.
"""

import re
import uuid
from datetime import datetime
from typing import Any, List, Dict, TypeVar, cast, Union

T = TypeVar('T')


def validate_url(url: str) -> tuple[bool, str | None]:
    """
    Validate a URL.

    Args:
        url: URL to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if URL is empty
    if not url:
        return False, "URL cannot be empty"

    # Simple URL regex pattern
    url_pattern = r"^(http|https)://[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:[0-9]{1,5})?(/.*)?$"

    # Check URL format
    if not re.match(url_pattern, url):
        return False, "URL must start with http:// or https:// and have a valid domain"

    return True, None


def validate_email(email: str) -> tuple[bool, str | None]:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if email is empty
    if not email:
        return False, "Email cannot be empty"

    # Email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Check email format
    if not re.match(email_pattern, email):
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
    # Check if UUID is empty
    if not uuid_str:
        return False, "UUID cannot be empty"

    # Try to parse UUID
    try:
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
    Validate a date string.

    Args:
        date_str: Date string to validate
        format_str: Date format string (default: "%Y-%m-%d")

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if date is empty
    if not date_str:
        return False, "Date cannot be empty"

    # Try to parse date
    try:
        datetime.strptime(date_str, format_str)
    except ValueError:
        return False, f"Invalid date format, expected {format_str}"
    else:
        return True, None


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str],
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


def validate_enum_field(value: Any, valid_values: List[T]) -> tuple[bool, str | None]:
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
