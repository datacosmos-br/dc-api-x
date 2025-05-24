# Plugin System Architecture

> *"The power of a system lies in its extensibility."*
> This guide explains how DCApiX's plugin architecture enables seamless extension
> without modifying the core codebase.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [12 - Development: Code Quality](12-development-code-quality.md) | **13 - Development: Plugin System** | [20 - Tech: Overview](20-tech-overview.md) |

---

## 1. Introduction

DCApiX treats **every external connector**—Oracle DB, WMS, Redis, Kafka—as a *plugin* discovered at runtime via Python entry-points. This design enables developers to add new functionality, support additional protocols, or integrate with different systems while maintaining compatibility with the existing ecosystem. The core stays dependency-free while teams add features on their own cadence.

---

## 2. Plugin System Architecture

### 2.1 Core Components

The plugin system consists of several key components:

* **Hookspecs**: Define extension points where plugins can integrate
* **Hookimpl**: Plugin implementations that connect to extension points
* **Plugin Registry**: Central registry that manages plugin discovery and registration
* **Plugin Manager**: Coordinates plugin loading, validation, and execution

### 2.2 Hook Specification

A plugin is a plain Python module that **implements one or more hooks** defined in `dc_api_x.hookspecs`. Each hook receives a mutable registry that the plugin mutates.

```python
# src/dc_api_x/hookspecs/hookspecs.py
import pluggy
from typing import Type

hookspec = pluggy.HookspecMarker("dc_api_x")

@hookspec
def register_adapters(registry: dict[str, Type["ProtocolAdapter"]]) -> None:
    """Add custom adapters keyed by a user-friendly name."""

@hookspec
def register_auth_providers(registry: dict[str, Type["AuthProvider"]]) -> None:
    """Expose new authentication mechanisms (e.g. mTLS, SAML token)."""

@hookspec
def register_hooks(registry: list[type["RequestHook"]]) -> None:
    """Inject global request/response hooks (tracing, metrics, …)."""
```

More hooks can be added without breaking existing plugins because unimplemented hooks are simply ignored.

### 2.3 Registry Organization

The plugin system uses multiple registries organized by component type:

* **Adapter Registry**: Protocol adapters for different systems
* **Auth Provider Registry**: Authentication mechanisms
* **Schema Provider Registry**: Schema handling and validation
* **Config Provider Registry**: Configuration management
* **Data Provider Registry**: Data handling and transformation
* **Hook Registry**: Request/response lifecycle hooks

Each registry is a dictionary mapping names to component classes, allowing for easy lookup and extension.

---

## 3. Creating a Plugin

### 3.1 Plugin Structure

A typical DCApiX plugin follows this structure:

```
my-plugin/
├── my_plugin/
│   ├── __init__.py      # Plugin registration
│   └── adapter.py       # Implementation
└── pyproject.toml       # Package metadata and entry points
```

### 3.2 Implementation Example (Oracle DB)

Let's create a plugin for Oracle DB access:

#### `oracle_adapter.py`

```python
from dc_api_x.ext.adapters import DatabaseAdapter
import oracledb

class OracleDatabaseAdapter(DatabaseAdapter):
    """Thin-mode Oracle DB adapter with automatic reconnect."""

    def __init__(self, dsn: str, user: str, password: str, **kw):
        self.pool = oracledb.create_pool(user=user, password=password, dsn=dsn, **kw)

    def query(self, sql: str, params: dict | None = None):
        with self.pool.acquire() as conn, conn.cursor() as cur:
            cur.execute(sql, params or {})
            return cur.fetchall()

    def query_value(self, sql: str, params: dict | None = None):
        return self.query(sql, params)[0][0]
```

#### `__init__.py`

```python
from dc_api_x import hookspecs

def register_adapters(reg):
    from .oracle_adapter import OracleDatabaseAdapter
    reg["oracle_db"] = OracleDatabaseAdapter
```

> **Tip:** Import heavy dependencies (`oracledb`) *inside* the function to avoid
> import cost when the plugin is present but not used.

#### `pyproject.toml`

```toml
[project]
name = "dc-api-x-oracle-db"
version = "0.1.0"
dependencies = ["dc-api-x", "python-oracledb>=2.0"]

[project.entry-points."dc_api_x.plugins"]
oracle_db = "dc_api_x_oracle_db"
```

### 3.3 Using the Plugin

```python
import dc_api_x as apix
apix.enable_plugins()                  # discovers oracle_db

ora = apix.get_adapter("oracle_db")    # lookup by registry key
print(ora.query_value("SELECT sysdate FROM dual"))
```

*If the plugin is missing, `get_adapter("oracle_db")` raises `AdapterNotFound`.*

---

## 4. Advanced Plugin Features

### 4.1 Version Compatibility

Plugins should declare their compatibility with the core framework:

```toml
[project]
dependencies = ["dc-api-x>=0.2.0"]
```

The core follows SemVer; minor releases never break the public extension interfaces.

