"""
Entity module for DCApiX.

This module provides base classes for entity operations with support for
CRUD operations, pagination, filtering, and sorting.
"""

from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from dc_api_x.entity.base import BaseEntity
from dc_api_x.entity.filters import EntityFilter, FilterExpression
from dc_api_x.entity.sorters import EntitySorter, SortDirection

T = TypeVar("T", bound=BaseModel)

__all__ = [
    "BaseEntity",
    "EntityFilter",
    "FilterExpression",
    "EntitySorter",
    "SortDirection",
    "EntityManager",
]

# Error message constants
ENTITY_NAME_REQUIRED = "Entity name is required"
ENTITY_NOT_REGISTERED = "Entity '{name}' not registered"


class EntityManager:
    """
    Manager class for registering and retrieving entity classes.

    This class maintains a registry of entity classes and provides
    methods to create and retrieve entity instances.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialize the entity manager.

        Args:
            client: API client to use for entity operations
        """
        self.client = client
        self._entities: dict[str, type[BaseEntity]] = {}

    def register(
        self,
        entity_class: type[BaseEntity],
        name: Optional[str] = None,
    ) -> None:
        """
        Register an entity class.

        Args:
            entity_class: Entity class to register
            name: Optional name to register the entity with (defaults to resource_name)
        """
        entity_name = name or entity_class.resource_name
        if not entity_name:
            raise ValueError(ENTITY_NAME_REQUIRED)
        self._entities[entity_name] = entity_class

    def get(self, name: str, base_path: str = "") -> BaseEntity[T]:
        """
        Get an entity instance by name.

        Args:
            name: Entity name
            base_path: Optional base path for the entity

        Returns:
            Entity instance

        Raises:
            KeyError: If the entity is not registered
        """
        if name not in self._entities:
            raise KeyError(ENTITY_NOT_REGISTERED.format(name=name))
        entity_class = self._entities[name]
        return entity_class(self.client, base_path)
