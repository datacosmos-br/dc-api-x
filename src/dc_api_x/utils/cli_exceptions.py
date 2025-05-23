"""
CLI-specific exception classes.

This module defines exceptions that are specific to CLI operations.
"""

from dc_api_x import (
    INVALID_JSON_IN_ERROR,
    SCHEMA_ENTITY_NOT_SPECIFIED_ERROR,
    SCHEMA_EXTRACTION_FAILED_ERROR,
    CLIError,
    ValidationError,
)


class SchemaEntityNotSpecifiedError(CLIError):
    """Raised when an entity name is required but not provided."""

    def __init__(self):
        super().__init__(SCHEMA_ENTITY_NOT_SPECIFIED_ERROR)


class SchemaExtractionFailedError(CLIError):
    """Raised when schema extraction fails for an entity."""

    def __init__(self, entity: str):
        super().__init__(SCHEMA_EXTRACTION_FAILED_ERROR.format(entity))


class JsonValidationError(ValidationError):
    """Raised when JSON validation fails."""

    DATA_FILE = "data file"
    DATA_STRING = "data string"

    def __init__(self, source: str, error: Exception):
        super().__init__(INVALID_JSON_IN_ERROR.format(source, error))
