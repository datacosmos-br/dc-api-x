# Pytest Guide for DCApiX

## Introduction

DCApiX uses [pytest](https://docs.pytest.org/en/8.3.x/) as its testing framework, providing a robust foundation for unit, integration, and functional testing. This guide provides a comprehensive overview of how pytest is used within DCApiX, serving as a central reference for developers who want to contribute tests or understand the testing architecture.

## Core Pytest Features in DCApiX

### Test Organization

DCApiX follows these principles for organizing tests:

- **Separate Test Types**: Unit tests, integration tests, and functional tests are clearly separated
- **Directory Structure**: Tests mirror the package structure they're testing
- **Naming Conventions**: Test files are prefixed with `test_` and test functions start with `test_`
- **Fixtures**: Reusable test components in `conftest.py` files

### Fixture System

DCApiX leverages pytest's powerful fixture system for test setup and teardown:

- **Scoped Fixtures**: Different lifetimes (function, class, module, session)
- **Factory Fixtures**: Generate test data dynamically
- **Autouse Fixtures**: Automatic setup/teardown without explicit declaration
- **Parameterized Fixtures**: Run the same test with different inputs

### Plugin Integration

DCApiX extends pytest with useful plugins:

- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-asyncio**: Async test support
- **pytest-xdist**: Parallel test execution

## Basic Usage in DCApiX

### Running Tests

Basic pytest commands used in DCApiX:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test function
pytest tests/unit/test_client.py::test_get_request

# Run with verbose output
pytest -v

# Run with code coverage
pytest --cov=dc_api_x
```

### Writing a Simple Test

Here's a basic test for the ApiClient class:

```python
# tests/unit/test_client.py
import pytest
from dc_api_x import ApiClient
from dc_api_x.testing import MockAdapter

def test_api_client_get():
    """Test that the ApiClient can make GET requests."""
    # Create a mock adapter with predefined responses
    mock_adapter = MockAdapter(responses={
        ("GET", "/users"): {"data": [{"id": 1, "name": "Test User"}]}
    })
    
    # Create client with mock adapter
    client = ApiClient(url="https://example.com", adapter=mock_adapter)
    
    # Make request
    response = client.get("users")
    
    # Check response
    assert response.success is True
    assert response.data[0]["name"] == "Test User"
```

### Using Fixtures

Fixtures help set up test dependencies:

```python
# tests/conftest.py
import pytest
from dc_api_x import ApiClient
from dc_api_x.testing import MockAdapter

@pytest.fixture
def mock_adapter():
    """Fixture providing a pre-configured mock adapter."""
    return MockAdapter(responses={
        ("GET", "/users"): {"data": [{"id": 1, "name": "Test User"}]},
        ("POST", "/users"): {"success": True, "id": 2},
    })

@pytest.fixture
def api_client(mock_adapter):
    """Fixture providing a pre-configured API client."""
    return ApiClient(url="https://example.com", adapter=mock_adapter)

# tests/unit/test_client.py
def test_get_users(api_client):
    """Test getting users using fixtures."""
    response = api_client.get("users")
    assert response.success is True
    assert len(response.data) == 1
    
def test_create_user(api_client):
    """Test creating a user using fixtures."""
    response = api_client.post("users", json={"name": "New User"})
    assert response.success is True
    assert response.id == 2
```

## Advanced Features

### Parameterized Tests

Run the same test with different inputs:

```python
import pytest
from dc_api_x.utils import format_url

@pytest.mark.parametrize("base,path,expected", [
    ("https://example.com", "users", "https://example.com/users"),
    ("https://example.com/", "users", "https://example.com/users"),
    ("https://example.com", "/users", "https://example.com/users"),
    ("https://example.com/", "/users", "https://example.com/users"),
])
def test_format_url(base, path, expected):
    """Test URL formatting with different inputs."""
    assert format_url(base, path) == expected
```

### Testing Exceptions

Verify that code raises expected exceptions:

```python
import pytest
from dc_api_x import ApiClient, ApiError

def test_connection_error():
    """Test that connection errors are properly handled."""
    # Create client with non-existent URL
    client = ApiClient(url="https://non-existent-url.example")
    
    # Verify exception is raised with appropriate message
    with pytest.raises(ApiError) as excinfo:
        client.get("users")
    
    assert "Connection error" in str(excinfo.value)
```

### Mock Testing

Use mocking to isolate units:

```python
def test_retry_mechanism(mocker):
    """Test retry mechanism using mocks."""
    # Mock the request method
    mock_request = mocker.patch("dc_api_x.client.HttpAdapter.request")
    
    # Configure mock to fail twice then succeed
    mock_request.side_effect = [
        ApiError("Connection refused"),  # First attempt fails
        ApiError("Timeout"),             # Second attempt fails
        {"success": True, "data": []}    # Third attempt succeeds
    ]
    
    # Create client with retry configuration
    client = ApiClient(
        url="https://example.com",
        max_retries=3,
        retry_backoff=0.1
    )
    
    # Make request - should succeed after retries
    response = client.get("users")
    
    # Verify the request was called 3 times
    assert mock_request.call_count == 3
    assert response.success is True
```

### Async Testing

Test asynchronous code:

```python
import pytest
import asyncio
from dc_api_x import ApiAsyncClient

@pytest.mark.asyncio
async def test_async_client():
    """Test async client operations."""
    # Create async client with mock adapter
    client = ApiAsyncClient(url="https://example.com")
    
    # Mock the _request method to return test data
    client._request = asyncio.coroutine(lambda method, path, **kwargs: {
        "success": True,
        "data": [{"id": 1, "name": "Async User"}]
    })
    
    # Make async request
    response = await client.get("users")
    
    # Check response
    assert response["success"] is True
    assert response["data"][0]["name"] == "Async User"
```

### Testing CLI Commands

Test Typer CLI commands:

```python
from typer.testing import CliRunner
from dc_api_x.cli import app

def test_cli_config_list():
    """Test the config list command."""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "list"])
    
    # Check exit code
    assert result.exit_code == 0
    
    # Check output contains expected text
    assert "Available profiles" in result.stdout
