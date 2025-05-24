"""
Base Entity implementation for DCApiX.

This module provides the main BaseEntity class that all entities should inherit from.
It implements CRUD operations with support for pagination, filtering and sorting.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Generic

# Import from relative modules instead of dc_api_x to avoid circular imports
from ..pagination import PaginationConfig
from ..utils.definitions import EntityId, FilterDict, T
from .filters import EntityFilter
from .sorters import EntitySorter, SortDirection

if TYPE_CHECKING:
    from dc_api_x.client import ApiClient

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
UNSUPPORTED_HTTP_METHOD_ERROR = "Unsupported HTTP method: {}"


# Helper functions to avoid TRY301 violations
def _raise_entity_error(
    error_template: str,
    resource_name: str,
    error_message: str,
) -> None:
    """
    Raise an EntityError with formatted message.

    Args:
        error_template: Error message template
        resource_name: Resource name
        error_message: Error message

    Raises:
        EntityError: The formatted error
    """
    # Import here to avoid circular imports
    from ..utils import exceptions

    raise exceptions.EntityError(error_template.format(resource_name, error_message))


def _raise_unsupported_method_error(method: str) -> None:
    """
    Raise an EntityError for unsupported HTTP method.

    Args:
        method: The unsupported HTTP method

    Raises:
        EntityError: The formatted error
    """
    # Import here to avoid circular imports
    from ..utils import exceptions

    raise exceptions.EntityError(UNSUPPORTED_HTTP_METHOD_ERROR.format(method))


@dataclass
class PaginateOptions:
    """Options for paginating entities."""

    filters: FilterDict | EntityFilter | None = None
    sort_by: str | None = None
    sort_order: str | SortDirection = SortDirection.ASC
    page_size: int | None = None
    max_pages: int | None = None
    params: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class ListOptions:
    """Options for listing entities."""

    filters: FilterDict | EntityFilter | None = None
    sort_by: str | None = None
    sort_order: str | SortDirection = SortDirection.ASC
    limit: int | None = None
    offset: int | None = None
    params: dict[str, Any] | None = field(default_factory=dict)

    def to_paginate_options(self) -> PaginateOptions:
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

    def __init__(self, client: ApiClient, base_path: str = "") -> None:
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
            from ..utils import exceptions

            raise exceptions.ValidationError(MISSING_RESOURCE_NAME_ERROR)

    @property
    def resource_path(self) -> str:
        """Get the resource path for the entity."""
        if not self.base_path:
            return self.resource_name
        return f"{self.base_path}/{self.resource_name}"

    def get(
        self,
        entity_id: EntityId,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any] | None:
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
            from ..utils import exceptions

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

            _raise_entity_error(LIST_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def paginate(
        self,
        filters: FilterDict | EntityFilter | None = None,
        sort_by: str | None = None,
        sort_order: str | SortDirection = SortDirection.ASC,
        page_size: int | None = None,
        max_pages: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Iterator[T | dict[str, Any]] | None:
        """
        Paginate through all entities matching the filters.

        Args:
            filters: Optional filters to apply
            sort_by: Optional field to sort by
            sort_order: Optional sort direction
            page_size: Optional page size
            max_pages: Optional maximum number of pages to retrieve
            params: Optional additional query parameters

        Returns:
            Iterator of entity data

        Raises:
            EntityError: If the request fails
        """
        options = PaginateOptions(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page_size=page_size,
            max_pages=max_pages,
            params=params,
        )
        return self.paginate_with_params(options)

    def paginate_with_params(
        self,
        options: PaginateOptions | None = None,
        **kwargs: Any,
    ) -> Iterator[T | dict[str, Any]] | None:
        """
        Paginate through all entities with the specified options.

        Args:
            options: Options for pagination
            **kwargs: Additional parameters to pass to the paginate function

        Returns:
            Iterator of entity data

        Raises:
            EntityError: If the request fails
        """
        if options is None:
            options = PaginateOptions()

        try:
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
            pagination_config = self.pagination_config
            if options.page_size is not None:
                pagination_config.page_size = options.page_size
            if options.max_pages is not None:
                pagination_config.max_pages = options.max_pages

            # Import here to avoid circular imports
            from .. import paginate

            # Use the paginate function to get an iterator
            return paginate(
                client=self.client,
                endpoint=self.resource_path,
                params=query_params,
                config=pagination_config,
                model_class=self.model_class,
                **kwargs,
            )
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(PAGINATION_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def create(self, data: dict[str, Any] | T) -> T | dict[str, Any] | None:
        """
        Create a new entity.

        Args:
            data: Entity data as dictionary or model instance

        Returns:
            Created entity data

        Raises:
            EntityError: If the request fails
        """
        try:
            # Convert model to dictionary if needed
            if hasattr(data, "model_dump"):
                # Pydantic v2
                json_data = data.model_dump()
            elif hasattr(data, "dict"):
                # Pydantic v1
                json_data = data.dict()
            else:
                # Already a dictionary
                json_data = data

            # Send the request
            response = self.client.post(self.resource_path, json_data=json_data)

            if not response.success:
                _raise_entity_error(
                    CREATE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(CREATE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def update(
        self,
        entity_id: EntityId,
        data: dict[str, Any] | T,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any] | None:
        """
        Update an existing entity.

        Args:
            entity_id: The entity ID
            data: Entity data as dictionary or model instance
            params: Optional query parameters

        Returns:
            Updated entity data

        Raises:
            EntityError: If the request fails
        """
        try:
            # Convert model to dictionary if needed
            if hasattr(data, "model_dump"):
                # Pydantic v2
                json_data = data.model_dump()
            elif hasattr(data, "dict"):
                # Pydantic v1
                json_data = data.dict()
            else:
                # Already a dictionary
                json_data = data

            # Send the request
            endpoint = f"{self.resource_path}/{entity_id}"
            response = self.client.put(endpoint, json_data=json_data, params=params)

            if not response.success:
                _raise_entity_error(
                    UPDATE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(UPDATE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def partial_update(
        self,
        entity_id: EntityId,
        data: dict[str, Any] | T,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any] | None:
        """
        Partially update an existing entity.

        Args:
            entity_id: The entity ID
            data: Entity data as dictionary or model instance
            params: Optional query parameters

        Returns:
            Updated entity data

        Raises:
            EntityError: If the request fails
        """
        try:
            # Convert model to dictionary if needed
            if hasattr(data, "model_dump"):
                # Pydantic v2
                json_data = data.model_dump(exclude_unset=True)
            elif hasattr(data, "dict"):
                # Pydantic v1
                json_data = data.dict(exclude_unset=True)
            else:
                # Already a dictionary
                json_data = data

            # Send the request
            endpoint = f"{self.resource_path}/{entity_id}"
            response = self.client.patch(endpoint, json_data=json_data, params=params)

            if not response.success:
                _raise_entity_error(
                    PARTIAL_UPDATE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            # Convert to model if a model class is defined
            if self.model_class and response.data:
                return self._to_model(response.data)

            return response.data or {}
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(PARTIAL_UPDATE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def delete(
        self,
        entity_id: EntityId,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Delete an entity by ID.

        Args:
            entity_id: The entity ID
            params: Optional query parameters

        Returns:
            True if deletion was successful

        Raises:
            EntityError: If the request fails
        """
        try:
            # Send the request
            endpoint = f"{self.resource_path}/{entity_id}"
            response = self.client.delete(endpoint, params=params)

            if not response.success:
                _raise_entity_error(
                    DELETE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            return response.success
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(DELETE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return False

    def bulk_create(
        self,
        items: list[dict[str, Any] | T],
    ) -> list[T | dict[str, Any]] | None:
        """
        Create multiple entities in a single request.

        Args:
            items: List of entity data as dictionaries or model instances

        Returns:
            List of created entities

        Raises:
            EntityError: If the request fails
        """
        try:
            # Convert models to dictionaries if needed
            json_data = []
            for item in items:
                if hasattr(item, "model_dump"):
                    # Pydantic v2
                    json_data.append(item.model_dump())
                elif hasattr(item, "dict"):
                    # Pydantic v1
                    json_data.append(item.dict())
                else:
                    # Already a dictionary
                    json_data.append(item)

            # Send the request
            endpoint = f"{self.resource_path}/bulk"
            response = self.client.post(endpoint, json_data={"items": json_data})

            if not response.success:
                _raise_entity_error(
                    BULK_CREATE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            # Convert to models if a model class is defined
            if self.model_class and response.data and isinstance(response.data, list):
                return [self._to_model(item) for item in response.data]

            return response.data or []
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(BULK_CREATE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def bulk_update(
        self,
        items: list[tuple[EntityId, dict[str, Any] | T]],
    ) -> list[T | dict[str, Any]] | None:
        """
        Update multiple entities in a single request.

        Args:
            items: List of (entity_id, data) tuples

        Returns:
            List of updated entities

        Raises:
            EntityError: If the request fails
        """
        try:
            # Convert models to dictionaries if needed
            json_data = []
            for entity_id, item in items:
                if hasattr(item, "model_dump"):
                    # Pydantic v2
                    data = item.model_dump()
                elif hasattr(item, "dict"):
                    # Pydantic v1
                    data = item.dict()
                else:
                    # Already a dictionary
                    data = item

                # Add the ID field to the data
                json_data.append({self.id_field: entity_id, **data})

            # Send the request
            endpoint = f"{self.resource_path}/bulk"
            response = self.client.put(endpoint, json_data={"items": json_data})

            if not response.success:
                _raise_entity_error(
                    BULK_UPDATE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            # Convert to models if a model class is defined
            if self.model_class and response.data and isinstance(response.data, list):
                return [self._to_model(item) for item in response.data]

            return response.data or []
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(BULK_UPDATE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return None

    def bulk_delete(self, ids: list[EntityId]) -> bool:
        """
        Delete multiple entities in a single request.

        Args:
            ids: List of entity IDs to delete

        Returns:
            True if all entities were deleted successfully

        Raises:
            EntityError: If the request fails
        """
        try:
            # Send the request
            endpoint = f"{self.resource_path}/bulk"
            response = self.client.delete(endpoint, json_data={"ids": ids})

            if not response.success:
                _raise_entity_error(
                    BULK_DELETE_ENTITY_ERROR,
                    self.resource_name,
                    response.error or "Unknown error",
                )

            return response.success
        except Exception as e:
            # Import here to avoid circular imports

            _raise_entity_error(BULK_DELETE_ENTITY_ERROR, self.resource_name, str(e))
            # This return is needed for type checking but never reached
            return False

    def custom_action(
        self,
        action: str,
        entity_id: EntityId | None = None,
        data: dict[str, Any] | None = None,
        method: str = "POST",
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a custom action on the entity.

        Args:
            action: The action name
            entity_id: Optional entity ID for entity-specific actions
            data: Optional data to send with the request
            method: HTTP method to use (GET, POST, PUT, PATCH, DELETE)
            params: Optional query parameters

        Returns:
            Action response

        Raises:
            EntityError: If the request fails
        """
        try:
            # Build the endpoint URL
            if entity_id is not None:
                endpoint = f"{self.resource_path}/{entity_id}/{action}"
            else:
                endpoint = f"{self.resource_path}/{action}"

            # Send the request based on the method
            method = method.upper()
            if method == "GET":
                return self.client.get(endpoint, params=params)
            if method == "POST":
                return self.client.post(endpoint, json_data=data, params=params)
            if method == "PUT":
                return self.client.put(endpoint, json_data=data, params=params)
            if method == "PATCH":
                return self.client.patch(endpoint, json_data=data, params=params)
            if method == "DELETE":
                return self.client.delete(endpoint, params=params)

            # Unsupported method
            _raise_unsupported_method_error(method)
            # This return is needed for type checking but never reached
            return None
        except Exception as e:
            # Import here to avoid circular imports
            from ..utils import exceptions

            raise exceptions.EntityError(
                CUSTOM_ACTION_ERROR.format(action, self.resource_name, str(e)),
            ) from e

    def _to_model(self, data: dict[str, Any]) -> T:
        """
        Convert dictionary data to a model instance.

        Args:
            data: Dictionary data

        Returns:
            Model instance

        Raises:
            ValueError: If no model class is defined
        """
        if self.model_class is None:
            raise ValueError(NO_MODEL_CLASS_ERROR)
        return self.model_class.model_validate(data)

    def _to_dict(self, model: T) -> dict[str, Any]:
        """
        Convert a model instance to a dictionary.

        Args:
            model: Model instance

        Returns:
            Dictionary representation
        """
        if hasattr(model, "model_dump"):
            # Pydantic v2
            return model.model_dump()
        # Pydantic v1
        return model.dict()
