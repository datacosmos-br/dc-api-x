"""
Schema extraction and management for DCApiX.

This module provides classes and functions for extracting and managing API schemas,
including schema extraction, caching, and loading from files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, create_model

import dc_api_x as apix
from dc_api_x.utils.logging import setup_logger

# Set up logger
logger = setup_logger(__name__)


class SchemaDefinition:
    """
    Schema definition for an API entity.

    This class encapsulates a schema definition for an API entity, including
    field definitions, constraints, and metadata.
    """

    def __init__(
        self,
        name: str,
        fields: dict[str, dict[str, Any]],
        description: Optional[str] = None,
        required_fields: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize SchemaDefinition.

        Args:
            name: Entity name
            fields: Field definitions
            description: Schema description (optional)
            required_fields: List of required field names (optional)
        """
        self.name = name
        self.fields = fields
        self.description = description
        self.required_fields = required_fields or []

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> SchemaDefinition:
        """
        Create SchemaDefinition from dictionary.

        Args:
            name: Entity name
            data: Schema definition data

        Returns:
            SchemaDefinition: Schema definition
        """
        fields = {}
        required_fields = []
        description = data.get("description", "")

        # Handle JSON Schema format
        if (
            "properties" in data
            and isinstance(data["properties"], dict[str, Any])
            or "type" in data
            and data["type"] == "object"
            and "properties" in data
        ):
            fields = data["properties"]
            required_fields = data.get("required", [])
        # Handle simple field list format
        elif "fields" in data and isinstance(data["fields"], dict[str, Any]):
            fields = data["fields"]
            required_fields = data.get("required_fields", [])

        cls(
            name=name,
            fields=fields,
            description=description,
            required_fields=required_fields,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert SchemaDefinition to dictionary.

        Returns:
            Dict[str, Any]: Schema definition as dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "fields": self.fields,
            "required_fields": self.required_fields,
        }

    def to_json_schema(self) -> dict[str, Any]:
        """
        Convert SchemaDefinition to JSON Schema format.

        Returns:
            Dict[str, Any]: JSON Schema
        """
        return {
            "type": "object",
            "title": self.name,
            "description": self.description,
            "properties": self.fields,
            "required": self.required_fields,
        }

    def save(self, directory: Union[str, Path]) -> str:
        """
        Save SchemaDefinition to a file.

        Args:
            directory: Directory to save the schema in

        Returns:
            str: Path to the saved schema file
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        file_path = directory / f"{self.name.lower()}.schema.json"
        with file_path.open("w") as f:
            json.dump(self.to_json_schema(), f, indent=2)

        logger.debug("Saved schema to %s", file_path)
        return str(file_path)

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> SchemaDefinition:
        """
        Load SchemaDefinition from a file.

        Args:
            file_path: Path to the schema file

        Returns:
            SchemaDefinition: Schema definition
        """
        file_path = Path(file_path)
        logger.debug("Loading schema from %s", file_path)

        with file_path.open() as f:
            data = json.load(f)

        # Extract entity name from filename
        name = file_path.stem
        if name.endswith(".schema"):
            name = name[:-7]

        # Handle JSON Schema format
        if "properties" in data and isinstance(data["properties"], dict[str, Any]):
            return cls(
                name=data.get("title", name),
                fields=data["properties"],
                description=data.get("description", ""),
                required_fields=data.get("required", []),
            )

        # Handle our custom format
        return cls.from_dict(name, data)


class SchemaExtractor:
    """
    Schema extractor for API entities.

    This class provides methods for extracting schema definitions from an API,
    with support for caching and schema management.
    """

    def __init__(
        self,
        client: apix.ApiClient,
        cache_dir: Optional[Union[str, Path]] = None,
        schema_path: str = "api/schemas",
    ) -> None:
        """
        Initialize SchemaExtractor.

        Args:
            client: API client instance
            cache_dir: Directory for caching schemas (optional)
            schema_path: API endpoint path for schema extraction
        """
        self.client = client
        if self is not None:
            self.cache_dir = Path(cache_dir) if cache_dir else None
        else:
            # Handle None case appropriately
            pass  # TODO: Implement proper None handling
        self.schema_path = schema_path
        self.schemas: dict[str, SchemaDefinition] = {}
        logger.debug("SchemaExtractor initialized with schema_path=%s", schema_path)

    def discover_entities(self) -> list[str]:
        """
        Discover available entity types from the API.

        Returns:
            List[str]: List of entity names
        """
        logger.debug("Discovering entities")
        try:
            # Try standard REST endpoint first
            response = self.client.get("api/entities")

            if response.success and isinstance(response.data, list[Any]):
                logger.debug("Discovered %d entities", len(response.data))
                return response.data

            # Try alternate endpoint if standard fails
            response = self.client.get("metadata/entities")
            if response.success and isinstance(response.data, list[Any]):
                logger.debug("Discovered %d entities from metadata", len(response.data))
                return response.data

            logger.warning("No entities discovered from API")

        except apix.ApiError as e:
            logger.warning("Error discovering entities: %s", str(e))
            return []
        else:
            return []

    def extract_schema(self, entity_name: str) -> Optional[SchemaDefinition]:
        """
        Extract schema for an entity from the API.

        Args:
            entity_name: Name of the entity

        Returns:
            Optional[SchemaDefinition]: Schema definition or None if not found
        """
        # Check cache first
        if entity_name in self.schemas:
            logger.debug("Returning cached schema for %s", entity_name)
            return self.schemas[entity_name]

        # Try to load from cache directory
        if self.cache_dir and self.cache_dir.exists():
            schema_file = self.cache_dir / f"{entity_name.lower()}.schema.json"
            if schema_file.exists():
                try:
                    logger.debug("Loading schema from cache for %s", entity_name)
                    schema = SchemaDefinition.load(schema_file)
                    self.schemas[entity_name] = schema
                    return schema
                except (
                    Exception
                ) as e:  # noqa: BLE001 - Tratamento genérico necessário para qualquer erro de cache
                    logger.warning(
                        "Error loading cached schema for %s: %s",
                        entity_name,
                        str(e),
                    )
                    # Ignore errors when loading from cache

        # Fetch from API
        try:
            logger.debug("Fetching schema from API for %s", entity_name)
            response = self.client.get(f"{self.schema_path}/{entity_name}")
            if not response.success or not isinstance(response.data, dict[str, Any]):
                logger.warning("Failed to fetch schema for %s", entity_name)
                return None

            schema = SchemaDefinition.from_dict(entity_name, response.data)
            self.schemas[entity_name] = schema

            # Save to cache if enabled
            if self.cache_dir:
                logger.debug("Saving schema to cache for %s", entity_name)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                schema.save(self.cache_dir)

            return schema
        except apix.ApiError:
            logger.exception(
                "API error extracting schema for %s",
                entity_name,
            )
            return None

    def extract_schemas(
        self,
        entity_names: list[str],
    ) -> dict[str, Optional[SchemaDefinition]]:
        """
        Extract schemas for multiple entities.

        Args:
            entity_names: List of entity names

        Returns:
            Dict[str, Optional[SchemaDefinition]]: Mapping of entity names to schema definitions
        """
        result = {}
        for entity_name in entity_names:
            result[entity_name] = self.extract_schema(entity_name)
        return result

    def extract_all_schemas(self) -> dict[str, Optional[SchemaDefinition]]:
        """
        Extract schemas for all available entities.

        Returns:
            Dict[str, Optional[SchemaDefinition]]: Mapping of entity names to schema definitions
        """
        entity_names = self.discover_entities()
        logger.info("Extracting schemas for %d entities", len(entity_names))
        return self.extract_schemas(entity_names)


class SchemaManager:
    """
    Schema manager for API client.

    This class provides a high-level interface for schema management and
    dynamic model generation based on schemas.
    """

    def __init__(
        self,
        client: Optional[apix.ApiClient] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        *,  # Make all parameters after this keyword-only
        offline_mode: bool = False,
    ) -> None:
        """
        Initialize SchemaManager.

        Args:
            client: API client instance (optional in offline mode)
            cache_dir: Directory for caching schemas (optional)
            offline_mode: Whether to operate in offline mode (using only cached schemas)
        """
        self.client = client
        if self is not None:
            self.cache_dir = Path(cache_dir) if cache_dir else None
        else:
            # Handle None case appropriately
            pass  # TODO: Implement proper None handling
        self.offline_mode = offline_mode
        self.extractor = (
            None
            if offline_mode or client is None
            else SchemaExtractor(client, cache_dir)
        )
        self.schemas: dict[str, SchemaDefinition] = {}
        self.models: dict[str, type[BaseModel]] = {}

        logger.debug(
            "SchemaManager initialized (offline_mode=%s, cache_dir=%s)",
            offline_mode,
            cache_dir,
        )

        # Load cached schemas in offline mode
        if offline_mode and cache_dir and Path(cache_dir).exists():
            self._load_cached_schemas()

    def _load_cached_schemas(self) -> None:
        """Load all cached schemas from the cache directory."""
        if not self.cache_dir or not self.cache_dir.exists():
            return

        logger.debug("Loading cached schemas from %s", self.cache_dir)
        for file_path in self.cache_dir.glob("*.schema.json"):
            try:
                schema = SchemaDefinition.load(file_path)
                self.schemas[schema.name] = schema
                logger.debug("Loaded schema for %s", schema.name)
            except (
                Exception
            ) as e:  # noqa: BLE001 - Tratamento genérico necessário para qualquer erro de formato
                logger.warning("Error loading schema from %s: %s", file_path, str(e))

        logger.info("Loaded %d schemas from cache", len(self.schemas))

    def get_schema(self, entity_name: str) -> Optional[SchemaDefinition]:
        """
        Get schema for an entity.

        Args:
            entity_name: Name of the entity

        Returns:
            Optional[SchemaDefinition]: Schema definition or None if not found
        """
        # Check if we already have the schema
        if entity_name in self.schemas:
            return self.schemas[entity_name]

        # Extract schema if we have an extractor
        if self.extractor:
            schema = self.extractor.extract_schema(entity_name)
            if schema:
                self.schemas[entity_name] = schema
                return schema

        # Try to load from cache directory
        if self.cache_dir and self.cache_dir.exists():
            schema_file = self.cache_dir / f"{entity_name.lower()}.schema.json"
            if schema_file.exists():
                try:
                    schema = SchemaDefinition.load(schema_file)
                    self.schemas[entity_name] = schema
                except (
                    Exception
                ) as e:  # noqa: BLE001 - Tratamento genérico necessário para qualquer erro de arquivo
                    logger.warning("Error loading schema file: %s", str(e))
                else:
                    return schema

        return None

    def get_model(self, entity_name: str) -> Optional[type[BaseModel]]:
        """
        Get model class for an entity.

        Args:
            entity_name: Name of the entity

        Returns:
            Optional[Type[BaseModel]]: Model class or None if schema not found
        """
        # Check if we already have the model
        if entity_name in self.models:
            return self.models[entity_name]

        # Get schema and create model
        schema = self.get_schema(entity_name)
        if not schema:
            logger.warning("No schema found for %s", entity_name)
            return None

        try:
            model = self.create_model(schema)
            self.models[entity_name] = model
        except Exception:
            logger.exception("Error creating model for %s", entity_name)
            return None
        else:
            return model

    def create_model(self, schema: SchemaDefinition) -> type[BaseModel]:
        """
        Create a model class from a schema definition.

        Args:
            schema: Schema definition

        Returns:
            Type[BaseModel]: Model class
        """
        # Define model fields
        fields = {}
        for field_name, field_schema in schema.fields.items():
            # Extract field type and properties
            field_type = self._get_field_type(field_schema)
            is_required = field_name in schema.required_fields

            # Extract field metadata
            description = field_schema.get("description", "")
            default = field_schema.get("default", ... if is_required else None)

            # Create field with metadata
            fields[field_name] = (
                field_type,
                Field(default=default, description=description),
            )

        # Create model class
        model_name = f"{schema.name.title().replace('_', '')}Model"
        model = create_model(
            model_name,
            __base__=BaseModel,
            **fields,
        )

        # Add metadata to model
        model.__doc__ = schema.description or f"Model for {schema.name}"
        logger.debug("Created model class %s with %d fields", model_name, len(fields))

        return model

    def _get_field_type(self, field_schema: dict[str, Any]) -> Any:
        """
        Get Python type for a field schema.

        Args:
            field_schema: Field schema

        Returns:
            Any: Python type
        """
        import typing

        field_type = field_schema.get("type", "string")
        format_type = field_schema.get("format", "")

        if field_type == "string":
            if format_type == "date-time":
                return typing.Optional[
                    str
                ]  # Use string for now, could use datetime.datetime
            if format_type == "date":
                return typing.Optional[
                    str
                ]  # Use string for now, could use datetime.date
            if format_type in {"email", "uri"}:
                return typing.Optional[str]
            return typing.Optional[str]
        if field_type == "number":
            if format_type == "float":
                return typing.Optional[float]
            return typing.Optional[float]
        if field_type == "integer":
            return typing.Optional[int]
        if field_type == "boolean":
            return typing.Optional[bool]
        if field_type == "array":
            if "items" in field_schema and isinstance(
                field_schema["items"],
                dict[str, Any],
            ):
                item_type = self._get_field_type(field_schema["items"])
                return typing.Optional[list[item_type]]
            return typing.Optional[list[typing.Any]]
        if field_type == "object":
            return typing.Optional[dict[str, typing.Any]]
        return typing.Optional[typing.Any]

    @classmethod
    def load_schema(cls, file_path: Union[str, Path]) -> SchemaDefinition:
        """
        Load a schema definition from a file.

        Args:
            file_path: Path to the schema file

        Returns:
            SchemaDefinition: The loaded schema
        """
        return SchemaDefinition.load(file_path)

    def save_schema(
        self,
        entity_name: str,
        directory: Optional[Union[str, Path]] = None,
    ) -> Optional[str]:
        """
        Save a schema definition to a file.

        Args:
            entity_name: Name of the entity
            directory: Directory to save the schema in (defaults to cache_dir)

        Returns:
            Optional[str]: Path to the saved schema file or None if failed
        """
        schema = self.get_schema(entity_name)
        if not schema:
            logger.warning("No schema found for %s", entity_name)
            return None

        save_dir = directory if directory else self.cache_dir
        if not save_dir:
            logger.warning("No directory specified for saving schema")
            return None

        return schema.save(save_dir)
