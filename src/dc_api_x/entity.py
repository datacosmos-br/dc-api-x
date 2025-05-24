"""
Entity operations and management for DCApiX.

This module provides a high-level interface for working with API entities,
including dynamic entity discovery and interaction through the EntityManager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import dc_api_x as apix
from dc_api_x.models import ApiResponse
from dc_api_x.utils.constants import (
    ACTION_EXECUTION_ERROR_MSG,
    ENTITY_CREATE_ERROR_MSG,
    UNSUPPORTED_HTTP_METHOD_MSG,
)
from dc_api_x.utils.definitions import EntityId
from dc_api_x.utils.exceptions import EntityError, ValidationError
from dc_api_x.utils.logging import setup_logger

if TYPE_CHECKING:
    from dc_api_x.client import ApiClient
    from dc_api_x.entity.base import BaseEntity
    from dc_api_x.models import BaseModel

# Set up logger
logger = setup_logger(__name__)


class EntityManager:
    """
    Manager for working with multiple entity types.

    This class provides a high-level interface for discovering and working
    with different entity types in the API through BaseEntity implementations.
    """

    def __init__(self, client: ApiClient) -> None:
        """
        Initialize EntityManager.

        Args:
            client: API client instance
        """
        self.client = client
        self.entities: dict[str, BaseEntity[Any]] = {}  # Cache of entity instances
        logger.debug("EntityManager initialized")

    def get_entity(
        self,
        entity_name: str,
        entity_class: type[BaseEntity[Any]] | None = None,
        model_class: type[BaseModel] | None = None,
        base_path: str = "",
    ) -> BaseEntity[Any]:
        """
        Get an Entity instance for the specified entity type.

        Args:
            entity_name: Name of the entity in the API
            entity_class: Optional entity class to use (defaults to BaseEntity[BaseModel])
            model_class: Optional model class for data validation and conversion
            base_path: Optional base path for API endpoints

        Returns:
            Entity instance configured for the specified entity type

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
            List of entity names discovered from the API
        """
        try:
            logger.debug("Discovering entities")
            # Try standard REST endpoint first
            response = self.client.get("api/entities")

            if response.success and isinstance(response.data, list):
                entity_list = cast(list[str], response.data)
                logger.debug("Discovered %d entities", len(entity_list))
                return entity_list

            # Try alternate endpoint if standard fails
            response = self.client.get("metadata/entities")
            if response.success and isinstance(response.data, list):
                entity_list = cast(list[str], response.data)
                logger.debug("Discovered %d entities from metadata", len(entity_list))
                return entity_list

            logger.warning("No entities discovered from API")
        except apix.ApiError as e:
            logger.warning("Error discovering entities: %s", str(e))
            return []
        else:
            return []

    def execute_entity_action(  # noqa: PLR0913, PLR0911
        self,
        entity_name: str,
        action: str,
        resource_id: EntityId | None = None,
        method: str = "POST",
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        Execute a custom action on an entity.

        Args:
            entity_name: Name of the entity
            action: Action name
            resource_id: Optional resource ID for the entity
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            data: Optional request payload data
            params: Optional query parameters

        Returns:
            API response from the action execution

        Raises:
            EntityError: If the action execution fails
        """
        entity = self.get_entity(entity_name)

        def _handle_unsupported_method(method_name: str) -> None:
            """Raise an error for an unsupported HTTP method."""
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
