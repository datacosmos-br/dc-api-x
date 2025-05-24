"""
Example entity classes for DCApiX.

This module provides example entity implementations to demonstrate
how to use the BaseEntity class.
"""

from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field

from dc_api_x.entity.base import BaseEntity
from dc_api_x.entity.sorters import SortDirection
from dc_api_x.pagination import PaginationConfig

# Error message constants
ACTIVATE_USER_FAILED = "Failed to activate user: {error}"
DEACTIVATE_USER_FAILED = "Failed to deactivate user: {error}"


class User(BaseModel):
    """A user entity model."""

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: str = Field(..., alias="createdAt")


class UserEntity(BaseEntity[User]):
    """
    User entity implementation.

    This class demonstrates how to create a concrete entity that uses
    a Pydantic model and configures pagination, filtering, and sorting.
    """

    # Entity configuration
    model_class: ClassVar[type[User]] = User
    resource_name: ClassVar[str] = "users"
    id_field: ClassVar[str] = "id"

    # Fields that can be used for filtering
    filterable_fields: ClassVar[list[str]] = [
        "username",
        "email",
        "is_active",
    ]

    # Fields that can be used for sorting
    sortable_fields: ClassVar[list[str]] = [
        "id",
        "username",
        "email",
        "created_at",
    ]

    # Default sorting
    default_sort_field: ClassVar[str] = "created_at"
    default_sort_direction: ClassVar[SortDirection] = SortDirection.DESC

    # Configure pagination
    pagination_config: ClassVar[PaginationConfig] = PaginationConfig(
        page_size=50,
        data_key="data",
        page_param="page",
        page_size_param="per_page",
    )

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email.

        This demonstrates how to create custom entity methods.

        Args:
            email: User email to search for

        Returns:
            User entity or None if not found
        """
        response = self.list(filters={"email": email})
        if not response.success or not response.data:
            return None

        items = response.data
        if not items or not isinstance(items, list[Any]) or not items:
            return None

        return self._to_model(items[0])

    def activate(self, user_id: int) -> User:
        """
        Activate a user.

        This demonstrates how to use custom actions.

        Args:
            user_id: User ID to activate

        Returns:
            Updated user entity
        """
        response = self.custom_action(
            action="activate",
            entity_id=user_id,
            method="POST",
        )

        if not response.success or not response.data:
            raise ValueError(ACTIVATE_USER_FAILED.format(error=response.error))

        return self._to_model(response.data)

    def deactivate(self, user_id: int) -> User:
        """
        Deactivate a user.

        Args:
            user_id: User ID to deactivate

        Returns:
            Updated user entity
        """
        response = self.custom_action(
            action="deactivate",
            entity_id=user_id,
            method="POST",
        )

        if not response.success or not response.data:
            raise ValueError(DEACTIVATE_USER_FAILED.format(error=response.error))

        return self._to_model(response.data)
