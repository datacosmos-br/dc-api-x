"""
GraphQL adapter for DCApiX.

This module defines the GraphQLAdapter abstract class for GraphQL operations.
"""

import abc
from collections.abc import Callable
from typing import Any, Optional, TypeVar

from ...exceptions import AdapterError, InvalidOperationError
from ...utils.validation import validate_not_empty
from .protocol import ProtocolAdapter

T = TypeVar("T")


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

    def __init__(
        self,
        url: str,
        request_handler: Optional[
            Callable[[str, dict[str, Any]], dict[str, Any]]
        ] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        """Initialize GraphQL adapter.

        Args:
            url: GraphQL endpoint URL
            request_handler: Optional custom request handler for making requests
            headers: Optional default headers for all requests
        """
        self.url = url
        self.request_handler = request_handler
        self.headers = headers or {}
        self._connected = False
        self._client = None

    def connect(self) -> bool:
        """Connect to the GraphQL endpoint.

        Returns:
            True if the connection was successful, False otherwise
        """
        try:
            # Attempt to import and setup the client
            # This can be customized based on the chosen implementation
            import requests

            self._client = requests.Session()
            for header, value in self.headers.items():
                self._client.headers[header] = value

            self._connected = True
            return True
        except ImportError:
            raise AdapterError(
                "Could not import 'requests'. Please install it with 'pip install requests'",
            )
        except Exception as e:
            raise AdapterError(f"Failed to connect to GraphQL endpoint: {str(e)}")

    def disconnect(self) -> bool:
        """Disconnect from the GraphQL endpoint.

        Returns:
            True if the disconnection was successful, False otherwise
        """
        if self._client:
            if hasattr(self._client, "close"):
                self._client.close()
            self._client = None
        self._connected = False
        return True

    def is_connected(self) -> bool:
        """Check if the adapter is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    def set_option(self, name: str, value: Any) -> None:
        """Set an adapter option.

        Args:
            name: Option name
            value: Option value
        """
        if name == "headers":
            if isinstance(value, dict):
                self.headers.update(value)
            else:
                raise ValueError("Headers must be a dictionary")
        elif name == "url":
            self.url = str(value)
        else:
            raise ValueError(f"Unknown option: {name}")

    def _make_request(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Make a request to the GraphQL endpoint.

        Args:
            query: GraphQL query or mutation
            variables: Optional variables for the query/mutation
            operation_name: Optional operation name if multiple operations exist in the query

        Returns:
            Response data from the GraphQL server

        Raises:
            AdapterError: If there's an issue making the request
        """
        if not self.is_connected():
            self.connect()

        # Prepare request payload
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        try:
            # Use custom request handler if provided
            if self.request_handler:
                response_data = self.request_handler(self.url, payload)
                return response_data

            # Otherwise use the default HTTP client
            if not self._client:
                raise AdapterError("No GraphQL client available")

            response = self._client.post(self.url, json=payload)
            response.raise_for_status()
            response_data = response.json()

            # Check for GraphQL errors
            if "errors" in response_data:
                error_messages = [
                    error.get("message", "Unknown error")
                    for error in response_data["errors"]
                ]
                raise AdapterError(f"GraphQL errors: {', '.join(error_messages)}")

            return response_data
        except Exception as e:
            if not isinstance(e, AdapterError):
                raise AdapterError(f"GraphQL request failed: {str(e)}")
            raise

    def query(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query
            variables: Optional variables for the query
            operation_name: Optional operation name if multiple operations exist in the query

        Returns:
            Query result data

        Raises:
            AdapterError: If there's an issue with the query
        """
        validate_not_empty(query, "query")

        response = self._make_request(query, variables, operation_name)
        if "data" not in response:
            raise AdapterError("Response missing data field")

        return response["data"]

    def mutation(
        self,
        mutation: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL mutation.

        Args:
            mutation: GraphQL mutation
            variables: Optional variables for the mutation
            operation_name: Optional operation name if multiple operations exist in the mutation

        Returns:
            Mutation result data

        Raises:
            AdapterError: If there's an issue with the mutation
        """
        validate_not_empty(mutation, "mutation")

        # Ensure this is actually a mutation
        if not mutation.strip().startswith("mutation"):
            raise InvalidOperationError(
                "Mutation string must start with 'mutation'. "
                "Did you mean to use query() instead?",
            )

        response = self._make_request(mutation, variables, operation_name)
        if "data" not in response:
            raise AdapterError("Response missing data field")

        return response["data"]
