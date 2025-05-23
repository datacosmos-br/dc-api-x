# Advanced-Libraries Playbook

> *"Great frameworks hide complexity—great teams still need to master it."*  
> This guide explains **how** and **why** dc-api-x leverages a curated stack of
> third-party libraries, and documents best-practice patterns for contributors
> and plugin authors.

---

## 1 ▸ Quick Reference Matrix

| Layer | Library | Advanced Features we **expect** you to use |
|-------|---------|--------------------------------------------|
| HTTP  | **httpx** | *HTTP/2*, connection pooling, `limits`, streaming, `AsyncClient` |
| DB    | **SQLAlchemy 2** | *Core select*, sync & async engines, `Session.begin()` context-manager, SQL compilation caching |
| Oracle| **python-oracledb** | Thin vs Thick mode, DRCP pooling, `json.dumps()` type handlers |
| LDAP  | **ldap3** | Connection pooling, *DirSync* (AD), RFC 4533 Sync Request, `RESTARTABLE` strategy |
| Models| **pydantic V2.11** | Custom validators, generics, `model_validate` on external payloads, JSON Schema export |
| Retry | **tenacity** | Exponential back-off + jitter, per-adapter policies, circuit-breaker pattern |
| Plugins| **pluggy** | Dynamic discovery, version compat guard via `PluginValidationError` |
| Logging| **structlog** + **rich** | Context vars (`bind`), colorised console, JSON when `LOG_AS_JSON=1` |
| CLI   | **typer** | Auto-completion, rich-help, parameter callbacks |
| Obs.  | **opentelemetry-api / sdk** | Span injection inside hooks (`trace_id` logged) |
| ETL   | **singer** + **meltano** | Tap/target pipelines, stream extraction, transformation (future) |
| System | **osquery** | SQL-based system monitoring, OS instrumentation (future) |
| Infrastructure | **steampipe** | Infrastructure as SQL, cloud service querying (future) |

---

## 2 ▸ HTTP — httpx Patterns

```python
import httpx, tenacity

@tenacity.retry(stop=tenacity.stop_after_attempt(5),
                wait=tenacity.wait_exponential(multiplier=0.5, jitter=0.2))
def fetch_large(url: str, dest: str) -> None:
    with httpx.Client(http2=True, timeout=httpx.Timeout(60.0)) as cli:
        with cli.stream("GET", url) as r, open(dest, "wb") as fh:
            for chunk in r.iter_bytes():
                fh.write(chunk)
```

*Always* reuse a client inside adapters; never create one per request.

---

## 3 ▸ SQLAlchemy 2 Cookbook

* **Core-first** → prefer `select(User)` over ORM-heavy `.query`.
* Use **typed mappings** (`@dataclass` + `registry.mapped`) for clear IDE hints.
* Batch writes under `engine.begin()` instead of scattered `conn.execute()`.

```python
from sqlalchemy import select
with engine.connect() as conn:
    for row in conn.scalars(select(User).where(User.active.is_(True))):
        ...
```

Async? Switch to `from sqlalchemy.ext.asyncio import create_async_engine`.

---

## 4 ▸ Oracle Specifics (python-oracledb)

| Topic        | Thin             | Thick                |
| ------------ | ---------------- | -------------------- |
| Footprint    | pure Python      | needs Instant Client |
| DRCP pooling | ❌                | ✅                    |
| JSON columns | Built-in support | Built-in support     |

Set `oracledb.defaults.fetch_lobs = False` unless you **really** need LOBs.

---

## 5 ▸ Pydantic V2.11 Pro Tips

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel, frozen=True):
    id: int
    email: EmailStr
    created_at: datetime = Field(..., alias="createdAt", frozen=True)
```

* Use `model_validate` instead of manual dict access inside adapters.
* Export JSON Schema ⇒ `User.model_json_schema()` → feeds the docs generator.

---

## 6 ▸ Tenacity Policies

*Define policy once, inject via HookConfig.*

```python
from tenacity import RetryCallState, wait_random_exponential

def log_before(retry_state: RetryCallState):  # noqa: D401
    logger.warning("retrying %s (%s)", retry_state.fn, retry_state.attempt_number)

policy = dict(
    wait=wait_random_exponential(multiplier=1, max=20),
    stop=tenacity.stop_after_attempt(4),
    before=log_before,
)
```

Attach: `RetryHook(policy=policy)`.

---

## 7 ▸ Modern Python Typing (PEP 585)

```python
# ❌ AVOID: importing from typing for built-in containers
from typing import Dict, List, Optional, Set, Tuple

