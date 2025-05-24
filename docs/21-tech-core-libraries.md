# Core Libraries

> *"Great frameworks hide complexity—great teams still need to master it."*
> This guide explains **how** and **why** DCApiX leverages a curated stack of
> core libraries, and documents best-practice patterns for contributors and plugin authors.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [20 - Tech: Overview](20-tech-overview.md) | **21 - Tech: Core Libraries** | [22 - Tech: Developer Tools](22-tech-developer-tools.md) |

---

## 1. Quick Reference Matrix

| Layer | Library | Advanced Features we **expect** you to use |
|-------|---------|--------------------------------------------|
| HTTP  | **httpx** | *HTTP/2*, connection pooling, `limits`, streaming, `AsyncClient` |
| DB    | **SQLAlchemy 2** | *Core select*, sync & async engines, `Session.begin()` context-manager, SQL compilation caching |
| Oracle| **python-oracledb** | Thin vs Thick mode, DRCP pooling, `json.dumps()` type handlers |
| LDAP  | **ldap3** | Connection pooling, *DirSync* (AD), RFC 4533 Sync Request, `RESTARTABLE` strategy |
| Models| **Pydantic** | Custom validators, generics, `model_validate` on external payloads, JSON Schema export |
| Retry | **tenacity** | Exponential back-off + jitter, per-adapter policies, circuit-breaker pattern |
| Plugins| **pluggy** | Dynamic discovery, version compat guard via `PluginValidationError` |

---

## 2. Pydantic (duplicated with 25-)

[Pydantic](https://docs.pydantic.dev/) is used for data validation, serialization, and configuration management in DCApiX.

### 2.1 Key Features

* **Data Validation**: Automatic validation of incoming data
* **Serialization**: Convert between Python objects and JSON/dict formats
* **Type Annotations**: First-class support for Python type hints
* **Settings Management**: Configuration with environment variables, files, and secrets
* **Schema Generation**: Export JSON Schema for API documentation

### 2.2 Best Practices

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel, frozen=True):
    id: int
    email: EmailStr
    created_at: datetime = Field(..., alias="createdAt", frozen=True)
```

* Use `model_validate` instead of manual dict access inside adapters
* Export JSON Schema via `User.model_json_schema()` to feed documentation
* Leverage Pydantic Settings for configuration management
* Use field validators for complex validation logic

### 2.3 Settings Management

DCApiX uses Pydantic Settings for configuration:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        extra="ignore"
    )

    url: str
    username: str
    password: SecretStr
    timeout: int = 30
    verify_ssl: bool = True
```

This allows loading configuration from:
* Environment variables
* `.env` files
* Direct initialization
* Configuration profiles

---

## 3. Pluggy