```

## Integration with Other Tools

### Coverage Reporting

Generate code coverage reports:

```bash
# Run tests with coverage and generate report
pytest --cov=dc_api_x --cov-report=html

# Open the HTML report
open htmlcov/index.html
```

### Continuous Integration

DCApiX runs tests in CI with:

```yaml
- name: Run Tests
  run: |
    pytest --cov=dc_api_x --cov-report=xml
    coverage report --fail-under=90
```

## Testing Strategies in DCApiX

### Unit Testing

Unit tests validate individual components in isolation:

```python
def test_transform_provider_format():
    """Test that TransformProvider correctly formats data."""
    # Create a transform provider with test configuration
    provider = TransformProvider(field_map={"id": "user_id", "name": "user_name"})
    
    # Test data
    input_data = {"id": 123, "name": "Test User"}
    
    # Transform data
    output = provider.transform(input_data)
    
    # Verify transformation
    assert output == {"user_id": 123, "user_name": "Test User"}
```

### Integration Testing

Integration tests verify component interactions:

```python
def test_client_with_real_adapter(real_api_config):
    """Test ApiClient with a real adapter (requires network)."""
    # Skip if integration tests are disabled
    if not real_api_config:
        pytest.skip("Integration tests disabled")
        
    # Create real client using configuration
    client = ApiClient(
        url=real_api_config["url"],
        auth_provider=BasicAuthProvider(
            real_api_config["username"],
            real_api_config["password"]
        )
    )
    
    # Make actual network request
    response = client.get("status")
    
    # Verify real API behavior
    assert response.success is True
    assert "version" in response.data
```

### Functional Testing

Functional tests validate end-to-end workflows:

```python
def test_extract_and_query_workflow(temp_dir):
    """Test extracting schema and using it for queries."""
    # Create API client
    client = ApiClient(url="https://example.com")
    
    # Extract schema to temp directory
    from dc_api_x.schema import SchemaExtractor
    extractor = SchemaExtractor(client)
    extractor.extract_all(output_dir=temp_dir)
    
    # Verify schema files were created
    assert (temp_dir / "user.json").exists()
    
    # Load schema and create entity client
    from dc_api_x.entity import EntityClient
    entity_client = EntityClient(client, schema_dir=temp_dir)
    
    # Mock response for entity request
    client.adapter = MockAdapter(responses={
        ("GET", "/users/123"): {"id": 123, "name": "Test User"}
    })
    
    # Make entity request
    user = entity_client.get("user", 123)
    
    # Verify entity was properly deserialized using schema
    assert user.id == 123
    assert user.name == "Test User"
```

## Best Practices

1. **Test Isolation**: Each test should run independently of others.

2. **Use Fixtures**: Reuse setup/teardown code with fixtures.

3. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification.

4. **Mock External Dependencies**: Use mocks for network, database, etc.

5. **Test Coverage**: Aim for high coverage but focus on critical paths.

6. **Clear Failure Messages**: Use descriptive assertions for clear failure reporting.

7. **Test Edge Cases**: Include error cases, empty inputs, boundary values.

8. **Test Public API**: Focus on testing public interfaces rather than implementation details.

9. **Parameterize Similar Tests**: Use parametrization for similar test cases.

10. **Clean Test Data**: Avoid persistent side effects in tests.

## See Also

- [pytest Documentation](https://docs.pytest.org/en/8.3.x/)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/)
- [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)
- [Typer Testing](https://typer.tiangolo.com/tutorial/testing/)
- [Code Quality Guide](06-code-quality.md)