def old_style(users: List[Dict[str, str]], active: Optional[bool] = None) -> Tuple[int, Set[str]]:
    pass

# ✅ PREFER: built-in types as generic containers (PEP 585, Python 3.10+)
def modern_style(users: list[dict[str, str]], active: bool | None = None) -> tuple[int, set[str]]:
    pass
```

* Use built-in types directly for generic annotations (Python 3.10+)
* Prefer `|` union operator over `Union` (PEP 604)
* Reserve `typing` imports for special types without built-in equivalents:
  * `typing.TypeVar`, `typing.Protocol`, `typing.Callable`, `typing.ParamSpec`, etc.
* Type aliases improve readability: `UserDict = dict[str, str]`

---

## 8 ▸ structlog & OTEL

```python
import structlog, opentelemetry.trace as otel

def enrich(_, __, event_dict):
    span = otel.get_current_span()
    if span and span.get_span_context().trace_id:
        event_dict["trace_id"] = f"{span.get_span_context().trace_id:032x}"
    return event_dict

structlog.configure(processors=[enrich, structlog.processors.JSONRenderer()])
```

All adapters log `method`, `path`, `duration_ms`, `status` by default.

---

## 9 ▸ Writing Robust Plugins

1. **Lazy-import** heavy deps; raise `ImportError` with actionable message.

2. Validate dc-api-x version:

   ```python
   import importlib.metadata as im, packaging.version as pkg
   if pkg.parse(im.version("dc-api-x")) < pkg.parse("0.2.0"):
       raise RuntimeError("oracle_db plugin needs dc-api-x ≥0.2.0")
   ```

3. Publish wheels with `pyproject.toml [entry-points."dc_api_x.plugins"]`.

4. Provide a `--dummy` mode for unit tests (fast, no network).

5. Document required ENV vars in your plugin README.

---

## 10 ▸ Testing & Mocking

* **responses** for HTTP adapters (`responses.activate`).
* **pytest-postgresql** / Testcontainers for DB integration tests.
* `apix.testing.MockAdapter` for deterministic unit tests.

---

## 11 ▸ Performance & Memory

| Tip                                                 | Impact                           |
| --------------------------------------------------- | -------------------------------- |
| Reuse httpx client, set `limits=max_keepalive=20`   | Latency -30 %                    |
| Use SQLAlchemy compiled cache (`engine.echo_cache`) | Heavy OLTP apps                  |
| `pydantic.Config.ser_json_typed_dict = True`        | 2× faster serialization          |
| Declare `__slots__` in adapters                     | Cut adapter instances \~40 % RAM |

---

## 12 ▸ Security Checklist

* TLS verified (`verify_ssl=True`) by default.
* Avoid `allow_redirects=True` against untrusted hosts.
* Never log secrets – hook `ScrubSecretsHook` strips tokens & passwords.
* Use `oracledb.connect(dsn, purity="self")` to avoid session bleed in pools.

---

## 13 ▸ Ruff Linting Best Practices

```python
# ARG002: Unused method arguments
def process(self, _method, _url, **kwargs):  # Prefix unused args with _
    return self._process_with_kwargs(**kwargs)

# PLR0913: Too many arguments
@dataclass  # Use dataclasses for parameter groups
class ClientOptions:
    timeout: int = 30
    retry: bool = True
    max_connections: int = 10

def create_client(url: str, options: ClientOptions = None):
    options = options or ClientOptions()
    # ...

# COM812: Missing trailing commas
config = {
    "host": "example.com",
    "port": 443,
    "ssl": True,  # <- Always add trailing comma in multiline collections
}

# SIM102: Nested ifs
# Instead of:
# if a:
#     if b:
#         do_something()
# Use:
if a and b:
    do_something()

# TRY003: Long exception messages
# Instead of:
# raise ValueError("This is a very long detailed error message")
# Use custom exception classes:
class ConfigurationError(ValueError):
    """Raised when configuration is invalid."""
    
raise ConfigurationError("Missing required field")

# BLE001: Blind except
try:
    process_data()
except (ValueError, KeyError, TypeError):  # Specific exceptions
    handle_error()
# Avoid: except Exception

# TRY400: Use logging.exception in handlers
try:
    do_something_risky()
except Exception:
    # Instead of print or logger.error:
    logger.exception("Operation failed")  # Includes full traceback
