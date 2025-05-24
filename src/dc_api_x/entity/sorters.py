"""
Entity sorting module for DCApiX.

This module provides classes for building sort expressions
for entity queries.
"""

from enum import Enum


class SortDirection(str, Enum):
    """Sort direction for entity queries."""

    ASC = "asc"
    DESC = "desc"


class EntitySorter:
    """
    A sorter for entity queries.

    This class represents a sort specification with a field name
    and sort direction.
    """

    def __init__(
        self,
        field: str,
        direction: SortDirection = SortDirection.ASC,
    ) -> None:
        """
        Initialize a sort expression.

        Args:
            field: The field name to sort by
            direction: The sort direction (asc or desc)
        """
        self.field = field
        self.direction = direction

    def to_params(self) -> dict[str, str]:
        """
        Convert the sorter to query parameters.

        Returns:
            Dictionary of query parameters
        """
        return {
            "sort": self.field,
            "order": self.direction.value,
        }


class MultiFieldSorter:
    """
    A multi-field sorter for entity queries.

    This class allows sorting by multiple fields with different
    sort directions.
    """

    def __init__(self) -> None:
        """Initialize an empty sorter collection."""
        self.sorters: list[EntitySorter] = []

    def add(
        self,
        field: str,
        direction: SortDirection = SortDirection.ASC,
    ) -> "MultiFieldSorter":
        """
        Add a sort field.

        Args:
            field: The field name to sort by
            direction: The sort direction (asc or desc)

        Returns:
            Self for chaining
        """
        self.sorters.append(EntitySorter(field, direction))
        return self

    def asc(self, field: str) -> "MultiFieldSorter":
        """Add an ascending sort field."""
        return self.add(field, SortDirection.ASC)

    def desc(self, field: str) -> "MultiFieldSorter":
        """Add a descending sort field."""
        return self.add(field, SortDirection.DESC)

    def to_params(self) -> dict[str, str]:
        """
        Convert all sorters to query parameters.

        This method joins multiple sort fields using commas.

        Returns:
            Dictionary of query parameters
        """
        if not self.sorters:
            return {}

        fields = []
        directions = []

        for sorter in self.sorters:
            fields.append(sorter.field)
            directions.append(sorter.direction.value)

        return {
            "sort": ",".join(fields),
            "order": ",".join(directions),
        }
