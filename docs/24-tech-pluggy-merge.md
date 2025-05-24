# Pluggy Guide for DCApiX

## Introduction

DCApiX uses [pluggy](https://pluggy.readthedocs.io/en/latest/) as its plugin system framework, enabling modular architecture through a powerful plugin and hook mechanism. This guide provides a comprehensive overview of how pluggy is used within DCApiX to create an extensible system where new protocols, authentication methods, and other functionality can be added without modifying the core codebase.

## Core Pluggy Features in DCApiX

### Plugin Architecture

DCApiX implements a robust plugin architecture using pluggy:

- **Hook Specifications**: Formal interfaces for plugins to implement
- **Hook Implementations**: Concrete implementations of the hooks
- **Plugin Discovery**: Automatic discovery of plugins via entry points
- **Plugin Registry**: Central registry of discovered plugins

### Entry Points

DCApiX uses Python entry points for plugin discovery:

- **Package Registration**: Plugins register via `pyproject.toml` or `setup.py`
- **Namespace Isolation**: Plugins use the `dc_api_x.plugins` namespace
- **Lazy Loading**: Plugins are loaded on demand to minimize startup overhead
- **Version Compatibility**: Plugins can specify compatibility with core versions

### Hook System

DCApiX defines a comprehensive set of hooks for extension:

- **Adapter Hooks**: Add new protocol adapters (HTTP, databases, etc.)
- **Auth Provider Hooks**: Add new authentication mechanisms
- **Transform Hooks**: Add data transformation capabilities
- **Observer Hooks**: Hook into the request/response lifecycle
- **Provider Hooks**: Register new service providers

## Basic Usage in DCApiX

### Discovering Plugins

DCApiX discovers and loads plugins with:

```python
import dc_api_x as apix

# Discover and load all plugins
apix.enable_plugins()

# Get a specific adapter from a plugin
oracle_adapter = apix.get_adapter("oracle_db")

# Check available adapters
adapters = apix.list_adapters()
print(f"Available adapters: {', '.join(adapters)}")
```

### Creating a Simple Plugin

Here's how to create a basic plugin for DCApiX:

```python
# my_plugin/__init__.py
"""Example DCApiX plugin."""

def register_adapters(registry):
    """Register custom adapters with DCApiX."""
    from .custom_adapter import CustomAdapter
    registry["custom_protocol"] = CustomAdapter

# my_plugin/custom_adapter.py
from dc_api_x.ext.adapters import ProtocolAdapter

class CustomAdapter(ProtocolAdapter):
    """A custom protocol adapter."""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.client = None  # Would initialize actual client here
    
    def request(self, method, path, **kwargs):
        """Implement the request method required by ProtocolAdapter."""
        # Implementation details
        result = {"success": True, "data": {"sample": "data"}}
        return result
        
    def close(self):
        """Clean up resources."""
        if self.client:
            self.client.close()
```

### Registering a Plugin

In your plugin's `pyproject.toml`:

```toml
[project]
name = "dc-api-x-custom-plugin"
version = "0.1.0"
dependencies = ["dc-api-x>=0.2.0"]

[project.entry-points."dc_api_x.plugins"]
custom_plugin = "my_plugin"
```

## Advanced Features

### Multiple Hook Implementations

A plugin can implement multiple hooks:

```python
# advanced_plugin/__init__.py
"""Advanced DCApiX plugin."""

def register_adapters(registry):
    """Register custom adapters."""
    from .custom_adapter import CustomAdapter
    registry["custom_protocol"] = CustomAdapter

def register_auth_providers(registry):
    """Register custom auth providers."""
    from .custom_auth import CustomAuthProvider
    registry["custom_auth"] = CustomAuthProvider

def register_transforms(registry):
    """Register custom transforms."""
    from .custom_transform import CustomTransformProvider
    registry["custom_transform"] = CustomTransformProvider
```

### Plugin Lifecycle Management

Manage plugin lifecycle with initialization and cleanup:

```python
# lifecycle_plugin/__init__.py
"""Plugin with lifecycle management."""
import atexit

# Track resources that need cleanup
_resources = []

def register_adapters(registry):
    """Register adapters with lifecycle management."""
    from .managed_adapter import ManagedAdapter
    
    # Initialize adapter factory
    adapter_factory = ManagedAdapter.create_factory()
    _resources.append(adapter_factory)
    
    # Register the adapter
    registry["managed_protocol"] = adapter_factory.create_adapter
    
    # Register cleanup on exit
    atexit.register(cleanup_resources)

def cleanup_resources():
    """Clean up all resources when Python exits."""
    for resource in _resources:
        resource.cleanup()
    _resources.clear()
```

### Conditional Plugin Registration

Register plugins conditionally based on environment:

```python
# conditional_plugin/__init__.py
"""Plugin that registers conditionally."""
import os

def register_adapters(registry):
    """Register adapters only if conditions are met."""
    # Check for feature flag
    if os.environ.get("ENABLE_EXPERIMENTAL_ADAPTER") != "1":
        return  # Skip registration if feature flag is not set
    
    # Try to import optional dependency
    try:
        import some_optional_package
    except ImportError:
        # Log warning but don't fail
        import logging
        logging.warning("Optional dependency 'some_optional_package' not found, "
                      "experimental adapter not registered")
        return
    
    # Import and register the adapter if dependencies are available
    from .experimental_adapter import ExperimentalAdapter
    registry["experimental"] = ExperimentalAdapter
```

### Version Compatibility

Ensure plugin compatibility with core version:

```python
# version_plugin/__init__.py
"""Version-aware plugin."""
import importlib.metadata
from packaging import version

def register_adapters(registry):
    """Register adapters with version check."""
    # Check dc-api-x version
    core_version = version.parse(importlib.metadata.version("dc-api-x"))
    required_version = version.parse("0.2.0")
    
    if core_version < required_version:
        import warnings
        warnings.warn(
            f"Plugin requires dc-api-x>=0.2.0, but found {core_version}. "
            "Some features may not work correctly."
        )
    
    # Register the adapter
    from .compatible_adapter import CompatibleAdapter
    registry["compatible_protocol"] = CompatibleAdapter
```

## Plugin Integration with DCApiX Components

### Integration with ApiClient

Use custom adapters with ApiClient:

```python
from dc_api_x import ApiClient, enable_plugins

# Enable plugins to discover custom adapters
enable_plugins()

# Create client with custom adapter
client = ApiClient(
    url="protocol://example.com",
    adapter="custom_protocol",  # Use registered adapter by name
    adapter_options={"key": "value"}  # Pass options to adapter
)

# Use the client with custom protocol
response = client.get("resource")
```

### Integration with Pydantic

Use Pydantic for configuration:

```python
from pydantic import BaseModel, Field
from dc_api_x.ext.adapters import ProtocolAdapter

class CustomAdapterConfig(BaseModel):
    """Configuration for CustomAdapter."""
    host: str = Field(..., description="Host address")
    port: int = Field(8080, description="Port number")
    timeout: int = Field(30, description="Connection timeout in seconds")
    use_ssl: bool = Field(True, description="Whether to use SSL")

class ConfigurableAdapter(ProtocolAdapter):
    """Adapter that uses Pydantic for configuration."""
    
    def __init__(self, **kwargs):
        # Validate configuration with Pydantic
        self.config = CustomAdapterConfig(**kwargs)
        
        # Use validated configuration
        connection_string = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.config.port}"
        self.client = self._create_client(connection_string, self.config.timeout)
```

### Integration with Logging

Integrate with Logfire for structured logging:

```python
import logfire
from dc_api_x.ext.adapters import ProtocolAdapter

class LoggingAdapter(ProtocolAdapter):
    """Adapter with comprehensive logging."""
    
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", self.__class__.__name__)
        logfire.info(f"Initializing {self.name} adapter", **kwargs)
        # Initialize actual adapter
        
    def request(self, method, path, **kwargs):
        """Log requests and responses."""
        with logfire.context(adapter=self.name, method=method, path=path):
            logfire.debug("Making request")
            
            try:
                response = self._make_actual_request(method, path, **kwargs)
                logfire.info("Request successful", status=response.get("status"))
                return response
            except Exception as e:
                logfire.exception("Request failed", error_type=type(e).__name__)
                raise
```

## Plugin Development Best Practices

### 1. Lazy Loading

Delay importing heavy dependencies until needed:

```python
# Good - lazy import
def register_adapters(registry):
    # Only import when needed, reducing startup time
    from .heavy_adapter import HeavyAdapter
    registry["heavy"] = HeavyAdapter

# Avoid - eager import
from .heavy_adapter import HeavyAdapter  # Imported at module load time

def register_adapters(registry):
    registry["heavy"] = HeavyAdapter
```

### 2. Error Handling

Implement robust error handling in plugins:

```python
def register_adapters(registry):
    try:
        from .adapter import CustomAdapter
        registry["custom"] = CustomAdapter
    except ImportError as e:
        import logging
        logging.warning(f"Could not register custom adapter: {e}")
        # Continue without failing - core functionality remains intact
```

### 3. Documentation

Document your plugin thoroughly:

```python
# my_plugin/__init__.py
"""
DCApiX plugin for XYZ protocol.

This plugin provides:
- XYZ protocol adapter
- Authentication for XYZ services
- Data transformation for XYZ formats

Requirements:
- dc-api-x>=0.2.0
- xyz-client>=1.5.0

Environment variables:
- XYZ_API_KEY: Required API key for XYZ services
- XYZ_TIMEOUT: Optional timeout in seconds (default: 30)
"""

def register_adapters(registry):
    """
    Register the XYZ protocol adapter.
    
    The adapter supports the following features:
    - Automatic authentication with API key
    - Connection pooling
    - Rate limiting with backoff
    """
    from .xyz_adapter import XyzAdapter
    registry["xyz"] = XyzAdapter
```

### 4. Plugin Configuration

Use common configuration patterns:

```python
# Environment variables
import os

# Config files
import json
from pathlib import Path

def get_plugin_config():
    """Get plugin configuration from multiple sources."""
    # Default config
    config = {
        "timeout": 30,
        "max_connections": 10,
        "retry": True
    }
    
    # Override from config file
    config_file = Path.home() / ".config" / "dcapix" / "plugins" / "custom.json"
    if config_file.exists():
        with open(config_file) as f:
            config.update(json.load(f))
    
    # Override from environment variables
    if "CUSTOM_TIMEOUT" in os.environ:
        config["timeout"] = int(os.environ["CUSTOM_TIMEOUT"])
    
    return config
```

### 5. Testing Plugins

Create testable plugins:

```python
# testing_plugin/adapter.py
class TestableAdapter:
    """Adapter designed for testability."""
    
    def __init__(self, client=None, **kwargs):
        # Accept client injection for testing
        self.client = client or self._create_real_client(**kwargs)
    
    def _create_real_client(self, **kwargs):
        # Create actual client - can be mocked in tests
        return RealClient(**kwargs)
    
    def request(self, method, path, **kwargs):
        # Delegate to client, allowing for easy mocking
        return self.client.make_request(method, path, **kwargs)

# tests/test_plugin.py
def test_plugin_adapter():
    """Test the plugin adapter with a mock client."""
    # Create mock client
    mock_client = MagicMock()
    mock_client.make_request.return_value = {"success": True}
    
    # Create adapter with mock client
    adapter = TestableAdapter(client=mock_client)
    
    # Test the adapter
    result = adapter.request("GET", "/test")
    
    # Verify results
    assert result["success"] is True
    mock_client.make_request.assert_called_once_with("GET", "/test")
```

## Plugin Registry Reference

DCApiX provides multiple registries for different plugin types:

| Registry | Purpose | Hook Function |
|----------|---------|--------------|
| Adapters | Protocol adapters | `register_adapters(registry)` |
| Auth Providers | Authentication | `register_auth_providers(registry)` |
| Hooks | Request/response pipeline | `register_hooks(registry)` |
| Schema Providers | Schema management | `register_schema_providers(registry)` |
| Transform Providers | Data transformation | `register_transform_providers(registry)` |
| Pagination Handlers | Response pagination | `register_pagination_handlers(registry)` |
| Config Providers | Configuration management | `register_config_providers(registry)` |

## Official Plugin Examples

DCApiX provides several official plugins that serve as reference implementations:

| Plugin | Purpose | Features |
|--------|---------|----------|
| dc-api-x-oracle-db | Oracle Database | Connection pooling, PL/SQL support |
| dc-api-x-ldap | LDAP Directory | LDAP v3 support, search optimization |
| dc-api-x-redis | Redis Cache | Caching, pub/sub |
| dc-api-x-keycloak | Keycloak IAM | OAuth2, token management |

Each plugin follows the best practices outlined in this guide and can be used as a template for custom plugins.

## Future Plugin Roadmap

DCApiX is planning to expand its ecosystem with several high-value plugins to support additional protocols and integrations. Below is our roadmap for upcoming plugin development:

### HTTP and API Enhancements

| Plugin | Description | Key Features | Expected Release |
|--------|-------------|--------------|------------------|
| **dc-api-x-httpx** | Enhanced HTTP client using [HTTPX](https://www.python-httpx.org/) | HTTP/2 support, async capabilities, connection pooling, streaming responses | Q3 2025 |
| **dc-api-x-osquery** | Integration with [OSQuery](https://osquery.readthedocs.io/en/stable/) | SQL-based OS instrumentation, real-time monitoring | Q4 2025 |

### Database and Directory Services

| Plugin | Description | Key Features | Expected Release |
|--------|-------------|--------------|------------------|
| **dc-api-x-sqlalchemy** | Enhanced SQLAlchemy integration using [SQLAlchemy Plugin System](https://docs.sqlalchemy.org/en/20/core/plugins.html) | Custom types, dialect extensions, connection instrumentation | Q2 2025 |
| **dc-api-x-ldaptor** | Alternative LDAP client using [Ldaptor](https://ldaptor.readthedocs.io/en/latest/) | Async LDAP operations, schema awareness | Q3 2025 |
| **dc-api-x-python-ldap** | Advanced LDAP functionality with [python-ldap](https://www.python-ldap.org/) | SASL support, LDIF handling, advanced server controls | Q3 2025 |
| **dc-api-x-ldap3** | Comprehensive LDAP operations with [ldap3](https://ldap3.readthedocs.io/en/latest/) | Connection pooling, NTLM authentication, extended operations | Q2 2025 |

### Data Pipeline and ETL

| Plugin | Description | Key Features | Expected Release |
|--------|-------------|--------------|------------------|
| **dc-api-x-singer** | Implementation of the [Singer](https://github.com/singer-io/getting-started) specification | Standardized ETL taps and targets, data stream handling | Q4 2025 |
| **dc-api-x-meltano** | Integration with [Meltano](https://docs.meltano.com/) ELT framework | Pipeline orchestration, transformation management | Q4 2025 |
| **dc-api-x-sdk-meltano** | SDK for building Meltano-compatible plugins using [Meltano SDK](https://sdk.meltano.com/en/latest/) | Custom extractor/loader development | Q1 2026 |

### Infrastructure and Querying Tools

| Plugin | Description | Key Features | Expected Release |
|--------|-------------|--------------|------------------|
| **dc-api-x-steampipe** | Integration with [Steampipe](https://steampipe.io/docs) | SQL querying across cloud services | Q2 2026 |
| **dc-api-x-powerpipe** | Dashboards and visualizations with [Powerpipe](https://powerpipe.io/docs) | Metrics collection, visualization | Q2 2026 |
| **dc-api-x-flowpipe** | Workflow automation using [Flowpipe](https://flowpipe.io/) | Infrastructure automation, CI/CD integration | Q3 2026 |
| **dc-api-x-tailpipe** | Data transformation with [Tailpipe](https://tailpipe.io/) | ETL pipeline management | Q3 2026 |

Each plugin will follow DCApiX's architecture principles and best practices, with comprehensive documentation, test coverage, and example implementations. The development roadmap is subject to change based on community feedback and evolving technology landscapes.

## See Also

- [Pluggy Documentation](https://pluggy.readthedocs.io/en/latest/)
- [Python Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [Plugin System Guide](05-plugin-system.md)
- [Architecture](03-architecture.md)
- [Singer Specification](https://github.com/singer-io/getting-started) (Inspiration for DCApiX plugin architecture)
- [SQLAlchemy Plugin System](https://docs.sqlalchemy.org/en/20/core/plugins.html)
