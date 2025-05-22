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
| Models| **pydantic v2** | Custom validators, generics, `model_validate` on external payloads, JSON Schema export |
| Retry | **tenacity** | Exponential back-off + jitter, per-adapter policies, circuit-breaker pattern |
| Plugins| **pluggy** | Dynamic discovery, version compat guard via `PluginValidationError` |
| Logging| **structlog** + **rich** | Context vars (`bind`), colorised console, JSON when `LOG_AS_JSON=1` |
| CLI   | **typer** | Auto-completion, rich-help, parameter callbacks |
| Obs.  | **opentelemetry-api / sdk** | Span injection inside hooks (`trace_id` logged) |

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

## 5 ▸ Pydantic v2 Pro Tips

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
    authenticate()
except AuthError as e:
    logging.exception("Authentication failed")  # Not logging.error(f"...")

# PLR2004: Magic values
HTTP_UNAUTHORIZED = 401  # Define constants
if response.status_code == HTTP_UNAUTHORIZED:
    refresh_token()
```

---

## 14 ▸ Advanced Code Quality with wemake-python-styleguide

For projects requiring the strictest code quality standards, combine ruff with wemake-python-styleguide:

```python
# WPS221: Complex expressions with multiple conditions
# ❌ AVOID:
result = [x for x in items if x > 10 and x % 2 == 0 and is_valid(x)]

# ✅ PREFER: Split into steps
def is_valid_item(x):
    return x > 10 and x % 2 == 0 and is_valid(x)

result = [x for x in items if is_valid_item(x)]

# WPS204: Overused expressions
# ❌ AVOID:
if some_dict.get('key') and some_dict.get('key').get('nested'):
    value = some_dict.get('key').get('nested')
    # Use value...

# ✅ PREFER: Extract to variables
key_data = some_dict.get('key')
if key_data and key_data.get('nested'):
    nested_value = key_data.get('nested')
    # Use nested_value...

# WPS226: String literal overuse
# ❌ AVOID:
if status == 'success' or status == 'partial_success':
    print('Operation succeeded with status: ' + status)
    
# ✅ PREFER: Use constants
SUCCESS_STATUS = 'success'
PARTIAL_SUCCESS_STATUS = 'partial_success'
SUCCESS_MESSAGE = 'Operation succeeded with status: {0}'

if status in (SUCCESS_STATUS, PARTIAL_SUCCESS_STATUS):
    print(SUCCESS_MESSAGE.format(status))

# WPS210: Too many local variables
# WPS231: Too high function cognitive complexity
# Solutions:
# 1. Break into smaller functions
# 2. Use composition
# 3. Apply functional programming patterns
```

Setup:

```bash
# Installation
pip install wemake-python-styleguide

# Usage with ruff
ruff check && ruff format && flake8 . --select=WPS

# Configuration in setup.cfg
[flake8]
select = WPS
ignore = WPS305,WPS306  # Allow f-strings
max-complexity = 10
max-line-length = 88
```

Benefits:

* Enforces extremely strict code quality standards
* Identifies complex structures that may lead to maintainability issues
* Promotes modular, testable code architecture
* Complements ruff by focusing on code complexity metrics

---

## 15 ▸ Type Safety with mypy

```python
# Always fully annotate function signatures (no-untyped-def)
def connect(
    url: str,
    options: ConnectionOptions | None = None,
) -> Connection:
    # Implementation...

# Validate None access to prevent "union-attr" errors
def get_username(user: User | None) -> str:
    if user is None:
        return "anonymous"
    return user.username  # Safe access after None check

# Cast Any to specific types for "no-any-return" errors
def get_response_data() -> dict[str, str]:
    response = fetch_external_data()  # Returns Any
    # Type validation to ensure return type matches annotation
    return {str(k): str(v) for k, v in response.items()}

# Install missing type stubs
# python -m pip install types-requests types-PyYAML

# Handle type-incompatible assignments
def process_item_count(config: dict[str, Any]) -> int:
    # Not safe: count = config.get('count')  # might be None or str
    count_value = config.get('count')
    if count_value is None:
        return 0
    elif isinstance(count_value, int):
        return count_value
    return int(count_value)  # Convert str to int
