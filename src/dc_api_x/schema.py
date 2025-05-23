"""
Schema management for DCApiX.

This module provides classes for working with API schemas.
"""

import json
from pathlib import Path
from typing import Any, TypeVar, cast

from pydantic import BaseModel, create_model

from dc_api_x.client import ApiClient

# Define a generic type for models
ModelT = TypeVar("ModelT", bound=BaseModel)


class SchemaDefinition:
    """
    Schema definition for an API entity.

    This class represents a schema for an API entity, including field definitions,
    required fields, and other metadata.
    """

    def __init__(
        self,
        name: str,
        description: str,
        fields: dict[str, dict[str, Any]],
        required_fields: list[str] | None = None,
    ):
        """
        Initialize schema definition.

        Args:
            name: Schema name
            description: Schema description
            fields: Field definitions
            required_fields: Required fields
        """
        self.name = name
        self.description = description
        self.fields = fields
        self.required_fields = required_fields or []

    def to_json_schema(self) -> dict[str, Any]:
        """
        Convert to JSON Schema format.

        Returns:
            JSON Schema representation
        """
        schema = {
            "type": "object",
            "title": self.name,
            "description": self.description,
            "properties": self.fields,
        }

        if self.required_fields:
            schema["required"] = self.required_fields

        return schema

    def save(self, directory: Path) -> Path:
        """
        Save schema to file.

        Args:
            directory: Directory to save to

        Returns:
            Path to saved schema file
        """
        # Create directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = f"{self.name.lower()}.schema.json"
        file_path = directory / filename

        # Write schema to file
        with Path(file_path).open("w") as f:
            json.dump(self.to_json_schema(), f, indent=2)

        return file_path

    @classmethod
    def load(cls, file_path: Path) -> "SchemaDefinition":
        """
        Load schema from file.

        Args:
            file_path: Path to schema file

        Returns:
            Schema definition
        """
        try:
            with Path(file_path).open() as f:
                schema = json.load(f)

            return cls(
                name=schema.get("title", Path(file_path).name.split(".")[0]),
                description=schema.get("description", ""),
                fields=schema.get("properties", {}),
                required_fields=schema.get("required", []),
            )
        except FileNotFoundError as err:

            def _schema_file_not_found_error():
                return FileNotFoundError(f"Schema file not found: {file_path}")

            raise _schema_file_not_found_error() from err
        except json.JSONDecodeError as err:

            def _invalid_schema_error(err):
                return ValueError(f"Invalid schema format: {err}")

            raise _invalid_schema_error(err) from err


class SchemaManager:
    """
    Manager for API schemas.

    This class manages API schemas and generates models from them.
    """

    def __init__(
        self,
        client: ApiClient | None = None,
        cache_dir: Path | None = None,
        *,
        offline_mode: bool = False,
    ):
        """
        Initialize schema manager.

        Args:
            client: API client
            cache_dir: Directory for schema caching
            offline_mode: Whether to operate in offline mode
        """
        self.client = client
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./schemas")
        self.offline_mode = offline_mode
        self.schemas: dict[str, SchemaDefinition] = {}

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cached schemas
        self._load_cached_schemas()

    def _load_cached_schemas(self) -> None:
        """Load cached schemas from the cache directory."""
        if not self.cache_dir.exists():
            return

        for file_path in self.cache_dir.glob("*.schema.json"):
            try:
                schema_name = file_path.stem
                if schema_name.endswith(".schema"):
                    schema_name = schema_name[:-7]

                schema = SchemaDefinition.load(file_path)
                self.schemas[schema_name] = schema
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as err:
                print(f"Error loading schema {file_path}: {err}")

    def get_schema(self, name: str) -> SchemaDefinition | None:
        """
        Get schema by name.

        Args:
            name: Schema name

        Returns:
            Schema definition or None if not found
        """
        # Check if schema is already loaded
        if name in self.schemas:
            return self.schemas[name]

        # Try to load from cache
        schema_path = self.cache_dir / f"{name.lower()}.schema.json"
        if schema_path.exists():
            schema = SchemaDefinition.load(schema_path)
            self.schemas[name] = schema
            return schema

        # Try to fetch from API if not in offline mode
        if not self.offline_mode and self.client:
            # This would be implemented to fetch from the API
            pass

        return None

    def _python_type_from_json_type(
        self,
        json_type: str,
    ) -> type[Any]:  # type: ignore[return]
        """
        Get Python type from JSON Schema type.

        Args:
            json_type: JSON Schema type

        Returns:
            Python type
        """
        # Define a map of JSON types to Python types
        type_mapping: dict[str, type[Any]] = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        # Get the type from mapping or use Any for unknown types
        if json_type in type_mapping:
            return type_mapping[json_type]
        return Any  # type: ignore[return-value]

    def get_model(self, schema_name: str) -> type[BaseModel] | None:
        """
        Get model class for schema.

        Args:
            schema_name: Schema name

        Returns:
            Model class or None if schema not found
        """
        schema = self.get_schema(schema_name)
        if not schema:
            return None

        # Define field types and defaults
        field_definitions: dict[str, tuple[type, Any]] = {}

        for field_name, field_def in schema.fields.items():
            json_type = field_def.get("type", "string")
            field_type = self._python_type_from_json_type(json_type)

            # Set required fields without default values
            if field_name in schema.required_fields:
                field_definitions[field_name] = (field_type, ...)
            else:
                # Set optional fields with None as default
                # Create the proper type annotation for Optional fields
                field_definitions[field_name] = (field_type, None)

        # Create model dynamically using keyword arguments
        try:
            # Create the model with the field definitions
            model = create_model(  # type: ignore[call-overload]
                schema_name,
                __base__=BaseModel,
                **field_definitions,
            )

            # Add docstring
            if model.__doc__ is None:
                model.__doc__ = ""
            model.__doc__ += f"\n{schema.description}"

            return cast(type[BaseModel], model)
        except (TypeError, ValueError, AttributeError) as err:
            print(f"Error creating model for schema {schema_name}: {err}")
            return None
