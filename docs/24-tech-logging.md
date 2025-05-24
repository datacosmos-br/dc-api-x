# Structured Logging with Logfire

> *"Logs are useless unless they can be searched, filtered, and analyzed."*
> This guide explains how DCApiX integrates structured logging to provide powerful observability and diagnostics
> capabilities across the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [23 - Tech: Testing](23-tech-testing.md) | **24 - Tech: Structured Logging** | [25 - Tech: Typing](25-tech-typing.md) |

---

## 1. Introduction

DCApiX leverages [Logfire](https://logfire.dev) for advanced structured logging, monitoring, and observability. Logfire
provides powerful integration with Pydantic and other libraries used in DCApiX, making it an ideal companion for
enterprise-grade applications.

---

## 2. Core Features

### 2.1 Pydantic Integration

DCApiX takes advantage of Logfire's seamless integration with Pydantic:

* **Model Validation** - Automatic logging of validation errors
* **Schema Events** - Track schema changes and validations
* **Field Binding** - Structured logging of model fields

### 2.2 HTTP Client Integration

For API requests and responses, Logfire provides excellent HTTP client integrations:

* **HTTPX Integration** - Used with DCApiX's primary HTTP client
* **Request/Response Logging** - Detailed logging of HTTP operations
* **Performance Metrics** - Track timing and response sizes

### 2.3 Database Integration

Logfire provides specialized support for database operations:

* **SQLAlchemy Integration** - For logging database queries and performance metrics
* **Query Timing** - Measure and log query execution time
* **Connection Pooling** - Monitor connection pool usage

### 2.4 Advanced Features

Logfire extends beyond basic logging with powerful features:

* **Sensitive Data Scrubbing** - Automatically redact sensitive information
* **Environment Management** - Configure logging differently per environment
* **Context Binding** - Add structured context to log entries
* **Log Sampling** - Performance optimization for high-volume logs

---

## 3. Basic Usage

### 3.1 Setup and Configuration

Initialize Logfire in your DCApiX application:

```python
import logfire
from dc_api_x.config import Config

def setup_logging(config: Config):
    """Initialize Logfire with DCApiX configuration."""
    logfire.configure(
        service_name="dc-api-x",
        service_version=config.version,
        environment=config.environment,
        level="DEBUG" if config.debug else "INFO",
        scrub_fields=["password", "api_key", "token", "secret"],
    )
```

### 3.2 Logging API Requests

DCApiX automatically logs API requests and responses using Logfire:

```python
import logfire
from dc_api_x import ApiClient

client = ApiClient(url="https://api.example.com")

# This request will be automatically logged with request/response details
response = client.get("users")

# Add custom context to logs
logfire.bind(operation="fetch_users", user_count=len(response.data))
logfire.info("Successfully fetched users")
```

### 3.3 Logging Database Operations

When using the DatabaseAdapter, operations are logged with performance metrics:

```python
from dc_api_x import get_adapter
import logfire

# Get database adapter
db = get_adapter("oracle_db")

# Log database context
with logfire.context(database="oracle", operation="user_query"):
    # Query will be automatically logged with timing information
    users = db.query("SELECT * FROM users WHERE active = :active", {"active": True})
    logfire.info("Retrieved active users", count=len(users))
```

### 3.4 Structured Logging with Pydantic Models

Log Pydantic models with automatic field validation:

```python
from pydantic import BaseModel, EmailStr
import logfire

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

user = User(id=1, name="John Doe", email="john@example.com")

# Log the user model with full structure
logfire.info("User created", user=user)

# Fields will be automatically redacted if they match scrub_fields
secure_data = {"password": "secret123", "credit_card": "4111-1111-1111-1111"}
logfire.info("Processing payment", data=secure_data)  # password will appear as "***"
```

---

## 4. Advanced Features

### 4.1 Context Managers

Use context managers to add structured information to a block of code:

```python
import logfire
from dc_api_x import ApiClient

client = ApiClient(url="https://api.example.com")

# Add request_id to all logs in this context
with logfire.context(request_id="req-123"):
    response = client.get("users")
    # Process response
    logfire.info("Processed users", count=len(response.data))

    # Nested contexts are supported
    with logfire.context(operation="filter_active"):
        active_users = [u for u in response.data if u.get("active")]
        logfire.info("Filtered active users", count=len(active_users))
```

### 4.2 Error Handling

Log exceptions with proper context:

```python
import logfire
from dc_api_x import ApiClient, ApiError

client = ApiClient(url="https://api.example.com")

try:
    response = client.get("users")
    # Process response
except ApiError as e:
    # Log with full exception details
    logfire.exception("Failed to fetch users",
                      status_code=e.status_code,
                      error_type=type(e).__name__)
```

### 4.3 Performance Metrics

Track operation timing with built-in utilities:

```python
import logfire
import time

with logfire.Timer() as timer:
    # Perform operation
    time.sleep(0.5)

logfire.info("Operation completed", duration_ms=timer.milliseconds)
```

---

## 5. Integration with other DCApiX Components

### 5.1 ApiClient Integration

The ApiClient automatically logs requests and responses:

```python
from dc_api_x import ApiClient
import logfire

# Configure Logfire with detailed request logging
logfire.configure(
    service_name="my-service",
    log_request_headers=True,  # Log HTTP headers (credentials are scrubbed)
    log_request_body=True,     # Log request bodies
    log_response_headers=True  # Log response headers
)

client = ApiClient(url="https://api.example.com")

# This request will be logged with detailed information
response = client.get("users")
```

### 5.2 Plugin System Integration

When developing DCApiX plugins, integrate Logfire for consistent logging:

```python
from dc_api_x.ext.adapters import ProtocolAdapter
import logfire

class MyCustomAdapter(ProtocolAdapter):
    """Custom protocol adapter with Logfire integration."""

    def __init__(self, connection_string: str):
        self.conn_string = connection_string
        logfire.info("Initializing custom adapter",
                     adapter_type=self.__class__.__name__)

    def request(self, method: str, path: str, **kwargs):
        # Log request with sanitized connection string
        with logfire.context(method=method, path=path):
            logfire.debug("Sending request")
            # Implementation
            return result
```

---

## 6. Best Practices

1. **Use Structured Logging**: Always use keyword arguments rather than string interpolation.

   ```python
   # Good
   logfire.info("User created", user_id=123, status="active")

   # Avoid
   logfire.info(f"User created: {user_id} with status {status}")
   ```

2. **Log Levels**: Use appropriate log levels.
   * `debug`: Detailed information for debugging
   * `info`: Confirmation of normal events
   * `warning`: Something unexpected but not an error
   * `error`: An error that prevented an operation
   * `critical`: An error that requires immediate attention

3. **Context Binding**: Use context to add recurring information rather than repeating in each log.

   ```python
   # Add context once
   logfire.bind(request_id=req_id, user_id=user.id)

   # Then log without repeating
   logfire.info("Operation started")
   # ... do work ...
   logfire.info("Operation completed")
   ```

4. **Security**: Never log sensitive data. Use `scrub_fields` to automatically redact known sensitive fields.

5. **Performance**: For high-volume logs, consider using sampling to reduce overhead.

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools
* [23 - Tech: Testing](23-tech-testing.md) - Testing guide
* [25 - Tech: Typing](25-tech-typing.md) - Advanced typing and Pydantic usage
* [30 - CLI Reference](30-cli-reference.md) - Command-line interface reference
