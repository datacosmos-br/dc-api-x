# Plugin System

dc-api-x treats **every external connector**—Oracle DB, WMS, Redis, Kafka—as a
*plugin* discovered at runtime via Python entry-points.  
The core stays dependency-free while teams add features on their own cadence.

---

## 1 ▸ Hook Specification

A plugin is a plain Python module that **implements one or more hooks** defined
in `dc_api_x.hookspecs`.  
Each hook receives a mutable registry that the plugin mutates.

```python
# src/dc_api_x/hookspecs/hookspecs.py
import pluggy
from typing import Type, Dict
from dc_api_x.ext.adapters import ProtocolAdapter
from dc_api_x.ext.auth import AuthProvider

hookspec = pluggy.HookspecMarker("dc_api_x")

@hookspec
def register_adapters(registry: Dict[str, Type[ProtocolAdapter]]) -> None:
    """Add custom adapters keyed by a user-friendly name."""

@hookspec
def register_auth_providers(registry: Dict[str, Type[AuthProvider]]) -> None:
    """Expose new authentication mechanisms (e.g. mTLS, SAML token)."""

@hookspec
def register_hooks(registry: list[type["RequestHook"]]) -> None:
    """Inject global request/response hooks (tracing, metrics, …)."""
```

More hooks can be added without breaking existing plugins because unimplemented
hooks are simply ignored.

---

## 2 ▸ Writing a Plugin – Oracle DB Example

Directory layout:

```bash
dc-api-x-oracle-db/
├── dc_api_x_oracle_db/
│   ├── __init__.py
│   └── oracle_adapter.py
└── pyproject.toml
```

### 2.1  Implementation (`oracle_adapter.py`)

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

### 2.2  Plugin entry (`__init__.py`)

```python
from dc_api_x import hookspecs

def register_adapters(reg):
    from .oracle_adapter import OracleDatabaseAdapter
    reg["oracle_db"] = OracleDatabaseAdapter
```

> **Tip:** import heavy dependencies (`oracledb`) *inside* the function to avoid
> import cost when the plugin is present but not used.

### 2.3  `pyproject.toml`

```toml
[project]
name = "dc-api-x-oracle-db"
version = "0.1.0"
dependencies = ["dc-api-x", "python-oracledb>=2.0"]

[project.entry-points."dc_api_x.plugins"]
oracle_db = "dc_api_x_oracle_db"
```

Publish this wheel to PyPI (or your internal repository).

---

## 3 ▸ Using the Plugin

```python
import dc_api_x as apix
apix.enable_plugins()                  # discovers oracle_db

ora = apix.get_adapter("oracle_db")    # lookup by registry key
print(ora.query_value("SELECT sysdate FROM dual"))
```

*If the extra is missing, `get_adapter("oracle_db")` raises `AdapterNotFound`.*

---

## 4 ▸ Version Compatibility

Plugins should declare their compatibility in `requires-python` and, if needed,
pin a **minimum** dc-api-x version, e.g.:

```toml
[project]
dependencies = ["dc-api-x>=0.2.0"]
```

The core follows SemVer; minor releases never break the public extension
interfaces.

---

## 5 ▸ Testing Your Plugin

```bash
pip install -e .[dev]          # installs dc-api-x + test deps
pytest -q                      # run your plugin's tests
```

Use the `apix.testing.MockAdapter` helper to fake network/db calls:

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

---

## 6 ▸ Advanced Hooks

| Hook                                       | Typical Use Case                                               |
| ------------------------------------------ | -------------------------------------------------------------- |
| `register_hooks`                           | Global Prometheus metrics, OpenTelemetry tracing.              |
| `register_schema_providers`                | Custom OpenAPI fetcher for vendor-specific auth handshake.     |
| `register_transform_providers` *(roadmap)* | Domain-specific ETL transforms (e.g. flatten WMS entity JSON). |

---

## 7 ▸ Best Practices Checklist ✅

1. **Lazy imports** for big native libs (oracledb, cx\_Oracle).
2. Ship **unit tests**; CI matrix: *Linux* + *Windows* (or skip if not relevant).
3. Document required env vars (`ORACLE_DSN`, `WMS_URL`, …) in the README.
4. Use **semver** and update `CHANGELOG.md` on every release.
5. Keep adapter names lowercase snake\_case to avoid collisions.

---

## 8 ▸ Future Plugin Roadmap

DCApiX is planning an extensive expansion of its plugin ecosystem over the next several years (2025-2026). These plugins will significantly enhance DCApiX's capabilities across multiple domains:

### HTTP and API Enhancements

- **HTTPX Plugin**: Modern HTTP client with HTTP/2 and async capabilities
- **OSQuery Integration**: System-level monitoring via SQL interface

### Database and Directory Services

- **Enhanced SQLAlchemy Support**: Custom types, dialects, and connection instrumentation
- **Multiple LDAP Client Options**: Compatible implementations for ldap3, python-ldap, and Ldaptor

