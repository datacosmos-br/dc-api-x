"""
Base Entity implementation for DCApiX.

This module provides the main BaseEntity class that all entities should inherit from.
It implements CRUD operations with support for pagination, filtering and sorting.
"""

import builtins
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, ClassVar, Generic, TypeVar, Union

from pydantic import BaseModel

# Import from relative modules instead of dc_api_x to avoid circular imports
from ..pagination import PaginationConfig, paginate
from .filters import EntityFilter
from .sorters import EntitySorter, SortDirection

# Type variable for entity models
T = TypeVar("T", bound=BaseModel)

# Error message constants
MISSING_RESOURCE_NAME_ERROR = "resource_name must be specified for entity"
GET_ENTITY_ERROR = "Failed to retrieve {}: {}"
LIST_ENTITY_ERROR = "Failed to list {} entities: {}"
PAGINATION_ERROR = "Pagination failed for {}: {}"
CREATE_ENTITY_ERROR = "Failed to create {}: {}"
UPDATE_ENTITY_ERROR = "Failed to update {}: {}"
PARTIAL_UPDATE_ENTITY_ERROR = "Failed to partially update {}: {}"
DELETE_ENTITY_ERROR = "Failed to delete {}: {}"
BULK_CREATE_ENTITY_ERROR = "Failed to bulk create {}: {}"
BULK_UPDATE_ENTITY_ERROR = "Failed to bulk update {}: {}"
BULK_DELETE_ENTITY_ERROR = "Failed to bulk delete {}: {}"
CUSTOM_ACTION_ERROR = "Failed to execute '{}' on {}: {}"
NO_MODEL_CLASS_ERROR = "No model class defined for entity"


@dataclass
class PaginateOptions:
    """Options for paginating entities."""

    filters: Union[dict[str, Any], EntityFilter, None] = None
    sort_by: str | None = None
    sort_order: Union[str, SortDirection] = SortDirection.ASC
    page_size: int | None = None
    max_pages: int | None = None
    params: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class ListOptions:
    """Options for listing entities."""

    filters: Union[dict[str, Any], EntityFilter, None] = None
    sort_by: str | None = None
    sort_order: Union[str, SortDirection] = SortDirection.ASC
    limit: int | None = None
    offset: int | None = None
    params: dict[str, Any] | None = field(default_factory=dict)

    def to_paginate_options(self) -> "PaginateOptions":
        """Convert list options to paginate options."""
        return PaginateOptions(
            filters=self.filters,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            page_size=self.limit,
            params=self.params,
        )


