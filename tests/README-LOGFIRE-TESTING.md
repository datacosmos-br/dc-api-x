# Logfire Testing Pattern

This document explains how to use the structured logging pattern with Logfire in your tests.

## Overview

The DC-API-X project includes a standardized pattern for using Logfire in tests. This pattern ensures:

1. Tests work even when Logfire is not installed
2. Consistent logging across all tests
3. Easy assertion of log contents
4. Context tracking across test operations
5. Proper redaction of sensitive data

## Import Pattern

Instead of importing Logfire directly, always import from the `tests` package:

```python
from tests import (
    LOGFIRE_AVAILABLE,
    LogEntry,
    context,
    debug,
    error,
    info,
    requires_logfire,
    span,
    test_context,
    warning,
)
```

## Testing for Logfire Availability

Use the `requires_logfire` decorator to mark tests that require Logfire:

```python
@requires_logfire
def test_something_with_logging(logfire_testing):
    """Test that requires Logfire."""
    info("This is a test message")

    # Check logs
    assert len(logfire_testing.logs) > 0
```

You can also use the decorator with a parameter to allow the test to run with mock Logfire:

```python
@requires_logfire(strict=False)
def test_something_with_optional_logfire(logfire_testing):
    """Test that uses Logfire if available but continues if not."""
    info("This is a test message")

    # Test will proceed even if Logfire is not installed
```

## Using the Logfire Testing Fixture

The `logfire_testing` fixture configures Logfire and captures logs:

```python
def test_with_logfire(logfire_testing):
    """Test with logfire capture."""
    # Log messages
    info("Log message", value=42)

    # Verify logs
    assert len(logfire_testing.logs) > 0
    assert logfire_testing.logs[0]["message"] == "Log message"
    assert logfire_testing.logs[0]["value"] == 42

    # Access log properties directly
    assert logfire_testing.logs[0].message == "Log message"
    assert logfire_testing.logs[0].level == "INFO"
```

### Finding Logs by Criteria

The fixture provides helper methods to find logs:

```python
def test_find_logs(logfire_testing):
    """Test finding logs by criteria."""
    # Log some messages
    info("First message", value=1)
    warning("Second message", value=2)
    error("Error message", code=500, value=3)

    # Find logs by criteria
    warnings = logfire_testing.find_logs(level="WARNING")
    assert len(warnings) == 1
    assert warnings[0].message == "Second message"

    # Find first log matching criteria
    error_log = logfire_testing.find_log(code=500)
    assert error_log is not None
    assert error_log.message == "Error message"
    assert error_log.value == 3
```

## Logging Context

Use the `context` function to add context to logs:

```python
def test_with_context(logfire_testing):
    """Test with logging context."""
    with context(operation="test_operation", user_id="test-user"):
        info("Log with context")

    # Verify context was added
    log = logfire_testing.find_log(message="Log with context")
    assert log.operation == "test_operation"
    assert log.user_id == "test-user"
```

For test-specific context, use the `test_context` helper:

```python
def test_with_test_context(logfire_testing):
    """Test with test_context helper."""
    with test_context(operation="special_operation"):
        info("Test operation log")

    # The test_context helper automatically adds test=True
    log = logfire_testing.find_log(message="Test operation log")
    assert log.test is True
    assert log.operation == "special_operation"
```

## Measuring Operations

Use `span` to measure operations:

```python
def test_with_span(logfire_testing):
    """Test with span timing."""
    with span("operation_name"):
        # Do something
        time.sleep(0.1)

    # Verify span was created
    span_log = logfire_testing.find_log(span_name="operation_name")
    assert span_log is not None
    assert span_log.duration_ms >= 100
```

## Mock Logfire for Non-Logfire Environments

The test package provides mock implementations of all Logfire functions that work when Logfire is not installed:

```python
# This will work with or without Logfire installed
from tests import info, context, span

def test_something():
    with context(request_id="1234"):
        with span("operation"):
            info("This works regardless of Logfire availability")
```

## LogEntry Object

All log entries are wrapped in a `LogEntry` object that provides attribute access to log fields:

```python
def test_log_entry(logfire_testing):
    """Test LogEntry object."""
    info("Test message", value=42, items=["a", "b"])

    log = logfire_testing.logs[0]

    # Access as dictionary
    assert log["value"] == 42

    # Access as attribute
    assert log.value == 42
    assert log.items == ["a", "b"]
    assert log.message == "Test message"
    assert log.level == "INFO"
```

## Testing API Clients

When testing API clients, verify logging of requests and responses:

```python
@requires_logfire
def test_api_request_logging(api_client, logfire_testing):
    """Test API request logging."""
    # Make request
    response = api_client.get("users")

    # Verify logs
    request_logs = logfire_testing.find_logs(method="GET")
    assert len(request_logs) > 0

    # Find the specific request log
    request_log = logfire_testing.find_log(url=lambda url: "users" in url)
    assert request_log is not None
```

## Testing Validation

Verify that validation functions log appropriate warnings:

```python
@requires_logfire
def test_validation_logging(logfire_testing):
    """Test validation logging."""
    # Test invalid value
    is_valid, _ = validate_email("not-an-email")

    # Verify logs
    validation_log = logfire_testing.find_log(field="email")
    assert validation_log is not None
    assert validation_log.level == "WARNING"
    assert validation_log.value == "not-an-email"
```

## Sensitive Data Redaction

Test that sensitive data is properly redacted:

```python
@requires_logfire
def test_sensitive_data_redaction(api_client, logfire_testing):
    """Test sensitive data redaction."""
    # Make request with sensitive data
    api_client.post("login", json_data={
        "username": "testuser",
        "password": "secret123"
    })

    # Verify password was redacted
    request_log = logfire_testing.find_log(request_body=lambda body: isinstance(body, dict))
    assert request_log is not None
    assert request_log.request_body["password"] == "[REDACTED]"
```

## Running Tests with Logfire

Use the `--logfire` flag to enable Logfire during test runs:

```bash
python -m pytest --logfire tests/
```

You can also run only tests that require Logfire:

```bash
python -m pytest -m logfire tests/
```

## Automatic Test Context

The `logfire_testing` fixture automatically adds useful test metadata to all logs:

- `test_name`: Name of the test function
- `test_module`: Name of the test module
- `test_class`: Name of the test class (if applicable)
- `test_file`: Name of the test file
- `pytest_nodeid`: Full pytest node ID

This makes it easy to filter logs by test in your logging UI or dashboard.

## Best Practices

1. Always use the `requires_logfire` decorator for tests that rely on Logfire
2. Use the `find_log` and `find_logs` methods instead of manually filtering logs
3. Use `LogEntry` attribute access (`.field_name`) for cleaner test code
4. Test both happy path and error path logging
5. Verify context values are properly included in logs
6. Check that sensitive data is properly redacted
7. Use span timing for performance-sensitive operations
8. Don't assert exact log message formats, as they may change
9. Use `test_context()` when adding additional context to tests
