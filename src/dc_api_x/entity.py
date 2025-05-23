"""
Entity management for DCApiX.

This module provides entity classes for managing API resources.
"""

from typing import Any, Type

from dc_api_x.client import ApiClient
from dc_api_x.models import ApiResponse
from pydantic import BaseModel


class Entity:
    """
    Base class for API entity operations.

    An entity represents a resource in the API, such as a User or Product,
    and provides methods for CRUD operations.
    """

    def __init__(
        self,
        client: ApiClient,
        resource_path: str,
        model_class: Type[BaseModel] | None = None,
    ):
        """
        Initialize entity.

        Args:
            client: API client
            resource_path: Resource path
            model_class: Model class for entity data
        """
        self.client = client
        self.resource_path = resource_path.rstrip("/")
        self.model_class = model_class

    def get(
        self,
        entity_id: str | int,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID
            params: Query parameters

        Returns:
            ApiResponse with entity data
        """
        endpoint = f"{self.resource_path}/{entity_id}"
        return self.client.get(endpoint, params=params)

    def list(
        self,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        List entities.

        Args:
            params: Query parameters

        Returns:
            ApiResponse with entity list
        """
        return self.client.get(self.resource_path, params=params)

    def create(
        self,
        data: dict[str, Any],
    ) -> ApiResponse:
        """
        Create entity.

        Args:
            data: Entity data

        Returns:
            ApiResponse with created entity
        """
        return self.client.post(self.resource_path, json_data=data)

    def update(
        self,
        entity_id: str | int,
        data: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        Update entity.

        Args:
            entity_id: Entity ID
            data: Entity data
            params: Query parameters

        Returns:
            ApiResponse with updated entity
        """
        endpoint = f"{self.resource_path}/{entity_id}"
        return self.client.put(endpoint, json_data=data, params=params)

    def delete(
        self,
        entity_id: str | int,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        """
        Delete entity.

        Args:
            entity_id: Entity ID
            params: Query parameters

        Returns:
            ApiResponse with deletion result
        """
        endpoint = f"{self.resource_path}/{entity_id}"
        return self.client.delete(endpoint, params=params)


class EntityManager:
    """
    Manager for API entities.

    This class manages entity instances and provides access to them.
    """

    def __init__(self, client: ApiClient):
        """
        Initialize entity manager.

        Args:
            client: API client
        """
        self.client = client
        self.entities: dict[str, Entity] = {}

    def get_entity(
        self,
        resource_path: str,
        model_class: Type[BaseModel] | None = None,
    ) -> Entity:
        """
        Get entity for resource path.

        Args:
            resource_path: Resource path
            model_class: Model class for entity data

        Returns:
            Entity instance
        """
        return Entity(self.client, resource_path, model_class)

    def register_entity(
        self,
        name: str,
        entity: Entity,
    ) -> None:
        """
        Register entity.

        Args:
            name: Entity name
            entity: Entity instance
        """
        self.entities[name] = entity
