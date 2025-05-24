# Plugin System Architecture

> *"The power of a system lies in its extensibility."*
> This guide explains how DCApiX's plugin architecture enables seamless extension without modifying the core codebase,
> forming the foundation of the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [26 - Tech: CLI](26-tech-cli.md) | **27 - Tech: Plugin** | [30 - CLI Reference](30-cli-reference.md) |

---

## 1. Introduction

DCApiX is built on a flexible plugin architecture that allows for extension without modifying the core codebase. This
design enables developers to add new functionality, support additional protocols, or integrate with different systems
while maintaining compatibility with the existing ecosystem.

---

## 2. Plugin System Overview

### 2.1 Core Components

The plugin system consists of several key components:

* **Hookspecs**: Define extension points where plugins can integrate
* **Hookimpl**: Plugin implementations that connect to extension points
* **Plugin Registry**: Central registry that manages plugin discovery and registration
* **Plugin Manager**: Coordinates plugin loading, validation, and execution

### 2.2 Extension Points

DCApiX provides several types of extension points:

* **Protocol Adapters**: Extend to support new API protocols
* **Authentication Providers**: Add authentication methods
* **Data Transformers**: Add data transformation capabilities
* **Storage Backends**: Support different storage systems
* **CLI Extensions**: Add new commands to the CLI
* **Event Hooks**: React to system events

### 2.3 Plugin Structure

A typical DCApiX plugin follows this structure:

```
my_plugin/
├── __init__.py             # Plugin registration
├── hookimpl.py             # Hook implementations
├── adapters/               # Protocol adapters
├── auth/                   # Authentication providers
├── transforms/             # Data transformers
├── storage/                # Storage backends
├── cli/                    # CLI extensions
└── hooks/                  # Event hooks
```

---

## 3. Creating a Plugin

### 3.1 Basic Plugin

Creating a basic plugin requires implementing the plugin hook:

```python
from dc_api_x.hookspecs import hookimpl

# Mark as a DCApiX plugin
@hookimpl
def register_plugin():
    """Register the plugin with DCApiX."""
    return {
        "name": "my-plugin",
        "version": "0.1.0",
        "description": "My custom DCApiX plugin",
    }
```

### 3.2 Protocol Adapter

Adding a new protocol adapter:

```python
from dc_api_x.hookspecs import hookimpl
from dc_api_x.ext.adapters import ProtocolAdapter

class MyProtocolAdapter(ProtocolAdapter):
    """Custom protocol adapter for MyProtocol."""

    def __init__(self, config):
        self.config = config

    def connect(self):
        """Establish connection to the service."""
        # Implementation

    def request(self, method, path, **kwargs):
        """Make a request to the service."""
        # Implementation

    def close(self):
        """Close the connection."""
        # Implementation

@hookimpl
def register_protocol_adapter():
    """Register the protocol adapter."""
    return {
        "name": "myprotocol",
        "adapter": MyProtocolAdapter,
        "schemes": ["myp", "myprotocol"],
    }
```

### 3.3 Authentication Provider

Adding a new authentication method:

```python
from dc_api_x.hookspecs import hookimpl
from dc_api_x.ext.auth import AuthProvider

class MyAuthProvider(AuthProvider):
    """Custom authentication provider."""

    def authenticate(self, request):
        """Add authentication to the request."""
        # Implementation
        return request

    def refresh(self):
        """Refresh authentication credentials."""
        # Implementation

@hookimpl
def register_auth_provider():
    """Register the authentication provider."""
    return {
        "name": "myauth",
        "provider": MyAuthProvider,
    }
```

### 3.4 CLI Extension

Adding new CLI commands:

```python
from dc_api_x.hookspecs import hookimpl
import doctyper

def register_cli_commands(app):
    """Add custom commands to the CLI."""
    my_app = doctyper.Typer(help="My plugin commands")

    @my_app.command("hello")
    def hello_command(name: str):
        """Say hello from the plugin.

        Args:
            name: The name to greet
        """
        print(f"Hello {name} from my plugin!")

    app.add_typer(my_app, name="myplugin")

@hookimpl
def register_cli():
    """Register CLI commands."""
    return register_cli_commands
```

---

## 4. Advanced Plugin Features

### 4.1 Event Hooks

Plugins can register handlers for system events:

```python
from dc_api_x.hookspecs import hookimpl

@hookimpl
def on_startup(app):
    """Execute when the application starts."""
    print("Plugin starting up!")

@hookimpl
def on_shutdown(app):
    """Execute when the application shuts down."""
    print("Plugin shutting down!")

@hookimpl
def before_request(request):
    """Execute before each API request."""
    print(f"Making request to {request.url}")
    return request

@hookimpl
def after_response(response):
    """Execute after each API response."""
    print(f"Received response with status {response.status_code}")
    return response
```

### 4.2 Plugin Configuration

Plugins can define their own configuration schema:

```python
from pydantic import BaseModel, Field
from dc_api_x.hookspecs import hookimpl

class MyPluginConfig(BaseModel):
    """Configuration schema for my plugin."""
    enable_feature: bool = Field(
        default=False,
        description="Enable the special feature"
    )
    timeout: int = Field(
        default=30,
        description="Timeout in seconds",
        ge=1,
        le=300
    )

@hookimpl
def register_config_schema():
    """Register configuration schema."""
    return {
        "name": "my-plugin",
        "schema": MyPluginConfig,
    }
```

