# Developer Tools

> *"Good tools make developers more productive, great tools make them more creative."*
> This guide covers the developer tools integrated into DCApiX that enhance
> productivity, quality, and the overall development experience.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [21 - Tech: Core Libraries](21-tech-core-libraries.md) | **22 - Tech: Developer Tools** | [23 - Tech: Testing](23-tech-testing.md) |

---

## 1. Overview

DCApiX integrates several powerful developer tools to improve the development experience, ensure code quality, and enable robust testing and documentation. This document covers four key tools:

* **Typer** – Command-line interface framework
* **Logfire** – Structured logging and observability
* **Pytest** – Comprehensive testing framework
* **MonkeyType** – Runtime type discovery and annotation

---

## 2. Typer

[Typer](https://typer.tiangolo.com/) is used to build DCApiX's command-line interface, enhanced with [doctyper](https://github.com/audivir/doctyper) for rich documentation generation.

### 2.1 Key Features

* **Type-Driven CLI**: Automatic parameter validation based on Python type hints
* **Command Hierarchy**: Intuitive organization of commands and subcommands
* **Rich Documentation**: Automatic help text generation
* **Parameter Types**: Support for various parameter types (arguments, options, flags)
* **Rich Output**: Colorized output and progress bars

### 2.2 Command Structure

The DCApiX CLI follows a hierarchical structure:

```asciidoc
dcapix
├── config           # Configuration management
│   ├── list         # List available profiles
│   ├── show         # Show configuration for a profile
│   └── test         # Test connection with a profile
├── request          # HTTP request commands
│   ├── get          # Make GET request
│   └── post         # Make POST request
├── schema           # Schema management
│   ├── extract      # Extract schema from API
│   ├── list         # List available schemas
│   └── show         # Show schema details
└── entity           # Entity operations
    ├── list         # List available entities
    └── get          # Retrieve entity data
```

### 2.3 Creating Commands

DCApiX uses doctyper to enhance Typer with Google-style docstring parsing:

```python
@app.command()
def example(
    name: Annotated[str, doctyper.Argument(help="Name argument")],
    count: Annotated[int, doctyper.Option(help="Count of iterations")] = 1,
) -> None:
    """Simple example command.

    Prints a greeting to the specified name a given number of times.

    Args:
        name: The name to greet
        count: Number of times to print the greeting
    """
    for _ in range(count):
        print(f"Hello {name}")
```

### 2.4 Best Practices

* **Use Google-style Docstrings**: Include detailed `Args:` sections for all parameters
* **Follow Command Hierarchy**: Group related commands logically
* **Type Everything**: Use proper type annotations for all parameters
* **Provide Examples**: Include example usages in command help
* **Confirmation for Destructive Actions**: Always confirm before destructive operations

---

## 3. Logfire

[Logfire](https://logfire.dev) provides advanced structured logging, monitoring, and observability in DCApiX.

### 3.1 Key Features

* **Structured Logging**: JSON-based structured log events
* **Context Binding**: Add context to related log entries
* **Pydantic Integration**: Automatic model logging and validation events
* **HTTP Client Integration**: Log requests and responses
* **Sensitive Data Scrubbing**: Automatically redact sensitive information

### 3.2 Basic Usage

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

### 3.3 Context Management

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

### 3.4 Integration with Other Components

```python
# Integration with ApiClient
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

### 3.5 Best Practices

* **Use Structured Logging**: Always use keyword arguments rather than string interpolation
* **Use Appropriate Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL for different severity
* **Context Binding**: Use context to add recurring information
* **Security**: Never log sensitive data; use `scrub_fields` to automatically redact
* **Performance**: For high-volume logs, consider using sampling to reduce overhead

---

## 4. Pytest

[Pytest](https://docs.pytest.org/) is the testing framework used by DCApiX to ensure code quality and reliability.

### 4.1 Test Organization

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

### 4.2 AAA Pattern

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

### 4.3 Fixtures

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

### 4.4 Parameterized Tests

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

### 4.5 Advanced Features

* **Fixture Factories**: Create customizable fixtures
* **Async Testing**: Test asynchronous code with pytest-asyncio
* **Property-Based Testing**: Use hypothesis for property-based testing
* **Visual Testing**: Generate visual reports with pytest-html
* **Parallel Testing**: Run tests in parallel with pytest-xdist

### 4.6 Best Practices

* **Independent Tests**: Each test should be self-contained
* **Clean Fixtures**: Use fixtures for setup and teardown
* **Test Categories**: Use markers to categorize tests
* **Coverage**: Aim for high coverage of critical paths
* **Mocking**: Use mocks for external dependencies
* **Parameterization**: Use parameterized tests for multiple scenarios

---

## 5. MonkeyType

[MonkeyType](https://github.com/Instagram/MonkeyType) is used for runtime type discovery and annotation in DCApiX.

### 5.1 Key Features

* **Type Discovery** – Generate accurate type annotations for existing untyped code
* **Pydantic Integration** – Discover field types for Pydantic models
* **mypy Compatibility** – Improve static type checking coverage with minimal effort
* **Type Validation** – Find type inconsistencies in your codebase

### 5.2 Workflow

The basic workflow for using MonkeyType consists of:

1. **Collection**: Run tests with MonkeyType to collect runtime type information
2. **Discovery**: List modules that have collected type information
3. **Application**: Apply collected types to specific modules
4. **Refinement**: Manually review and refine the types if necessary
5. **Verification**: Verify type consistency with mypy

### 5.3 Basic Usage

DCApiX includes several Makefile targets that simplify MonkeyType usage:

```bash
# Run all tests with MonkeyType to collect type information
make monkeytype-run

# List modules with collected type information
make monkeytype-list

# Apply types to a specific module
make monkeytype-apply MODULE=dc_api_x.config

# Verify types with mypy
make monkeytype-mypy MODULE=dc_api_x.config
```

### 5.4 Converting to Pydantic Models

MonkeyType generates standard Python type annotations that need to be converted to Pydantic field definitions:

#### Original Class

```python
class Config:
    def __init__(self, api_url, timeout=None):
        self.api_url = api_url
        self.timeout = timeout or 30
```

#### After MonkeyType

```python
class Config:
    def __init__(self, api_url: str, timeout: Optional[int] = None) -> None:
        self.api_url = api_url
        self.timeout = timeout or 30
```

#### Converted to Pydantic

```python
class Config(BaseModel):
    api_url: str
    timeout: Optional[int] = 30
```

### 5.5 Best Practices

* **Run with Comprehensive Tests**: Ensure good test coverage for accurate type collection
* **Review Generated Types**: MonkeyType can only detect types used in tests
* **Refine Complex Types**: Generic types, unions, and other complex types may need manual adjustment
* **Verify with mypy**: Always check the applied types with mypy

---

## 6. Integration and Workflow

These developer tools work together to provide a comprehensive development workflow:

1. **Design and Document**: Define API contracts with Pydantic models
2. **Implement CLI**: Build user-friendly interfaces with Typer
3. **Add Logging**: Instrument code with Logfire for observability
4. **Write Tests**: Create comprehensive test suites with Pytest
5. **Discover Types**: Use MonkeyType to enhance type annotations
6. **Validate Types**: Verify type consistency with mypy

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries like Pydantic and Pluggy
* [23 - Tech: Testing](23-tech-testing.md) - Detailed testing guide
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Detailed logging guide
* [25 - Tech: Typing](25-tech-typing.md) - Advanced typing and Pydantic usage
* [26 - Tech: CLI](26-tech-cli.md) - Detailed CLI implementation guide
