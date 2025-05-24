"""
Entity filtering module for DCApiX.

This module provides classes for building complex filter expressions
for entity queries.
"""

from enum import Enum, auto
from typing import Any


class FilterOperator(Enum):
    """Filter operators supported by the entity API."""

    EQ = auto()  # Equal
    NEQ = auto()  # Not equal
    GT = auto()  # Greater than
    GTE = auto()  # Greater than or equal
    LT = auto()  # Less than
    LTE = auto()  # Less than or equal
    CONTAINS = auto()  # Contains substring
    STARTSWITH = auto()  # Starts with
    ENDSWITH = auto()  # Ends with
    IN = auto()  # In list
    ISNULL = auto()  # Is null
    ISNOTNULL = auto()  # Is not null


class FilterExpression:
    """
    A filter expression for entity queries.

    This class represents a single filter condition with a field name,
    operator, and value.
    """

    # Operator mapping to URL query parameter suffixes
    _OP_MAP = {
        FilterOperator.EQ: "",
        FilterOperator.NEQ: "__ne",
        FilterOperator.GT: "__gt",
        FilterOperator.GTE: "__gte",
        FilterOperator.LT: "__lt",
        FilterOperator.LTE: "__lte",
        FilterOperator.CONTAINS: "__contains",
        FilterOperator.STARTSWITH: "__startswith",
        FilterOperator.ENDSWITH: "__endswith",
        FilterOperator.IN: "__in",
        FilterOperator.ISNULL: "__isnull",
        FilterOperator.ISNOTNULL: "__isnotnull",
    }

    def __init__(self, field: str, operator: FilterOperator, value: Any = None) -> None:
        """
        Initialize a filter expression.

        Args:
            field: The field name to filter on
            operator: The filter operator
            value: The filter value (optional for some operators)
        """
        self.field = field
        self.operator = operator
        self.value = value

    def to_params(self) -> dict[str, Any]:
        """
        Convert the filter expression to query parameters.

        Returns:
            Dictionary of query parameters
        """
        suffix = self._OP_MAP.get(self.operator, "")
        param_name = f"{self.field}{suffix}"

        # Special handling for IS NULL and IS NOT NULL
        if self.operator in (FilterOperator.ISNULL, FilterOperator.ISNOTNULL):
            return {param_name: "true"}

        # Special handling for IN operator
        if self.operator == FilterOperator.IN and isinstance(
            self.value,
            list | tuple[Any, ...],
        ):
            # Convert list to comma-separated string
            return {param_name: ",".join(str(v) for v in self.value)}

        return {param_name: self.value}


class EntityFilter:
    """
    A collection of filter expressions for entity queries.

    This class allows building complex filter conditions by combining
    multiple expressions.
    """

    def __init__(self) -> None:
        """Initialize an empty filter collection."""
        self.expressions: list[FilterExpression] = []

    def add(self, expression: FilterExpression) -> "EntityFilter":
        """
        Add a filter expression.

        Args:
            expression: The filter expression to add

        Returns:
            Self for chaining
        """
        self.expressions.append(expression)
        return self

    def eq(self, field: str, value: Any) -> "EntityFilter":
        """Add an equals filter."""
        return self.add(FilterExpression(field, FilterOperator.EQ, value))

    def ne(self, field: str, value: Any) -> "EntityFilter":
        """Add a not-equals filter."""
        return self.add(FilterExpression(field, FilterOperator.NEQ, value))

    def gt(self, field: str, value: Any) -> "EntityFilter":
        """Add a greater-than filter."""
        return self.add(FilterExpression(field, FilterOperator.GT, value))

    def gte(self, field: str, value: Any) -> "EntityFilter":
        """Add a greater-than-or-equal filter."""
        return self.add(FilterExpression(field, FilterOperator.GTE, value))

    def lt(self, field: str, value: Any) -> "EntityFilter":
        """Add a less-than filter."""
        return self.add(FilterExpression(field, FilterOperator.LT, value))

    def lte(self, field: str, value: Any) -> "EntityFilter":
        """Add a less-than-or-equal filter."""
        return self.add(FilterExpression(field, FilterOperator.LTE, value))

    def contains(self, field: str, value: str) -> "EntityFilter":
        """Add a contains filter."""
        return self.add(FilterExpression(field, FilterOperator.CONTAINS, value))

    def startswith(self, field: str, value: str) -> "EntityFilter":
        """Add a starts-with filter."""
        return self.add(FilterExpression(field, FilterOperator.STARTSWITH, value))

    def endswith(self, field: str, value: str) -> "EntityFilter":
        """Add an ends-with filter."""
        return self.add(FilterExpression(field, FilterOperator.ENDSWITH, value))

    def in_list(self, field: str, values: list[Any]) -> "EntityFilter":
        """Add an in-list filter."""
        return self.add(FilterExpression(field, FilterOperator.IN, values))

    def is_null(self, field: str) -> "EntityFilter":
        """Add an is-null filter."""
        return self.add(FilterExpression(field, FilterOperator.ISNULL))

    def is_not_null(self, field: str) -> "EntityFilter":
        """Add an is-not-null filter."""
        return self.add(FilterExpression(field, FilterOperator.ISNOTNULL))

    def to_params(self) -> dict[str, Any]:
        """
        Convert all expressions to query parameters.

        Returns:
            Dictionary of query parameters
        """
        params = {}
        for expr in self.expressions:
            params.update(expr.to_params())
        return params