[Pluggy](https://pluggy.readthedocs.io/) powers DCApiX's plugin system, enabling extensibility and modularity.

### 3.1 Key Features

* **Hook Specifications**: Formal interfaces for plugins to implement
* **Hook Implementations**: Concrete implementations of the hooks
* **Plugin Discovery**: Automatic discovery of plugins via entry points
* **Plugin Registry**: Central registry of discovered plugins

### 3.2 Plugin Architecture

```python
# plugin/__init__.py
"""Example DCApiX plugin."""

def register_adapters(registry):
    """Register custom adapters with DCApiX."""
    from .custom_adapter import CustomAdapter
    registry["custom_protocol"] = CustomAdapter
```

### 3.3 Best Practices

* **Lazy-import** heavy dependencies to reduce startup time
* **Validate** DCApiX version compatibility
* **Publish** wheels with proper entry points
* **Provide** test modes for faster unit testing
* **Document** required environment variables

---

## 4. HTTPX

[HTTPX](https://www.python-httpx.org/) provides modern HTTP client capabilities in DCApiX.

### 4.1 Key Features

* **HTTP/2 Support**: More efficient connections
* **Connection Pooling**: Reuse connections for better performance
* **Async Support**: Both synchronous and asynchronous APIs
* **Streaming**: Efficient handling of large responses
* **Timeouts**: Comprehensive timeout handling

### 4.2 Best Practices

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

* **Always reuse clients**: Create one client per adapter, not per request
* **Set appropriate limits**: Use `limits=httpx.Limits(max_keepalive=20)`
* **Handle streaming properly**: Use context managers for streaming responses

---

## 5. SQLAlchemy

[SQLAlchemy](https://www.sqlalchemy.org/) is used for database connectivity in DCApiX.

### 5.1 Key Features

* **Core API**: SQL expression language
* **ORM**: Object-relational mapping
* **Connection Pooling**: Efficient connection management
* **Dialects**: Support for various database backends
* **Type System**: Rich type mapping between Python and SQL

### 5.2 Best Practices

```python
from sqlalchemy import select
with engine.connect() as conn:
    for row in conn.scalars(select(User).where(User.active.is_(True))):
        # Process row
```

* **Core-first approach**: Prefer `select(User)` over ORM-heavy `.query`
* **Use typed mappings**: `@dataclass` + `registry.mapped` for clear IDE hints
* **Batch operations**: Use `engine.begin()` for transaction management
* **Async support**: Use `sqlalchemy.ext.asyncio.create_async_engine` for async operations

---

## 6. Tenacity

[Tenacity](https://tenacity.readthedocs.io/) provides robust retry logic in DCApiX.

### 6.1 Key Features

* **Retry Policies**: Flexible configuration of retry behavior
* **Backoff Strategies**: Various backoff algorithms including exponential
* **Circuit Breaker**: Prevent cascading failures
* **Event Hooks**: Callbacks for retry events
* **Timeout Control**: Limit the total retry time

### 6.2 Best Practices

```python
from tenacity import RetryCallState, wait_random_exponential

def log_before(retry_state: RetryCallState):
    logger.warning("retrying %s (%s)", retry_state.fn, retry_state.attempt_number)

policy = dict(
    wait=wait_random_exponential(multiplier=1, max=20),
    stop=tenacity.stop_after_attempt(4),
    before=log_before,
)
```

* **Define policy once**: Create reusable policy configurations
* **Add jitter**: Always add randomness to avoid thundering herd problems
* **Log retries**: Use before/after hooks to log retry attempts
* **Set appropriate limits**: Combine `stop_after_attempt` with `stop_after_delay`

---

## 7. Modern Python Typing

DCApiX leverages modern Python typing features:

```python
# ❌ AVOID: importing from typing for built-in containers
from typing import Dict, List, Optional, Set, Tuple

def old_style(users: List[Dict[str, str]], active: Optional[bool] = None) -> Tuple[int, Set[str]]:
    pass

# ✅ PREFER: built-in types as generic containers (PEP 585, Python 3.10+)
def modern_style(users: list[dict[str, str]], active: bool | None = None) -> tuple[int, set[str]]:
    pass
```

### 7.1 Best Practices

* Use built-in types directly for generic annotations (Python 3.10+)
* Prefer `|` union operator over `Union` (PEP 604)
* Reserve `typing` imports for special types without built-in equivalents
* Use type aliases to improve readability: `UserDict = dict[str, str]`

---

## 8. Performance Optimization

| Tip | Impact |
|-----|--------|
| Reuse httpx client, set `limits=max_keepalive=20` | Latency -30% |
| Use SQLAlchemy compiled cache (`engine.echo_cache`) | Improved performance for heavy OLTP apps |
| `pydantic.Config.ser_json_typed_dict = True` | 2× faster serialization |
| Declare `__slots__` in adapters | Cut adapter instances ~40% RAM |

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools like Typer, Logfire, and testing
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Detailed guide on the logging system
* [27 - Tech: Plugin](27-tech-plugin.md) - Detailed guide on the plugin system