class BaseEntity(Generic[T]):
    """
    Base class for all API entities.

    This class provides CRUD operations for entities with support for
    pagination, filtering and sorting. It can be used with or without
    a model class.
    """

    # Class-level configuration
    model_class: ClassVar[type[T] | None] = None
    resource_name: ClassVar[str] = ""
    id_field: ClassVar[str] = "id"
    filterable_fields: ClassVar[list[str]] = []
    sortable_fields: ClassVar[list[str]] = []
    default_sort_field: ClassVar[str | None] = None
    default_sort_direction: ClassVar[SortDirection] = SortDirection.ASC
    pagination_config: ClassVar[PaginationConfig] = PaginationConfig()

    def __init__(self, client: Any, base_path: str = ""):
        """
        Initialize a new entity instance.

        Args:
            client: The API client to use for requests
            base_path: Optional base path to prepend to the resource path
        """
        self.client = client
        self.base_path = base_path.rstrip("/")

        # Validate the entity configuration
        if not self.resource_name:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.ValidationError(MISSING_RESOURCE_NAME_ERROR)

    @property
    def resource_path(self) -> str:
        """Get the resource path for the entity."""
        if not self.base_path:
            return self.resource_name
        return f"{self.base_path}/{self.resource_name}"

    def get(
        self,
        entity_id: str | int,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any]:
        """
        Get a single entity by ID.

        Args:
            entity_id: The entity ID
            params: Optional query parameters

        Returns:
            The entity data as a model instance or dictionary

        Raises:
            EntityError: If the request fails
        """
        endpoint = f"{self.resource_path}/{entity_id}"
        response = self.client.get(endpoint, params=params)

        if not response.success:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                GET_ENTITY_ERROR.format(self.resource_name, response.error),
            )

        # Convert to model if a model class is defined
        if self.model_class and response.data:
            return self._to_model(response.data)

        return response.data or {}

    def list(
        self,
        options: ListOptions | None = None,
    ) -> Any:  # Return type is ApiResponse
        """
        List entities with filtering and sorting.

        Args:
            options: Options for listing entities

        Returns:
            API response with list of entities

        Raises:
            EntityError: If the request fails
        """
        if options is None:
            options = ListOptions()

        # Prepare parameters
        query_params = options.params.copy() if options.params else {}

        # Apply filters
        if options.filters:
            if isinstance(options.filters, EntityFilter):
                # Use the entity filter object
                filter_params = options.filters.to_params()
                query_params.update(filter_params)
            else:
                # Use the simple dictionary filters
                query_params.update(options.filters)

        # Apply sorting
        sort_field = options.sort_by or self.default_sort_field
        if sort_field:
            if isinstance(options.sort_order, str):
                sort_direction = (
                    SortDirection.DESC
                    if options.sort_order.lower() == "desc"
                    else SortDirection.ASC
                )
            else:
                sort_direction = options.sort_order

            # Create a sorter and add it to the parameters
            sorter = EntitySorter(sort_field, sort_direction)
            query_params.update(sorter.to_params())

        # Apply pagination
        if options.limit is not None:
            query_params["limit"] = options.limit
        if options.offset is not None:
            query_params["offset"] = options.offset

        try:
            return self.client.get(self.resource_path, params=query_params)
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                LIST_ENTITY_ERROR.format(self.resource_name, str(e)),
            )

    # For backward compatibility
    def list_with_params(
        self,
        filters: dict[str, Any] | EntityFilter | None = None,
        sort_by: str | None = None,
        sort_order: str | SortDirection = SortDirection.ASC,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        List entities with filtering and sorting (backward compatibility).

        Args:
            filters: Dictionary of filter conditions or EntityFilter instance
            sort_by: Field name to sort by
            sort_order: Sort direction (asc or desc)
            limit: Maximum number of results to return
            offset: Offset for pagination
            params: Additional query parameters

        Returns:
            API response with list of entities
        """
        options = ListOptions(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            params=params or {},
        )
        return self.list(options)

    def paginate(
        self,
        options: PaginateOptions | None = None,
    ) -> Iterator[T | dict[str, Any]]:
        """
        Paginate through all entities with filtering and sorting.

        This method handles pagination automatically and yields each entity.

        Args:
            options: Options for paginating entities

        Yields:
            Each entity as a model instance or dictionary

        Raises:
            EntityError: If the request fails
        """
        if options is None:
            options = PaginateOptions()

        # Prepare parameters
        query_params = options.params.copy() if options.params else {}

        # Apply filters
        if options.filters:
            if isinstance(options.filters, EntityFilter):
                # Use the entity filter object
                filter_params = options.filters.to_params()
                query_params.update(filter_params)
            else:
                # Use the simple dictionary filters
                query_params.update(options.filters)

        # Apply sorting
        sort_field = options.sort_by or self.default_sort_field
        if sort_field:
            if isinstance(options.sort_order, str):
                sort_direction = (
                    SortDirection.DESC
                    if options.sort_order.lower() == "desc"
                    else SortDirection.ASC
                )
            else:
                sort_direction = options.sort_order

            # Create a sorter and add it to the parameters
            sorter = EntitySorter(sort_field, sort_direction)
            query_params.update(sorter.to_params())

        # Configure pagination
        config = PaginationConfig(
            page_size=options.page_size or self.pagination_config.page_size,
            max_pages=options.max_pages or self.pagination_config.max_pages,
            params=query_params,
            data_key=self.pagination_config.data_key,
            page_param=self.pagination_config.page_param,
            page_size_param=self.pagination_config.page_size_param,
        )

        try:
            # Use the paginate function from the pagination module
            yield from paginate(
                self.client,
                self.resource_path,
                model_class=self.model_class,
                config=config,
            )
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                PAGINATION_ERROR.format(self.resource_name, str(e)),
            ) from e

    # For backward compatibility
    def paginate_with_params(
        self,
        filters: dict[str, Any] | EntityFilter | None = None,
        sort_by: str | None = None,
        sort_order: str | SortDirection = SortDirection.ASC,
        page_size: int | None = None,
        max_pages: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Iterator[T | dict[str, Any]]:
        """
        Paginate through entities with filtering and sorting (backward compatibility).

        Args:
            filters: Dictionary of filter conditions or EntityFilter instance
            sort_by: Field name to sort by
            sort_order: Sort direction (asc or desc)
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch
            params: Additional query parameters

        Yields:
            Each entity as a model instance or dictionary
        """
        options = PaginateOptions(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page_size=page_size,
            max_pages=max_pages,
            params=params or {},
        )
        yield from self.paginate(options)

    def create(self, data: dict[str, Any] | T) -> T | dict[str, Any]:
        """
        Create a new entity.

        Args:
            data: Entity data as dictionary or model instance

        Returns:
            The created entity as a model instance or dictionary

        Raises:
            EntityError: If the request fails
        """
        # Convert model to dict if needed
        payload = self._to_dict(data) if isinstance(data, BaseModel) else data

        try:
            response = self.client.post(self.resource_path, json_data=payload)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    CREATE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                CREATE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def update(
        self,
        entity_id: str | int,
        data: dict[str, Any] | T,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any]:
        """
        Update an existing entity.

        Args:
            entity_id: The entity ID
            data: Updated entity data as dictionary or model instance
            params: Optional query parameters

        Returns:
            The updated entity as a model instance or dictionary

        Raises:
            EntityError: If the request fails
        """
        endpoint = f"{self.resource_path}/{entity_id}"

        # Convert model to dict if needed
        payload = self._to_dict(data) if isinstance(data, BaseModel) else data

        try:
            response = self.client.put(endpoint, json_data=payload, params=params)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    UPDATE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                UPDATE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def partial_update(
        self,
        entity_id: str | int,
        data: dict[str, Any] | T,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any]:
        """
        Partially update an entity (PATCH).

        Args:
            entity_id: The entity ID
            data: The fields to update as dictionary or model instance
            params: Optional query parameters

        Returns:
            The updated entity as a model instance or dictionary

        Raises:
            EntityError: If the request fails
        """
        endpoint = f"{self.resource_path}/{entity_id}"

        # Convert model to dict if needed
        payload = self._to_dict(data) if isinstance(data, BaseModel) else data

        try:
            response = self.client.patch(endpoint, json_data=payload, params=params)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    PARTIAL_UPDATE_ENTITY_ERROR.format(
                        self.resource_name,
                        response.error,
                    ),
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                PARTIAL_UPDATE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def delete(
        self,
        entity_id: str | int,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: The entity ID
            params: Optional query parameters

        Returns:
            True if the deletion was successful

        Raises:
            EntityError: If the request fails
        """
        endpoint = f"{self.resource_path}/{entity_id}"

        try:
            response = self.client.delete(endpoint, params=params)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    DELETE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            return True
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                DELETE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def bulk_create(
        self, items: builtins.list[dict[str, Any] | T]
    ) -> builtins.list[T | dict[str, Any]]:
        """
        Create multiple entities in a single request.

        Args:
            items: List of entity data as dictionaries or model instances

        Returns:
            List of created entities as model instances or dictionaries

        Raises:
            EntityError: If the request fails
        """
        # Convert models to dicts if needed
        payload = [
            self._to_dict(item) if isinstance(item, BaseModel) else item
            for item in items
        ]

        try:
            endpoint = f"{self.resource_path}/bulk"
            response = self.client.post(endpoint, json_data=payload)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    BULK_CREATE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            result = response.data or []

            # Convert to models if a model class is defined
            if self.model_class and isinstance(result, list):
                return [self._to_model(item) for item in result]

            return result
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                BULK_CREATE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def bulk_update(
        self,
        items: builtins.list[tuple[str | int, dict[str, Any] | T]],
    ) -> builtins.list[T | dict[str, Any]]:
        """
        Update multiple entities in a single request.

        Args:
            items: List of tuples containing (entity_id, data)

        Returns:
            List of updated entities as model instances or dictionaries

        Raises:
            EntityError: If the request fails
        """
        # Convert models to dicts if needed
        payload = []
        for entity_id, data in items:
            data_dict = self._to_dict(data) if isinstance(data, BaseModel) else data
            item_payload = {self.id_field: entity_id}
            item_payload.update(data_dict)
            payload.append(item_payload)

        try:
            endpoint = f"{self.resource_path}/bulk"
            response = self.client.put(endpoint, json_data=payload)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    BULK_UPDATE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            result = response.data or []

            # Convert to models if a model class is defined
            if self.model_class and isinstance(result, list):
                return [self._to_model(item) for item in result]

            return result
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                BULK_UPDATE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def bulk_delete(self, ids: builtins.list[str | int]) -> bool:
        """
        Delete multiple entities in a single request.

        Args:
            ids: List of entity IDs to delete

        Returns:
            True if all deletions were successful

        Raises:
            EntityError: If the request fails
        """
        try:
            endpoint = f"{self.resource_path}/bulk"
            payload = {self.id_field: ids}
            response = self.client.delete(endpoint, json_data=payload)

            if not response.success:
                # Import here to avoid circular imports
                from .. import exceptions

                raise exceptions.EntityError(
                    BULK_DELETE_ENTITY_ERROR.format(self.resource_name, response.error),
                )

            return True
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                BULK_DELETE_ENTITY_ERROR.format(self.resource_name, str(e)),
            ) from e

    def custom_action(
        self,
        action: str,
        entity_id: str | int | None = None,
        data: dict[str, Any] | None = None,
        method: str = "POST",
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a custom action on an entity or collection.

        Args:
            action: The action name
            entity_id: Optional entity ID (for resource-specific actions)
            data: Optional payload data
            method: HTTP method to use (default: POST)
            params: Optional query parameters

        Returns:
            API response

        Raises:
            EntityError: If the request fails
        """
        if entity_id:
            endpoint = f"{self.resource_path}/{entity_id}/{action}"
        else:
            endpoint = f"{self.resource_path}/{action}"

        try:
            if method.upper() == "GET":
                return self.client.get(endpoint, params=params)
            if method.upper() == "POST":
                return self.client.post(endpoint, json_data=data, params=params)
            if method.upper() == "PUT":
                return self.client.put(endpoint, json_data=data, params=params)
            if method.upper() == "PATCH":
                return self.client.patch(endpoint, json_data=data, params=params)
            if method.upper() == "DELETE":
                return self.client.delete(endpoint, json_data=data, params=params)
            raise ValueError(f"Unsupported HTTP method: {method}")
        except Exception as e:
            # Import here to avoid circular imports
            from .. import exceptions

            raise exceptions.EntityError(
                CUSTOM_ACTION_ERROR.format(action, self.resource_name, str(e)),
            ) from e

    def _to_model(self, data: dict[str, Any]) -> T:
        """Convert dictionary data to a model instance."""
        if not self.model_class:
            raise RuntimeError(NO_MODEL_CLASS_ERROR)

        if hasattr(self.model_class, "model_validate"):
            # Pydantic v2
            return self.model_class.model_validate(data)

        # Pydantic v1 fallback
        return self.model_class(**data)

    def _to_dict(self, model: T) -> dict[str, Any]:
        """Convert a model instance to a dictionary."""
        if hasattr(model, "model_dump"):
            # Pydantic v2
            return model.model_dump()

        # Pydantic v1 fallback
        return model.dict()