### 4.3 Data Transformers

Plugins can add data transformation capabilities:

```python
from dc_api_x.hookspecs import hookimpl
from dc_api_x.ext.transforms import DataTransformer

class MyTransformer(DataTransformer):
    """Custom data transformer."""

    def transform(self, data, **options):
        """Transform the data."""
        # Implementation
        return transformed_data

@hookimpl
def register_transformer():
    """Register the data transformer."""
    return {
        "name": "mytransform",
        "transformer": MyTransformer,
    }
```

---

## 5. Plugin Discovery and Loading

### 5.1 Discovery Mechanisms

DCApiX discovers plugins through several mechanisms:

* **Entry Points**: Plugins declared in Python package entry points
* **Explicit Registration**: Plugins registered programmatically
* **Directory Scanning**: Plugins discovered in specific directories

### 5.2 Entry Point Registration

The most common way to register a plugin is via entry points in `pyproject.toml`:

```toml
[project.entry-points."dc_api_x.plugins"]
my-plugin = "my_plugin:plugin"
```

Where `my_plugin/plugin.py` contains the hook implementations.

### 5.3 Explicit Registration

Plugins can be registered programmatically:

```python
from dc_api_x import plugin_manager
import my_plugin

# Register a plugin module
plugin_manager.register_plugin(my_plugin)

# Register multiple plugins
plugin_manager.register_plugins([plugin1, plugin2, plugin3])
```

### 5.4 Plugin Loading Process

DCApiX loads plugins in this sequence:

1. **Discovery**: Find available plugins through entry points and directories
2. **Registration**: Register plugins and hook implementations
3. **Validation**: Validate plugin interfaces and requirements
4. **Initialization**: Initialize plugins in dependency order
5. **Hook Execution**: Invoke relevant hooks as needed

---

## 6. Plugin Communication

### 6.1 Direct API Access

Plugins can access the DCApiX API directly:

```python
from dc_api_x import api

def my_plugin_function():
    """Do something with the API."""
    client = api.get_client("my-service")
    response = client.get("/resource")
    return response.data
```

### 6.2 Inter-Plugin Communication

Plugins can communicate with each other through the plugin manager:

```python
from dc_api_x import plugin_manager

def call_another_plugin():
    """Call a function from another plugin."""
    # Get a reference to another plugin
    other_plugin = plugin_manager.get_plugin("other-plugin")

    # Call its function
    result = other_plugin.some_function()
    return result
```

### 6.3 Event-Based Communication

Plugins can communicate indirectly through events:

```python
from dc_api_x.events import EventEmitter
from dc_api_x.hookspecs import hookimpl

# Create an event emitter
emitter = EventEmitter()

# Emit an event from one plugin
def emit_event():
    """Emit a custom event."""
    emitter.emit("my-plugin:event", {"data": "value"})

# Listen for events in another plugin
@hookimpl
def register_event_handlers():
    """Register event handlers."""
    def handle_event(event_data):
        print(f"Received event with data: {event_data}")

    emitter.on("my-plugin:event", handle_event)
```

---

## 7. Plugin Development Best Practices

1. **Minimal Dependencies**: Keep plugin dependencies minimal and explicit

2. **Version Compatibility**: Clearly specify which DCApiX versions are supported

3. **Documentation**: Document plugin functionality, configuration, and usage

4. **Error Handling**: Handle errors gracefully and provide clear error messages

5. **Testing**: Write comprehensive tests for all plugin functionality

6. **Performance**: Be mindful of performance impact, especially for hooks that run frequently

7. **Security**: Follow security best practices, especially for auth providers

8. **Configuration Validation**: Use Pydantic models to validate plugin configuration

9. **Consistent Naming**: Follow DCApiX naming conventions for consistency

10. **Backward Compatibility**: Maintain backward compatibility when updating plugins

---

## 8. Plugin Testing

### 8.1 Test Infrastructure

DCApiX provides utilities for testing plugins:

```python
from dc_api_x.testing import PluginTestCase

class TestMyPlugin(PluginTestCase):
    """Test cases for my plugin."""

    def setUp(self):
        """Set up the test environment."""
        # Load the plugin for testing
        self.load_plugin("my-plugin")

    def test_plugin_functionality(self):
        """Test plugin functionality."""
        # Test implementation
        result = self.plugin.some_function()
        self.assertEqual(result, expected_value)
```

### 8.2 Mock Adapters

For testing protocol adapters without making real requests:

```python
from dc_api_x.testing import MockAdapter

# Create a mock adapter
mock = MockAdapter()

# Configure mock responses
mock.add_response(
    method="GET",
    path="/users",
    status=200,
    body={"users": [{"id": 1, "name": "Test User"}]}
)

# Use the mock in tests
client = api.get_client("my-service", adapter=mock)
response = client.get("/users")
assert response.status_code == 200
assert len(response.data["users"]) == 1
```

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries reference
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools
* [23 - Tech: Testing](23-tech-testing.md) - Testing guide
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Structured logging with Logfire
* [26 - Tech: CLI](26-tech-cli.md) - CLI implementation
* [30 - CLI Reference](30-cli-reference.md) - CLI reference
