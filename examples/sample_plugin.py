"""
Sample plugin implementation for DC-API-X.

This module demonstrates how to implement a plugin for DC-API-X that registers
custom adapters, hooks, and providers.
"""

import logging
from typing import Any, Optional

import pluggy
import requests

import dc_api_x as apix
from dc_api_x.ext.adapters import HttpAdapter, ProtocolAdapter
from dc_api_x.ext.auth import AuthProvider, BasicAuthProvider
from dc_api_x.ext.hooks import ErrorHook, RequestHook, ResponseHook
from dc_api_x.ext.providers import (
    ConfigProvider,
    DataProvider,
    SchemaProvider,
    TransformProvider,
)
from dc_api_x.models import ApiResponse

# Register the plugin using the hookimpl marker
hookimpl = pluggy.HookimplMarker("dc_api_x")

logger = logging.getLogger(__name__)


class SampleHttpAdapter(HttpAdapter):
    """A sample HTTP adapter implementation."""

    def __init__(self, base_url: str, **kwargs: Any) -> None:
        """Initialize the adapter.

        Args:
            base_url: Base URL for API requests
            **kwargs: Additional configuration
        """
        super().__init__(base_url, **kwargs)
        self.base_url = base_url
        logger.info("Initialized SampleHttpAdapter with base URL: %s", base_url)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Make an HTTP request.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        logger.debug("SampleHttpAdapter making %s request to %s", method, path)
        return super().request(method, path, **kwargs)