```

Common mypy errors to fix:

* `no-untyped-def`: Add complete parameter and return type annotations
* `union-attr`: Check for `None` before accessing attributes
* `no-any-return`: Validate/cast return values to match declared type
* `import-untyped`: Install type stubs with `python -m pip install types-package`
* `assignment`: Ensure types match in assignments or add proper conversion

---

## 16 ▸ Cheat-Sheet for Plugin Authors

| Step | Action                                                                                  |
| ---- | --------------------------------------------------------------------------------------- |
| 1    | Fork the [template-plugin repo](https://github.com/datacosmos/dc-api-x-plugin-template) |
| 2    | Implement adapter in `<50` lines (inherit `ProtocolAdapter`)                            |
| 3    | Write pytest unit test + Sphinx docs                                                    |
| 4    | `poetry build && twine upload --repository datacosmos-internal dist/*`                  |
| 5    | Add yourself to AUTHORS.md 🎉                                                           |

---

* Master these advanced tools and dc-api-x becomes a superpower—not just a library.

## Advanced Libraries & Code Quality Tools

This document covers advanced libraries and tools used in the dc-api-x project to maintain code quality and enforce standards.

### Code Quality Tools

### wemake-python-styleguide

[wemake-python-styleguide](https://wemake-python-styleguide.readthedocs.io/) is an opinionated, strict linter for Python that enforces high code quality standards. It's built on top of flake8 and includes over 900 checks to ensure your code remains maintainable and clean.

### Key Features

* **Extremely strict**: Enforces best practices and prevents many anti-patterns
* **Comprehensive**: Over 900 built-in checks for various issues
* **Customizable**: Can be fine-tuned for your project's specific needs
* **Well-documented**: Detailed explanations for each error code

#### Common Issues and Solutions

##### ARG002: Unused method arguments

```python
# ❌ Error: Unused method argument
def process_data(data, options):  # options is unused
    return transform(data)

# ✅ Solution 1: Use underscore prefix for unused arguments
def process_data(data, _options):
    return transform(data)

# ✅ Solution 2: Remove the unused parameter if not needed by interface
def process_data(data):
    return transform(data)

# ✅ Solution 3: Use the parameter
def process_data(data, options):
    if options.get("verbose"):
        logger.debug("Processing data")
    return transform(data)
```

##### PLR2004: Magic value used in comparison

```python
# ❌ Error: Magic value in comparison
if status_code == 200:  # 200 is a magic value
    process_response(response)

# ✅ Solution: Use named constants
HTTP_OK = 200
if status_code == HTTP_OK:
    process_response(response)
```

##### WPS432: Found magic number

Similar to PLR2004, but for numeric literals used in other contexts.

```python
# ❌ Error: Magic number
def calculate_tax(amount):
    return amount * 0.21  # 0.21 is a magic number

# ✅ Solution: Use named constants
TAX_RATE = 0.21
def calculate_tax(amount):
    return amount * TAX_RATE
```

##### WPS202: Found too many module members

```python
# ❌ Error: Too many module members
# models.py with 20+ classes and functions

# ✅ Solution: Split into submodules
# models/__init__.py - Exports everything
# models/user.py - User-related models
# models/product.py - Product-related models
# models/order.py - Order-related models
```

##### WPS210: Found too many local variables

```python
# ❌ Error: Too many local variables
def process_order(order):
    customer_name = order.customer.name
    customer_email = order.customer.email
    order_total = order.total
    tax_amount = order_total * TAX_RATE
    shipping_cost = calculate_shipping(order)
    discount = apply_discounts(order)
    final_price = order_total + tax_amount + shipping_cost - discount
    # ... more variables and processing
    return final_price

# ✅ Solution: Extract smaller functions and use data classes
def calculate_final_price(order):
    tax_amount = calculate_tax(order.total)
    shipping_cost = calculate_shipping(order)
    discount = apply_discounts(order)
    return order.total + tax_amount + shipping_cost - discount

def process_order(order):
    customer = get_customer_details(order.customer)
    final_price = calculate_final_price(order)
    # Much fewer local variables
    return create_order_summary(customer, order, final_price)
```

#### Configuring for Your Project

To configure wemake-python-styleguide for your project, add settings to `setup.cfg`:

```ini
[flake8]
# Base flake8 configuration:
max-line-length = 88
select = WPS
ignore = 
    # Allow f-strings
    WPS305,
    WPS306,
    # Allow docstrings without imperative mood
    WPS326

# wemake-python-styleguide settings:
max-complexity = 10
max-imports = 15
max-module-members = 15
max-methods = 10
max-local-variables = 8
max-arguments = 5
max-attributes = 8
max-cognitive-complexity = 15

# Per-file ignores
per-file-ignores =
    # Allow magic values in test files
    tests/*:PLR2004,ARG002
    # Allow unused arguments in interface implementations
    src/your_module/client.py:ARG002
```

##### Integration with CI/CD

Add wemake-python-styleguide to your CI/CD pipeline to enforce these rules on every commit:

```yaml
- name: Lint with wemake-python-styleguide
  run: flake8 src/ tests/ --select=WPS
```

##### Ignoring Specific Issues

For cases where rule violations are necessary or appropriate:

1. **Inline ignores** for specific lines:

   ```python
   value = 42  # noqa: WPS432
   ```

2. **Per-file ignores** in `setup.cfg`:

   ```ini
   per-file-ignores =
       tests/*:PLR2004,ARG002
   ```

3. **Global ignores** for specific error codes:

   ```ini
   ignore = 
       WPS305,  # Allow f-strings
       WPS306,  # Allow string format
   ```

#### Examples of Complex Code Issues

Below are some examples of complex code patterns that would be flagged by wemake-python-styleguide:

##### 1. Nested Functions and Classes

```python
# ❌ Complex nested structure
def outer_function():
    def inner_function():
        class NestedClass:  # WPS431: Found nested class
            def __init__(self):
                self.value = 1
        return NestedClass()
    return inner_function()

# ✅ Flattened structure
class Helper:
    def __init__(self):
        self.value = 1

def create_helper():
    return Helper()

def outer_function():
    return create_helper()
```

##### 2. Complex Expressions

```python
# ❌ Complex expression
result = [x for x in range(10) if x % 2 == 0 and x > 5 or x % 3 == 0]  # WPS221

# ✅ Simpler expressions
even_greater_than_five = [x for x in range(10) if x % 2 == 0 and x > 5]
divisible_by_three = [x for x in range(10) if x % 3 == 0]
result = even_greater_than_five + divisible_by_three
```

##### 3. Deep Nesting

```python
# ❌ Deep nesting
def process_data(data):
    if data:
        for item in data:
            if item.active:
                for subitem in item.subitems:
                    if subitem.valid:  # WPS220: Found too deep nesting
                        process_subitem(subitem)

# ✅ Reduced nesting with early returns and helper functions
def is_processable(subitem):
    return subitem.valid

def process_subitems(subitems):
    for subitem in subitems:
        if is_processable(subitem):
            process_subitem(subitem)

def process_item(item):
    if not item.active:
        return
    process_subitems(item.subitems)

def process_data(data):
    if not data:
        return
    for item in data:
        process_item(item)
```

##### 4. Function with Too Many Arguments

```python
# ❌ Too many arguments
def configure_service(name, host, port, username, password, timeout, retries, ssl, proxy, debug):  # WPS211
    # ...implementation

# ✅ Using a configuration object
@dataclass
class ServiceConfig:
    name: str
    host: str
    port: int
    username: str
    password: str
    timeout: int = 30
    retries: int = 3
    ssl: bool = True
    proxy: str | None = None
    debug: bool = False

def configure_service(config: ServiceConfig):
    # ...implementation
```

By following these guidelines and using the tools like wemake-python-styleguide, you can maintain a high-quality codebase that remains maintainable and robust as it grows.
