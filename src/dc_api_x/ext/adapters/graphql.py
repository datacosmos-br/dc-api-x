"""
GraphQL adapter for DCApiX.

This module defines the GraphQLAdapter abstract class for GraphQL operations.
"""

import abc
from collections.abc import Callable
from typing import Any, Optional

from .protocol import ProtocolAdapter


class GraphQLAdapter(ProtocolAdapter):
    """Base interface for GraphQL adapters."""

    @abc.abstractmethod
    def execute(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Name of the operation to execute

        Returns:
            Query result as a dictionary with 'data' and possibly 'errors' fields
        """

    @abc.abstractmethod
    def execute_batch(
        self,
        operations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Execute multiple GraphQL operations in a single batch.

        Args:
            operations: List of operations, each with 'query', 'variables', and
                        optionally 'operationName' keys

        Returns:
            List of results corresponding to each operation
        """

    @abc.abstractmethod
    def introspect(self) -> dict[str, Any]:
        """
        Perform an introspection query to retrieve the GraphQL schema.

        Returns:
            Schema definition
        """

    @abc.abstractmethod
    def subscribe(
        self,
        subscription: str,
        callback: Callable[[dict[str, Any]], None],
        variables: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Subscribe to a GraphQL subscription.

        Args:
            subscription: GraphQL subscription query
            callback: Function to call when subscription data is received
            variables: Subscription variables

        Returns:
            Subscription object or ID that can be used to unsubscribe
        """

    @abc.abstractmethod
    def unsubscribe(self, subscription_id: Any) -> None:
        """
        Unsubscribe from a GraphQL subscription.

        Args:
            subscription_id: ID returned from subscribe
        """