class SampleAuthProvider(BasicAuthProvider):
    """A sample authentication provider implementation."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the provider.

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        super().__init__(username, password)
        logger.info("Initialized SampleAuthProvider for user: %s", username)


class SampleRequestHook(RequestHook):
    """A sample request hook implementation."""

    def __init__(self) -> None:
        """Initialize the hook."""
        self.order = 10
        logger.info("Initialized SampleRequestHook with order: %d", self.order)

    def handle(self, request: Any) -> Any:
        """Process a request.

        Args:
            request: Request to process

        Returns:
            Modified request
        """
        logger.debug("SampleRequestHook processing request")
        if isinstance(request, dict[str, Any]) and "headers" in request:
            request["headers"]["X-Sample-Header"] = "SampleValue"
        return request


class SampleResponseHook(ResponseHook):
    """A sample response hook implementation."""

    def __init__(self) -> None:
        """Initialize the hook."""
        self.order = 10
        logger.info("Initialized SampleResponseHook with order: %d", self.order)

    def handle(self, response: Any) -> Any:
        """Process a response.

        Args:
            response: Response to process

        Returns:
            Modified response
        """
        logger.debug("SampleResponseHook processing response")
        return response


class SampleErrorHook(ErrorHook):
    """A sample error hook implementation."""

    def __init__(self) -> None:
        """Initialize the hook."""
        self.order = 10
        logger.info("Initialized SampleErrorHook with order: %d", self.order)

    def handle(self, error: Exception) -> Optional[ApiResponse]:
        """Process an error.

        Args:
            error: Error to process

        Returns:
            Optional response to return instead of raising the error
        """
        logger.debug("SampleErrorHook processing error: %s", error)
        return None


class SampleSchemaProvider(SchemaProvider):
    """A sample schema provider implementation."""

    def __init__(self) -> None:
        """Initialize the provider."""
        logger.info("Initialized SampleSchemaProvider")

    def get_schema(self, entity_name: str) -> dict[str, Any]:
        """Get the schema for an entity.

        Args:
            entity_name: Name of the entity

        Returns:
            Schema as a dictionary
        """
        logger.debug("SampleSchemaProvider getting schema for: %s", entity_name)
        return {"type": "object", "properties": {"id": {"type": "integer"}}}


class SampleDataProvider(DataProvider[Any]):
    """A sample data provider implementation."""

    def __init__(self) -> None:
        """Initialize the provider."""
        logger.info("Initialized SampleDataProvider")

    def get_data(self, entity_name: str, **_kwargs: Any) -> list[dict]:
        """Get data for an entity.

        Args:
            entity_name: Name of the entity
            **_kwargs: Additional parameters (unused)

        Returns:
            List of data records
        """
        logger.debug("SampleDataProvider getting data for: %s", entity_name)
        return [{"id": 1, "name": "Sample"}]


class SampleConfigProvider(ConfigProvider):
    """A sample configuration provider implementation."""

    def __init__(self) -> None:
        """Initialize the provider."""
        logger.info("Initialized SampleConfigProvider")

    def get_config(self, name: str) -> dict[str, Any]:
        """Get configuration by name.

        Args:
            name: Configuration name

        Returns:
            Configuration dictionary
        """
        logger.debug("SampleConfigProvider getting config for: %s", name)
        return {"url": "https://api.example.com", "timeout": 30}


class SampleTransformProvider(TransformProvider[Any]):
    """A sample transform provider implementation."""

    def __init__(self) -> None:
        """Initialize the provider."""
        logger.info("Initialized SampleTransformProvider")

    def transform(self, data: Any, **_kwargs: Any) -> Any:
        """Transform data.

        Args:
            data: Data to transform
            **_kwargs: Additional parameters (unused)

        Returns:
            Transformed data
        """
        logger.debug("SampleTransformProvider transforming data")
        return data


# Define hook implementations
@hookimpl
def register_adapters(registry: dict[str, type[ProtocolAdapter]]) -> None:
    """Register adapters with the registry.

    Args:
        registry: Adapter registry
    """
    registry["sample_http"] = SampleHttpAdapter


@hookimpl
def register_auth_providers(registry: dict[str, type[AuthProvider]]) -> None:
    """Register authentication providers with the registry.

    Args:
        registry: Auth provider registry
    """
    registry["sample_auth"] = SampleAuthProvider


@hookimpl
def register_schema_providers(registry: dict[str, Any]) -> None:
    """Register schema providers with the registry.

    Args:
        registry: Schema provider registry
    """
    registry["sample_schema"] = SampleSchemaProvider


@hookimpl
def register_config_providers(registry: dict[str, Any]) -> None:
    """Register configuration providers with the registry.

    Args:
        registry: Config provider registry
    """
    registry["sample_config"] = SampleConfigProvider


@hookimpl
def register_data_providers(registry: dict[str, Any]) -> None:
    """Register data providers with the registry.

    Args:
        registry: Data provider registry
    """
    registry["sample_data"] = SampleDataProvider


@hookimpl
def register_transform_providers(registry: dict[str, Any]) -> None:
    """Register transform providers with the registry.

    Args:
        registry: Transform provider registry
    """
    registry["sample_transform"] = SampleTransformProvider


@hookimpl
def register_request_hooks(registry: dict[str, Any]) -> None:
    """Register request hooks with the registry.

    Args:
        registry: Request hook registry
    """
    registry["sample_request"] = SampleRequestHook


@hookimpl
def register_response_hooks(registry: dict[str, Any]) -> None:
    """Register response hooks with the registry.

    Args:
        registry: Response hook registry
    """
    registry["sample_response"] = SampleResponseHook


@hookimpl
def register_error_hooks(registry: dict[str, Any]) -> None:
    """Register error hooks with the registry.

    Args:
        registry: Error hook registry
    """
    registry["sample_error"] = SampleErrorHook


@hookimpl
def register_api_response_hooks(registry: dict[str, Any]) -> None:
    """Register API response hooks with the registry.

    Args:
        registry: API response hook registry
    """
    # No implementation for this example, but showing the hook for completeness


# Example of using the plugin
def main() -> None:
    """Demonstrate using the sample plugin."""
    # Enable plugins
    apix.enable_plugins()

    # Get registered components
    http_adapter_cls = apix.get_adapter("sample_http")
    auth_provider_cls = apix.get_auth_provider("sample_auth")
    schema_provider_cls = apix.get_schema_provider("sample_schema")
    config_provider_cls = apix.get_config_provider("sample_config")
    data_provider_cls = apix.get_data_provider("sample_data")
    transform_provider_cls = apix.get_transform_provider("sample_transform")
    request_hook_cls = apix.get_request_hook("sample_request")
    response_hook_cls = apix.get_response_hook("sample_response")
    error_hook_cls = apix.get_error_hook("sample_error")

    # Print registered components
    print(f"HTTP Adapter: {http_adapter_cls}")
    print(f"Auth Provider: {auth_provider_cls}")
    print(f"Schema Provider: {schema_provider_cls}")
    print(f"Config Provider: {config_provider_cls}")
    print(f"Data Provider: {data_provider_cls}")
    print(f"Transform Provider: {transform_provider_cls}")
    print(f"Request Hook: {request_hook_cls}")
    print(f"Response Hook: {response_hook_cls}")
    print(f"Error Hook: {error_hook_cls}")

    # Create and use components
    if http_adapter_cls:
        adapter = http_adapter_cls("https://api.example.com")
        print(f"Created adapter: {adapter}")

    if auth_provider_cls:
        auth_provider = auth_provider_cls("username", "password")
        print(f"Created auth provider: {auth_provider}")

    # List all registered components by type
    print("\nRegistered Adapters:", apix.list_adapters())
    print("Registered Auth Providers:", apix.list_auth_providers())
    print("Registered Schema Providers:", apix.list_schema_providers())
    print("Registered Config Providers:", apix.list_config_providers())
    print("Registered Data Providers:", apix.list_data_providers())
    print("Registered Transform Providers:", apix.list_transform_providers())
    print("Registered Request Hooks:", apix.list_request_hooks())
    print("Registered Response Hooks:", apix.list_response_hooks())
    print("Registered Error Hooks:", apix.list_error_hooks())


if __name__ == "__main__":
    main()
