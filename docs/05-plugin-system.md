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
pytest -q                      # run your plugin’s tests
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

*With less than 100 lines you can turn any proprietary system into a first-class
citizen inside dc-api-x—enjoy hacking!*