### 4.2 Event Hooks

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
```

### 4.3 CLI Extensions

Plugins can extend the DCApiX command-line interface:

```python
from dc_api_x.hookspecs import hookimpl
import typer

def register_cli_commands(app):
    """Add custom commands to the CLI."""
    my_app = typer.Typer(help="My plugin commands")

    @my_app.command("hello")
    def hello_command(name: str):
        """Say hello from the plugin."""
        print(f"Hello {name} from my plugin!")

    app.add_typer(my_app, name="myplugin")

@hookimpl
def register_cli():
    """Register CLI commands."""
    return register_cli_commands
```

---

## 5. Testing Plugins

### 5.1 Basic Test Setup

```bash
pip install -e ".[dev]"          # installs dc-api-x + test deps
pytest -q                        # run your plugin's tests
```

### 5.2 Using Mock Adapters

Use the `MockAdapter` helper to test without actual network/database calls:

```python
from dc_api_x.testing import MockAdapter

class DummyAdapter(MockAdapter):
    RESPONSES = {
        ("GET", "/ping"): {"pong": True},
    }

def test_plugin_registration():
    from dc_api_x import ApiClient
    client = ApiClient(adapter=DummyAdapter())
    assert client.get("ping").data["pong"] is True
```

### 5.3 Test Infrastructure

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
        result = self.plugin.some_function()
        self.assertEqual(result, expected_value)
```

---

## 6. Advanced Hook Types

| Hook | Typical Use Case |
|------|------------------|
| `register_adapters` | Protocol implementations (HTTP, Oracle, LDAP) |
| `register_auth_providers` | Authentication mechanisms (OAuth, JWT, API Keys) |
| `register_hooks` | Global middleware (metrics, tracing, logging) |
| `register_schema_providers` | Custom schema fetchers for vendor-specific APIs |
| `register_transform_providers` | Domain-specific ETL transformations |
| `register_cli` | CLI command extensions |

---

## 7. Plugin Discovery and Loading

### 7.1 Discovery Mechanisms

DCApiX discovers plugins through several mechanisms:

* **Entry Points**: Plugins declared in Python package entry points
* **Explicit Registration**: Plugins registered programmatically
* **Directory Scanning**: Plugins discovered in specific directories

### 7.2 Loading Process

The plugin loading process follows these steps:

1. **Discovery**: Find available plugins through entry points and directories
2. **Registration**: Register plugins and hook implementations
3. **Validation**: Validate plugin interfaces and requirements
4. **Initialization**: Initialize plugins in dependency order
5. **Hook Execution**: Invoke relevant hooks as needed

---

## 8. Best Practices

### 8.1 Plugin Development Checklist

1. **Lazy imports** for big native libs (oracledb, cx_Oracle)
2. Ship **unit tests**; CI matrix: *Linux* + *Windows* (or skip if not relevant)
3. Document required env vars (`ORACLE_DSN`, `WMS_URL`, …) in the README
4. Use **semver** and update `CHANGELOG.md` on every release
5. Keep adapter names lowercase snake_case to avoid collisions

### 8.2 Performance Considerations

* Use lazy loading to minimize startup impact
* Import heavy dependencies inside functions
* Initialize connections on demand, not at import time
* Add proper connection pooling for database adapters
* Use asyncio for I/O-bound operations where appropriate

### 8.3 Security Best Practices

* Never hard-code credentials in plugins
* Validate all inputs from external systems
* Use `SecretStr` for password and token fields
* Document security implications in plugin documentation
* Add proper error handling for failed operations

---

## 9. Future Plugin Roadmap

DCApiX is planning an extensive expansion of its plugin ecosystem over the next several years (2025-2026). These plugins will significantly enhance DCApiX's capabilities across multiple domains:

### 9.1 HTTP and API Enhancements

* **HTTPX Plugin**: Modern HTTP client with HTTP/2 and async capabilities
* **OSQuery Integration**: System-level monitoring via SQL interface

### 9.2 Database and Directory Services

* **Enhanced SQLAlchemy Support**: Custom types, dialects, and connection instrumentation
* **Multiple LDAP Client Options**: Compatible implementations for ldap3, python-ldap, and Ldaptor

### 9.3 Data Pipeline Solutions

* **Singer Specification Implementation**: Standardized ETL taps and targets
* **Meltano Integration**: ELT framework with pipeline orchestration
* **Custom ETL SDK**: Tools for building custom extractors and loaders

### 9.4 Infrastructure Management

* **Integration with Steampipe/Powerpipe**: SQL querying and visualization for cloud services
* **Flowpipe/Tailpipe Support**: Workflow automation and data transformation capabilities

---

## Related Documentation

* [10 - Development: Workflow](10-development-workflow.md) - Development workflow guide
* [11 - Development: Contributing](11-development-contributing.md) - Contribution guidelines
* [12 - Development: Code Quality](12-development-code-quality.md) - Code quality standards
* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [27 - Tech: Plugin](27-tech-plugin.md) - Plugin system technical details
