"""
GraphQL adapter for DCApiX.

This module defines the GraphQLAdapter class for interacting with GraphQL endpoints.
"""

import abc
from collections.abc import Callable
from typing import Any, Optional, TypeVar

from ...exceptions import AdapterError, InvalidOperationError
from .protocol import ProtocolAdapter

# Use TypeVar for the session type
SessionType = TypeVar("SessionType")


def validate_not_empty(value: str, name: str) -> None:
    """Validate that a string is not empty.

    Args:
        value: The string to validate
        name: Name of the parameter being validated

    Raises:
        ValueError: If the string is empty or None
    """
    if not value or not value.strip():
        raise ValueError(f"{name} cannot be empty")


class GraphQLAdapter(ProtocolAdapter):
    """Base interface for GraphQL adapters."""

    @abc.abstractmethod
    def execute(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL operation.

        Args:
            query: GraphQL query/mutation
            variables: Optional variables for the operation
            operation_name: Optional operation name

        Returns:
            Operation result data
        """

    @abc.abstractmethod
    def execute_batch(
        self,
        operations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Execute a batch of GraphQL operations.

        Args:
            operations: List of operations with shape {"query": "...", "variables": {...}}

        Returns:
            List of operation results
        """

    @abc.abstractmethod
    def introspect(self) -> dict[str, Any]:
        """Get the GraphQL schema through introspection.

        Returns:
            Schema introspection data
        """

    @abc.abstractmethod
    def subscribe(
        self,
        subscription: str,
        callback: Callable[[dict[str, Any]], None],
        variables: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Subscribe to a GraphQL subscription.

        Args:
            subscription: GraphQL subscription query
            callback: Function to call with subscription data
            variables: Optional variables for the subscription

        Returns:
            Subscription ID for unsubscribing
        """

    @abc.abstractmethod
    def unsubscribe(self, subscription_id: Any) -> None:
        """Unsubscribe from a GraphQL subscription.

        Args:
            subscription_id: Subscription ID from subscribe()
        """

    def __init__(
        self,
        url: str,
        request_handler: Optional[
            Callable[[str, dict[str, Any]], dict[str, Any]]
        ] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        """Initialize the GraphQL adapter.

        Args:
            url: GraphQL endpoint URL
            request_handler: Optional custom request handler
            headers: Optional HTTP headers for requests
        """
        self.url = url
        self.request_handler = request_handler
        self.headers = headers or {}
        # Initialize with Any type to allow Session later
        self._client: Any = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to the GraphQL endpoint.

        Returns:
            True if the connection was successful, False otherwise
        """
        try:
            # Attempt to import and setup the client
            from requests import Session

            # Create a new session
            client: Session = Session()

            # Add headers to the client
            if self.headers:
                for header, value in self.headers.items():
                    client.headers[header] = value

            # Assign to self._client after setup
            self._client = client
            self._connected = True
            return True

        except ImportError:

            def _no_requests_error():
                return AdapterError("Could not import 'requests'")

            raise _no_requests_error()
        except Exception as e:

            def _connection_error(err):
                return AdapterError(
                    f"Failed to connect to GraphQL endpoint: {str(err)}",
                )

            raise _connection_error(e)

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
            variables: Optional variables for cthe query/mutation
            operation_name: Optional operation name if multiple operations exist in the query

        Returns:
            Response data from the GraphQL server

        Raises:
            AdapterError: If there's an issue making the request
        """
        if not self.is_connected():
            self.connect()

        # Prepare request payload
        payload: dict[str, Any] = {"query": query}
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

                def _no_client_error():
                    return AdapterError("No GraphQL client available")

                raise _no_client_error()

            response = self._client.post(self.url, json=payload)
            response.raise_for_status()
            response_data = response.json()

            # Check for GraphQL errors
            if "errors" in response_data:
                error_messages = [
                    error.get("message", "Unknown error")
                    for error in response_data["errors"]
                ]

                def _graphql_errors():
                    return AdapterError(f"GraphQL errors: {', '.join(error_messages)}")

                raise _graphql_errors()

            return response_data
        except Exception as e:
            if not isinstance(e, AdapterError):

                def _request_error(err):
                    return AdapterError(f"GraphQL request failed: {str(err)}")

                raise _request_error(e) from e
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

            def _missing_data_error():
                return AdapterError("Response missing data field")

            raise _missing_data_error()

        # Get data from response
        data: Any = response["data"]

        # Handle the case where data might be a string
        if isinstance(data, str):
            import json

            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict):
                    return parsed_data
            except json.JSONDecodeError:
                # If JSON parsing fails, continue with original handling
                pass

        # Handle the case where data is already a dict
        if isinstance(data, dict):
            return data

        # Return empty dict if data is neither a valid JSON string nor a dict
        return {}

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

            def _invalid_mutation_error():
                return InvalidOperationError(
                    "Mutation string must start with 'mutation'. "
                    "Did you mean to use query() instead?",
                )

            raise _invalid_mutation_error()

        response = self._make_request(mutation, variables, operation_name)
        if "data" not in response:

            def _missing_data_error():
                return AdapterError("Response missing data field")

            raise _missing_data_error()

        # Get data from response
        data: Any = response["data"]

        # Handle the case where data might be a string
        if isinstance(data, str):
            import json

            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict):
                    return parsed_data
            except json.JSONDecodeError:
                # If JSON parsing fails, continue with original handling
                pass

        # Handle the case where data is already a dict
        if isinstance(data, dict):
            return data

        # Return empty dict if data is neither a valid JSON string nor a dict
        return {}
