"""
Schema provider interface for DCApiX.

This module defines the SchemaProvider abstract class for
schema definition and validation.
"""

import abc
from typing import Any

from .protocol import Provider


class SchemaProvider(Provider):
    """
    Base interface for schema providers.

    Schema providers supply schema information for data structures
    and can validate data against those schemas.
    """

    @abc.abstractmethod
    def get_schema(self, name: str) -> dict[str, Any]:
        """
        Get a schema by name.

        Args:
            name: Schema name

        Returns:
            Schema definition
        """

    @abc.abstractmethod
    def list_schemas(self) -> list[str]:
        """
        List available schemas.

        Returns:
            List of schema names
        """

    @abc.abstractmethod
    def validate(self, name: str, data: Any) -> list[str]:
        """
        Validate data against a schema.

        Args:
            name: Schema name
            data: Data to validate

        Returns:
            List of validation errors (empty if valid)
        """

    def register_schema(self, name: str, schema: dict[str, Any]) -> None:
        """
        Register a new schema.

        Args:
            name: Schema name
            schema: Schema definition
        """
        raise NotImplementedError("Schema registration not supported by this provider")