### Data Pipeline Solutions

- **Singer Specification Implementation**: Standardized ETL taps and targets
- **Meltano Integration**: ELT framework with pipeline orchestration
- **Custom ETL SDK**: Tools for building custom extractors and loaders

### Infrastructure Management

- **Integration with Steampipe/Powerpipe**: SQL querying and visualization for cloud services
- **Flowpipe/Tailpipe Support**: Workflow automation and data transformation capabilities

For detailed information on each planned plugin, including feature sets, expected release dates, and implementation strategies, see our comprehensive [Pluggy Guide](15-pluggy.md#future-plugin-roadmap).

---

*With less than 100 lines you can turn any proprietary system into a first-class
citizen inside dc-api-x—enjoy hacking!*
--- to reorg and merge into

# Plugin System Implementation Notes

## Overview

This document provides implementation notes for the dc-api-x plugin system, focusing on the components that have been implemented and what was previously missing.

## Implemented Components

### 1. Hook Specifications

The hook specifications system has been fully implemented with the following components:

- **Centralized Specifications**: Created `hookspecs.py` that imports and exports the combined hook specifications from the facade.
- **Facade Pattern**: The `HookSpecs` class in `facade.py` combines multiple specialized hook specification classes:
  - `AdapterHookSpecs` - Adapter-related hooks
  - `HookHookSpecs` - Hook-related hooks
  - `ProviderHookSpecs` - Provider-related hooks

### 2. Plugin Registry

The plugin registry system has been expanded to include:

- **Provider Registries**: Added missing registries for config, data, pagination, transform, and API response providers
- **Registry Getters**: Implemented getter functions for all registry types
- **Registry Listers**: Implemented lister functions for all registry types
- **Hook Discovery**: Enhanced plugin loading system to properly discover and call all hook implementations

### 3. Plugin Manager

The plugin manager has been updated to:

- **Register All Hooks**: Call all hook implementations to register components
- **Track Loading State**: Maintain a consistent loading state to avoid duplicate loading
- **Expose Components**: Provide a clean API for accessing registered components

### 4. Sample Plugin

A sample plugin implementation has been created in `examples/sample_plugin.py` that demonstrates:

- **Hook Implementation**: How to implement hook specifications
- **Component Registration**: How to register adapters, hooks, and providers
- **Plugin Usage**: How to use plugin components in client code

## Missing Components Status

The following components were previously missing and have now been implemented:

| Component | Status | Notes |
|-----------|--------|-------|
| Central Hook Specifications | ✅ Implemented | Created `hookspecs.py` |
| Provider Registries | ✅ Implemented | Added config, data, pagination, transform registries |
| Registry Access Functions | ✅ Implemented | Added getter and lister functions |
| API Response Hook Registry | ✅ Implemented | Added registry and accessor functions |
| Sample Plugin | ✅ Implemented | Created comprehensive example |

## Outstanding Tasks

While the core plugin system is now implemented, the following items may require further attention:

1. **Async Support**: The current implementation does not fully implement async adapters and hooks
2. **Plugin Versioning**: Additional version compatibility checking for plugins
3. **Plugin Unloading**: Mechanism for safely unloading or disabling plugins
4. **Plugin Dependency Handling**: Managing dependencies between plugins
5. **Error Handling**: More sophisticated error handling for plugin loading issues

## Implementation Details

### Hook Specifications Design

The hook specification system follows a hierarchical design:

```asciidoc
HookSpecs (facade.py)
├── AdapterHookSpecs (specs.py)
├── HookHookSpecs (hooks.py)
└── ProviderHookSpecs (providers.py)
```

This allows for separation of concerns while maintaining a unified interface.

### Registry Organization

Registries are organized by component type:

```asciidoc
Plugin Registry
├── Adapter Registry
├── Auth Provider Registry
├── Schema Provider Registry
├── Config Provider Registry
├── Data Provider Registry
├── Pagination Provider Registry
├── Transform Provider Registry
├── Request Hook Registry
├── Response Hook Registry
├── Error Hook Registry
└── API Response Hook Registry
```

Each registry is a dictionary mapping names to component classes.

### Plugin Loading Process

The plugin loading process follows these steps:

1. **Discovery**: Find plugins registered via entry points
2. **Loading**: Load each plugin module and register with plugin manager
3. **Hook Registration**: Call each hook implementation to register components
4. **State Tracking**: Mark plugins as loaded to avoid duplicate loading

## Conclusion

The plugin system is now fully implemented and ready for use. Plugin authors can create and register custom components using the hook specifications, and client code can access registered components through the provided API.

To create a new plugin:

1. Define component classes (adapters, hooks, providers)
2. Implement hook specifications using the `@hookimpl` decorator
3. Register the plugin via entry points in `setup.py` or `pyproject.toml`

For examples, see `examples/sample_plugin.py`. 
