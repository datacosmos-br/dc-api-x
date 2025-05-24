# Testing

> *"Code without tests is broken by design."* ― Jacob Kaplan-Moss
> This guide covers how DCApiX uses pytest for comprehensive testing,
> and provides patterns for extending test coverage across the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [22 - Tech: Developer Tools](22-tech-developer-tools.md) | **23 - Tech: Testing** | [24 - Tech: Structured Logging](24-tech-structured-logging.md) |

---

## 1. Overview

DCApiX uses [pytest](https://docs.pytest.org/) as its testing framework, providing a robust foundation for unit,
integration, and functional testing. This guide provides a comprehensive overview of how pytest is used within the
integration ecosystem, serving as a central reference for developers who want to contribute tests or understand the
testing architecture.

## 2. Core Pytest Features in DCApiX

### 2.1 Test Organization

DCApiX follows these principles for organizing tests:

* **Separate Test Types** – Unit tests, integration tests, and functional tests are clearly separated
* **Directory Structure** – Tests mirror the package structure they're testing
* **Naming Conventions** – Test files are named with `test_` prefix and test functions with `test_` prefix
* **Test Categories** – Tests are categorized using pytest markers like `@pytest.mark.unit`, `@pytest.mark.integration`, etc.

The test directories are organized as follows:

```asciidoc
tests/
├── unit/            # Tests for individual components
├── integration/     # Tests for component interactions
├── functional/      # Tests for complete workflows
├── performance/     # Performance and benchmarking tests
├── security/        # Security and authorization tests
├── conftest.py      # Shared fixtures and configuration
├── factories.py     # Test data factories
└── utils.py         # Test utility functions
```

### AAA Pattern

DCApiX tests follow the Arrange-Act-Assert (AAA) pattern:

```python
def test_example():
    # Arrange - set up test data and conditions
    user = User(name="Test User", email="test@example.com")

    # Act - perform the action being tested
    result = user.validate()

    # Assert - verify the results
    assert result is True
    assert user.is_valid is True
```

### Fixtures

DCApiX leverages pytest fixtures extensively for test setup and teardown:

```python
@pytest.fixture
def mock_client():
    """Create a mock API client for testing."""
    client = ApiClient(
        base_url="https://api.example.com",
        auth_provider=MockAuthProvider(),
    )
    return client

def test_client_operation(mock_client):
    # The mock_client fixture is automatically injected
    response = mock_client.get("users")
    assert response.status_code == 200
```

### Parameterized Tests

For testing multiple variations of the same scenario:

```python
@pytest.mark.parametrize(
    "input_value,expected_result",
    [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
    ],
)
def test_square_function(input_value, expected_result):
    result = square(input_value)
    assert result == expected_result
```

### Mocking

DCApiX uses pytest-mock for creating mock objects and patching functions:

```python
def test_api_call(mocker):
    # Mock an external API call
    mock_response = {"data": [{"id": 1, "name": "Test User"}]}
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    # Call the function that uses the external API
    result = get_users()

    # Verify the mock was called correctly
    mock_get.assert_called_once_with("https://api.example.com/users")
    assert result == mock_response["data"]
```

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Structured logging with Logfire
* [25 - Tech: Typing](25-tech-typing.md) - Type systems and Pydantic
* [27 - Tech: Plugin](27-tech-plugin.md) - Plugin system architecture
