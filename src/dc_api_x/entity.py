"""
Entity operations and management for DCApiX.

This module provides a high-level interface for working with API entities,
including dynamic entity discovery and interaction through the EntityManager.
"""

from __future__ import annotations

from typing import Any, Optional, TypeVar

import dc_api_x as apix
from dc_api_x.exceptions import EntityError, ValidationError
from dc_api_x.utils.logging import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Error message constants
ENTITY_CREATE_ERROR_MSG = "Failed to create entity instance: %s"
UNSUPPORTED_HTTP_METHOD_MSG = "Unsupported HTTP method: %s"
ACTION_EXECUTION_ERROR_MSG = "Failed to execute '%s' on %s: %s"

# Type variable for entity types
T = TypeVar("T", bound=apix.BaseModel)


class EntityManager:
    """
    Manager for working with multiple entity types.

    This class provides a high-level interface for discovering and working
    with different entity types in the API through BaseEntity implementations.
    """

    def __init__(self, client: apix.ApiClient):
        """
        Initialize EntityManager.

        Args:
            client: API client instance
        """
        self.client = client
        self.entities: dict[str, apix.BaseEntity[Any]] = {}  # Cache of entity instances
        logger.debug("EntityManager initialized")

    def get_entity(
        self,
        entity_name: str,
        entity_class: Optional[type[apix.BaseEntity[Any]]] = None,
        model_class: Optional[type[apix.BaseModel]] = None,
        base_path: str = "",
    ) -> apix.BaseEntity[Any]:
        """
        Get an Entity instance for the specified entity type.

        Args:
            entity_name: Name of the entity in the API
            entity_class: Optional entity class to use (defaults to BaseEntity)
            model_class: Optional model class for data validation and conversion
            base_path: Optional base path for API endpoints

        Returns:
            BaseEntity: Entity instance

        Raises:
            ValidationError: If entity configuration is invalid
        """
        # Use cached instance if available (and model_class matches)
        cache_key = f"{entity_name}:{base_path}"
        if cache_key in self.entities:
            entity = self.entities[cache_key]
            if (model_class is None or entity.model_class == model_class) and (
                entity_class is None or isinstance(entity, entity_class)
            ):
                return entity

        # Use the provided entity class or default to BaseEntity
        entity_class_to_use = entity_class or apix.BaseEntity[Any]

        # Create a new entity instance
        try:
            # Create a dynamic subclass with the entity configuration
            if model_class:
                # Define a subclass with the model class set
                entity_model_class = (
                    model_class  # Create a local variable to avoid name confusion
                )

                # Use type() to create a dynamic class
                dynamic_entity = type(
                    f"Dynamic{entity_name.capitalize()}Entity",
                    (entity_class_to_use,),
                    {
                        "model_class": entity_model_class,
                        "resource_name": entity_name,
                    },
                )
                entity = dynamic_entity(self.client, base_path)
            else:
                # Create instance with just the resource name set
                entity = entity_class_to_use(self.client, base_path)
                # Use setattr to set class variable
                entity.__class__.resource_name = entity_name
        except (TypeError, ValueError, AttributeError) as e:
            logger.exception(
                "Error creating entity instance for %s",
                entity_name,
            )
            raise ValidationError(ENTITY_CREATE_ERROR_MSG % str(e)) from e
        else:
            # Cache the entity instance
            self.entities[cache_key] = entity
            logger.debug("Created entity instance for %s", entity_name)
            return entity

    def discover_entities(self) -> list[str]:
        """
        Discover available entity types from the API.

        Returns:
            List[str]: List of entity names
        """
        try:
            logger.debug("Discovering entities")
            # Try standard REST endpoint first
            response = self.client.get("api/entities")

            if response.success and isinstance(response.data, list):
                logger.debug("Discovered %d entities", len(response.data))
                return response.data

            # Try alternate endpoint if standard fails
            response = self.client.get("metadata/entities")
            if response.success and isinstance(response.data, list):
                logger.debug("Discovered %d entities from metadata", len(response.data))
                return response.data
        except apix.ApiError as e:
            logger.warning("Error discovering entities: %s", str(e))
            return []
        else:
            logger.warning("No entities discovered from API")
            return []

    def execute_entity_action(  # noqa: PLR0913, PLR0911
        self,
        entity_name: str,
        action: str,
        resource_id: Optional[str] = None,
        method: str = "POST",
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> apix.ApiResponse:
        """
        Execute a custom action on an entity.

        Args:
            entity_name: Name of the entity
            action: Action name
            resource_id: Optional resource ID
            method: HTTP method (default: POST)
            data: Optional request data
            params: Optional query parameters

        Returns:
            Response data from the API
        """
        entity = self.get_entity(entity_name)

        def _handle_unsupported_method(method_name: str) -> None:
            """Inner function to raise method error"""
            raise ValueError(UNSUPPORTED_HTTP_METHOD_MSG % method_name)

        try:
            if hasattr(entity, "custom_action"):
                # Use standard arguments for custom_action
                return entity.custom_action(
                    action=action,
                    entity_id=resource_id,  # Use entity_id instead of id
                    method=method,
                    data=data,
                    params=params,
                )
            # Fallback implementation
            if resource_id:
                url = f"{entity.resource_path}/{resource_id}/{action}"
            else:
                url = f"{entity.resource_path}/{action}"

            method = method.upper()
            if method == "GET":
                return self.client.get(url, params=params)
            if method == "POST":
                return self.client.post(url, json_data=data, params=params)
            if method == "PUT":
                return self.client.put(url, json_data=data, params=params)
            if method == "PATCH":
                return self.client.patch(url, json_data=data, params=params)
            if method == "DELETE":
                return self.client.delete(url, params=params)

            _handle_unsupported_method(method)
            # This line is needed to satisfy mypy's flow analysis
            # It will never be reached due to the exception raised by _handle_unsupported_method
            return self.client.get("", params={})

        except (apix.ApiError, ValueError) as e:
            logger.exception(
                "Error executing action %s on %s",
                action,
                entity_name,
            )
            raise EntityError(
                ACTION_EXECUTION_ERROR_MSG % (action, entity_name, str(e)),
            ) from e