```

---

## 14 ▸ Future Library Integrations

DCApiX plans to integrate several powerful libraries through its plugin ecosystem. Here are best practices and patterns for working with these upcoming integrations. For detailed implementation timelines, see our [Plugin Roadmap](15-pluggy.md#future-plugin-roadmap).

### 14.1 HTTPX Advanced Features

The planned **dc-api-x-httpx** plugin will leverage HTTPX's modern features:

```python
import httpx

# HTTP/2 with connection pooling and async support
async def fetch_with_httpx():
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(http2=True, limits=limits) as client:
        # Parallel requests
        tasks = [client.get(f"https://api.example.com/items/{i}") for i in range(10)]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Streaming response processing
def stream_large_dataset():
    with httpx.Client() as client:
        with client.stream("GET", "https://api.example.com/large-dataset") as response:
            for chunk in response.iter_lines():
                yield process_chunk(chunk)
```

### 14.2 Advanced LDAP Operations

The multiple LDAP plugins (ldap3, python-ldap, Ldaptor) will enable advanced directory operations:

```python
# ldap3 pattern for efficient searches
def efficient_ldap_search(search_base, search_filter):
    from ldap3 import Server, Connection, SUBTREE, RESTARTABLE
    
    server = Server('ldap://example.com', get_info='ALL')
    conn = Connection(server, 'uid=admin,cn=users,dc=example,dc=com', 'password',
                     client_strategy=RESTARTABLE, auto_bind=True)
    
    # Paged search for large directories
    entry_list = []
    conn.search(search_base, search_filter, search_scope=SUBTREE,
                attributes=['cn', 'mail'], paged_size=100)
                
    # Process paged results
    entry_list.extend(conn.entries)
    cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    while cookie:
        conn.search(search_base, search_filter, search_scope=SUBTREE,
                    attributes=['cn', 'mail'], paged_size=100, paged_cookie=cookie)
        entry_list.extend(conn.entries)
        cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    
    return entry_list
```

### 14.3 ETL Patterns with Singer and Meltano

The **dc-api-x-singer** and **dc-api-x-meltano** plugins will enable standardized data pipelines:

```python
# Creating a Singer Tap implementation
class MyCustomTap:
    def discover(self):
        """Return a catalog of available streams."""
        return {
            "streams": [
                {
                    "tap_stream_id": "users",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    },
                    "metadata": [
                        {"breadcrumb": [], "metadata": {"selected": True}}
                    ]
                }
            ]
        }
    
    def sync(self, state=None):
        """Sync data from the source."""
        for record in self._fetch_records(state):
            yield {
                "type": "RECORD",
                "stream": "users",
                "record": record
            }
```

### 14.4 System Monitoring with OSQuery

The **dc-api-x-osquery** plugin will enable SQL-based system monitoring:

```python
def monitor_system_resources():
    import osquery
    
    # Initialize osquery instance
    instance = osquery.SpawnInstance()
    instance.open()
    
    # Query system information using SQL
    processes = instance.client.query("SELECT pid, name, cpu_time FROM processes ORDER BY cpu_time DESC LIMIT 10")
    memory_usage = instance.client.query("SELECT * FROM memory_info")
    disk_usage = instance.client.query("SELECT * FROM disk_usage")
    
    return {
        "top_processes": processes.response,
        "memory": memory_usage.response,
        "disk": disk_usage.response
    }
```

### 14.5 Infrastructure Querying with Steampipe

The **dc-api-x-steampipe** plugin will enable SQL queries across cloud infrastructure:

```python
def query_cloud_resources():
    from steampipe_client import SteampipeClient
    
    client = SteampipeClient()
    
    # Query AWS resources with SQL
    ec2_instances = client.query("""
        SELECT 
            instance_id, 
            instance_type, 
            region, 
            state_name 
        FROM 
            aws_ec2_instance
        WHERE 
            tags ->> 'Environment' = 'Production'
    """)
    
    # Query multi-cloud resources
    multi_cloud_vms = client.query("""
        SELECT
            'AWS' as cloud,
            instance_id as id,
            instance_type as type
        FROM
            aws_ec2_instance
        UNION
        SELECT
            'Azure' as cloud,
            id,
            size as type
        FROM
            azure_compute_virtual_machine
    """)
    
    return {
        "ec2_instances": ec2_instances,
        "multi_cloud_vms": multi_cloud_vms
    }
```

These integration patterns demonstrate how DCApiX will leverage these powerful libraries to expand its capabilities while maintaining its core principles of clean APIs, strong typing, and comprehensive documentation.
