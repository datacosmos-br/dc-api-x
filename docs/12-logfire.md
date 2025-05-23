# Logfire Guide for DCApiX

## Introduction

DCApiX leverages [Logfire](https://logfire.dev) for advanced structured logging, monitoring, and observability. Logfire provides powerful integration with Pydantic V2.11 and other libraries used in DCApiX, making it an ideal companion for enterprise-grade applications.

## Core Logfire Features in DCApiX

### Pydantic Integration

DCApiX takes advantage of Logfire's seamless integration with Pydantic V2.11:

- [Pydantic Integration](https://logfire.pydantic.dev/docs/integrations/pydantic/) - Automatic model logging and validation events
- [Model Validation](https://logfire.pydantic.dev/docs/reference/api/pydantic/) - Specialized logging for validation errors

### HTTP Client Integration

For API requests and responses, Logfire provides excellent HTTP client integrations:

- [HTTPX Integration](https://logfire.pydantic.dev/docs/integrations/http-clients/httpx/) - Used with DCApiX's primary HTTP client
- [Requests Integration](https://logfire.pydantic.dev/docs/integrations/http-clients/requests/) - For legacy HTTP client support
- [AIOHTTP Integration](https://logfire.pydantic.dev/docs/integrations/http-clients/aiohttp/) - For async HTTP operations

### Database Integration

Logfire provides specialized support for database operations:

- [SQLAlchemy Integration](https://logfire.pydantic.dev/docs/integrations/databases/sqlalchemy/) - For logging database queries and performance metrics

### Advanced Logging Features

Logfire extends beyond basic logging with powerful features:

- [Sensitive Data Scrubbing](https://logfire.pydantic.dev/docs/how-to-guides/scrubbing/) - Automatically redact sensitive information
- [Environment Management](https://logfire.pydantic.dev/docs/how-to-guides/environments/) - Configure logging differently per environment
- [Loguru Integration](https://logfire.pydantic.dev/docs/integrations/loguru/) - For compatibility with existing Loguru setups

### Testing and Verification

Robust testing tools ensure your logging works correctly:

- [Testing Tools](https://logfire.pydantic.dev/docs/reference/advanced/testing/) - Verify log output in unit tests
- [Testing API](https://logfire.pydantic.dev/docs/reference/api/testing/) - Programmatic testing capabilities

### Configuration and APIs

Full control over logging behavior:

- [Configuration Options](https://logfire.pydantic.dev/docs/reference/configuration/) - Customize logging behavior
- [CLI Tools](https://logfire.pydantic.dev/docs/reference/cli/) - Command-line utilities
- [Core API](https://logfire.pydantic.dev/docs/reference/api/logfire/) - Programmatic control
- [Error Handling](https://logfire.pydantic.dev/docs/reference/api/exceptions/) - Exception handling patterns
- [Log Propagation](https://logfire.pydantic.dev/docs/reference/api/propagate/) - Control log event flow
- [Log Sampling](https://logfire.pydantic.dev/docs/reference/api/sampling/) - Performance optimization for high-volume logs

## Basic Usage in DCApiX

### Setup and Configuration

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

### Logging API Requests

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

### Logging Database Operations

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

### Structured Logging with Pydantic Models

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

## Advanced Features

### Context Managers

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

### Error Handling

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

### Performance Metrics

Track operation timing with built-in utilities:

```python
import logfire
import time

with logfire.Timer() as timer:
    # Perform operation
    time.sleep(0.5)
    
logfire.info("Operation completed", duration_ms=timer.milliseconds)
```

## Integration with other DCApiX Components

### ApiClient Logging

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

### Plugin System Integration

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

## Best Practices

1. **Use Structured Logging**: Always use keyword arguments rather than string interpolation.

   ```python
   # Good
   logfire.info("User created", user_id=123, status="active")
   
   # Avoid
   logfire.info(f"User created: {user_id} with status {status}")
   ```

2. **Log Levels**: Use appropriate log levels.
   - `debug`: Detailed information for debugging
   - `info`: Confirmation of normal events
   - `warning`: Something unexpected but not an error
   - `error`: An error that prevented an operation
   - `critical`: An error that requires immediate attention

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

## See Also

- [Logfire Documentation](https://logfire.dev/docs/)
- [Pydantic Guide](11-pydantic_guide.md)
- [OpenTelemetry Integration](https://logfire.dev/docs/integrations/opentelemetry/)
