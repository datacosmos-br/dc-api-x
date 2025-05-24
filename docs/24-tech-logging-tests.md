# Structured Logging in Tests with Logfire

This guide explains how to use structured logging with Logfire in your tests.

## Overview

Logfire provides powerful structured logging capabilities that are also useful in testing. By using Logfire in tests, you can:

1. Verify that your code is logging correctly
2. Capture logs for test assertions
3. Add contextual information to test logs
4. Test error handling and error logging
5. Ensure sensitive data is properly redacted

## Setup

DC-API-X includes a `logfire_testing` fixture that configures Logfire for testing and captures logs for assertions:

```python
@pytest.fixture
def logfire_testing(request) -> Generator[Optional[logfire.testing.CapturedLogs], None, None]:
    """Setup Logfire structured logging for tests.

    This fixture configures Logfire for testing with proper context
    and enables the capture of logs for assertions.

    Returns:
        Generator with captured logs for test assertions
    """
    if not LOGFIRE_AVAILABLE:
        pytest.skip("Logfire not available")
        return None

    # Configure Logfire for testing if not already configured
    if not os.environ.get("LOGFIRE_CONFIGURED"):
        dc_logfire.setup_logging(
            service_name="dc-api-x-tests",
            environment="test",
            level="DEBUG",
            local=True,
        )

    test_name = request.node.name
    class_name = getattr(request.cls, "__name__", "")
    module_name = request.module.__name__

    # Create a context for this test
    with logfire.context(
        test_name=test_name,
        test_class=class_name,
        test_module=module_name,
    ):
        # Use Logfire's testing capture
        with logfire.testing.capture() as captured:
            yield captured
```

## Basic Usage

To use Logfire in your tests, include the `logfire_testing` fixture and use the standard Logfire API:

```python
def test_logfire_basic(logfire_testing):
    """Basic test with Logfire."""
    # Log a message
    logfire.info("This is a test message", value=42)

    # Make assertions about the logs
    assert len(logfire_testing.logs) > 0
    assert logfire_testing.logs[0]["message"] == "This is a test message"
    assert logfire_testing.logs[0]["value"] == 42
```

## Testing API Clients

Here's an example of testing API client logging:

```python
@responses.activate
def test_api_request_logging(api_client, logfire_testing):
    """Test that API requests are properly logged with Logfire."""
    # Mock response
    responses.add(
        responses.GET,
        "https://api.example.com/users",
        json={"data": [{"id": 1, "name": "John"}]},
        status=200,
    )

    # Use Logfire context for additional context
    with logfire.context(operation="list_users"):
        response = api_client.get("users")

    # Verify logs
    request_logs = [
        log for log in logfire_testing.logs
        if "https://api.example.com/users" in log.get("url", "")
    ]

    assert len(request_logs) >= 2  # Should have at least 2 logs (start and complete)
```

## Testing Validation

You can test that validation functions properly log validation errors:

```python
def test_invalid_email(logfire_testing):
    """Test validation error logging."""
    # Test invalid email
    is_valid, error = validate_email("not-an-email")
    assert is_valid is False

    # Verify logs
    validation_logs = [
        log for log in logfire_testing.logs
        if log["level"] == "WARNING" and log.get("field") == "email"
    ]

    assert len(validation_logs) > 0
    assert validation_logs[0]["value"] == "not-an-email"
```

## Testing Error Logging

To test error logging, use `pytest.raises` with Logfire assertions:

```python
def test_api_error_logging(api_client, logfire_testing):
    """Test that API errors are properly logged with Logfire."""
    # Mock error response
    responses.add(
        responses.GET,
        "https://api.example.com/error",
        json={"error": "Server error"},
        status=500,
    )

    # Use Logfire span to track the error
    with logfire.span("api_error_test"):
        with pytest.raises(Exception):
            api_client.get("error")

    # Verify error logs
    error_logs = [
        log for log in logfire_testing.logs
        if log["level"] == "ERROR" and "error" in log
    ]

    assert len(error_logs) > 0
```

## Testing Sensitive Data Redaction

You can test that sensitive data is properly redacted in logs:

```python
def test_request_body_logging_with_redaction(api_client, logfire_testing):
    """Test that request bodies are logged with sensitive data redacted."""
    # Create payload with sensitive data
    sensitive_payload = {
        "username": "testuser",
        "password": "secret123",
        "api_key": "abcd1234",
    }

    # Make request with sensitive data
    api_client.post("login", json_data=sensitive_payload)

    # Find logs containing request body
    body_logs = [
        log for log in logfire_testing.logs
        if "request_body" in log
    ]

    # Check that sensitive data was redacted
    body = body_logs[0]["request_body"]
    assert body["password"] == "[REDACTED]"
    assert body["api_key"] == "[REDACTED]"
```

## Best Practices

1. Always check if Logfire is available and skip tests that require it if not
2. Use `logfire.context()` to add test-specific context to logs
3. Test that your code is logging at the right levels (DEBUG, INFO, WARNING, ERROR)
4. Verify that sensitive data is properly redacted
5. Test both success and error scenarios
6. Check for specific field values in log entries
7. Use specific filtering to find relevant logs in assertions

## Useful Patterns

### Testing with span timing

```python
def test_with_timing(logfire_testing):
    with logfire.span("operation_name") as span:
        # Do something
        time.sleep(0.1)

    # Find the span log
    span_logs = [
        log for log in logfire_testing.logs
        if log.get("span_name") == "operation_name"
    ]

    # Verify timing was logged
    assert span_logs[0]["duration_ms"] >= 100  # at least 100ms
```

### Testing log suppression

```python
def test_log_suppression(logfire_testing):
    # This should not be logged due to scrubbing
    logfire.info("Log with secret", password="secret123")

    # Find logs with password
    password_logs = [
        log for log in logfire_testing.logs
        if "password" in log
    ]

    # Check that password was redacted
    assert password_logs[0]["password"] == "[REDACTED]"
```
