"""
DCApiX Utilities Module.

This module provides common utility functions and helpers for the DCApiX package.
"""

from .cli import (
    create_client_from_env,
    parse_json_data,
    resolve_config_file,
)
from .exceptions import (
    JsonValidationError,
    SchemaEntityNotSpecifiedError,
    SchemaExtractionFailedError,
)
from .formatting import (
    format_csv,
    format_datetime,
    format_json,
    format_response_data,
    format_table,
    format_text,
    format_value,
    normalize_key,
)
from .logging import create_cli_logger, get_logger, setup_logger
from .validation import (
    validate_callable,
    validate_date,
    validate_dict,
    validate_email,
    validate_enum_field,
    validate_list,
    validate_min_max,
    validate_not_empty,
    validate_one_of,
    validate_required_fields,
    validate_type,
    validate_url,
    validate_uuid,
)

__all__ = [
    # Modules
    "exceptions",
    "formatting",
    "logfire",
    "logging",
    "validation",
]

"""Utility modules for DCApiX."""
