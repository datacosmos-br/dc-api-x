# Code Quality Guidelines

This document outlines the coding standards, tools, and practices used in dc-api-x to maintain high code quality.

## Coding Standards

### Style Guides

- **PEP 8**: We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style, with slight modifications indicated in our configuration files.
- **Google Python Style Guide**: For docstrings and more detailed conventions, we follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

### Documentation Standards

- All public modules, classes, methods, and functions must have docstrings.
- We use Google-style docstrings for all documentation.
- Type hints must be used for all function parameters and return values.

## Automated Code Quality Workflow

We've implemented an automated workflow to maintain high code quality standards. This workflow consists of several commands that can be run individually or as part of a continuous cycle.

### Makefile Commands

The project includes the following Makefile commands for code quality:

```bash
# Run all linting checks (non-blocking)
make lint

# Format code with black and isort
make format

# Fix lint issues automatically
make lint-fix

# Run security checks
make security

# Run all formatting and auto-fixes at once
make fix

# Generate detailed lint reports
make lint-report

# Generate lint statistics
make lint-stats
```

### Continuous Linting and Fixing Workflow

For efficient development, it's recommended to run the following cycle:

1. Write code
2. Run `make lint` to check for issues
3. Run `make lint-fix` to automatically fix the issues
4. Run `make format` to ensure consistent formatting
5. Repeat as necessary

The script in `scripts/auto_lint_fix.sh` automates this workflow by running multiple iterations of linting and fixing until all issues are resolved or a maximum number of attempts is reached.

#### Usage

```bash
# Run from project root
./scripts/auto_lint_fix.sh
```

This script:

1. Runs `make lint` to check for issues
2. If issues are found, runs `make lint-fix` and `make format`
3. Repeats the process until no issues are found or max attempts reached
4. Provides detailed output on progress and remaining issues

### Benefits of Automated Quality Workflow

- **Consistency**: Ensures all code follows the same style guidelines
- **Efficiency**: Automatically fixes common issues without manual intervention
- **Incremental Improvement**: Gradually improves code quality with each run
- **Focus on Logic**: Lets developers focus on business logic rather than style

## Linting and Code Quality Tools

We use a comprehensive set of linting and code quality tools to ensure our code meets high standards:

### Primary Tools

1. **Black**: Automatic code formatter that ensures consistent code style.
   - Configuration: `pyproject.toml` (section [tool.black])
   - Run with: `make format` or `make lint-fix-black`

2. **Ruff**: Fast Python linter that combines multiple linting tools into one.
   - Configuration: `pyproject.toml` (section [tool.ruff])
   - Run with: `make lint` or `make lint-fix`

3. **isort**: Sorts imports alphabetically and automatically separates them into sections.
   - Configuration: `pyproject.toml` (section [tool.isort])
   - Run with: `make format` or `make lint-fix-imports`

4. **Mypy**: Static type checker for Python.
   - Configuration: `pyproject.toml` (section [tool.mypy])
   - Run with: `make lint`

5. **Bandit**: Security-focused linter that looks for common security issues.
   - Configuration: `pyproject.toml` (section [tool.bandit])
   - Run with: `make security`

## Common Linting Issues and Solutions

### Magic Values (PLR2004)

**Issue**: Using literal values directly in comparisons.

```python
# ❌ Bad practice
if status_code == 200:  # Using magic value 200
    return "Success"

# ✅ Good practice
HTTP_OK = 200
if status_code == HTTP_OK:
    return "Success"
```

### Unused Arguments (ARG002)

**Issue**: Function parameters that aren't used in the body.

```python
# ❌ Bad practice
def process_data(data, options):  # options is unused
    return transform(data)

# ✅ Good practice (Option 1: prefix with underscore)
def process_data(data, _options):
    return transform(data)

# ✅ Good practice (Option 2: remove if not needed)
def process_data(data):
    return transform(data)
```

### Complex Expressions (WPS221)

**Issue**: Expressions with too many operations or conditions.

```python
# ❌ Bad practice
result = [x for x in items if x > 10 and x % 2 == 0 and is_valid(x)]

# ✅ Good practice
def is_valid_item(x):
    return x > 10 and x % 2 == 0 and is_valid(x)

result = [x for x in items if is_valid_item(x)]
```

### Too Many Arguments (PLR0913)

**Issue**: Functions with too many arguments are difficult to use and test.

```python
# ❌ Bad practice
def create_connection(host, port, user, password, database, timeout, retry, ssl):
    # Implementation
    pass

# ✅ Good practice
@dataclass
class ConnectionConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    timeout: int = 30
    retry: bool = True
    ssl: bool = False

def create_connection(config: ConnectionConfig):
    # Implementation
    pass
```

### Missing Trailing Commas (COM812)

**Issue**: Missing trailing commas in multi-line collections can cause unnecessary merge conflicts.

```python
# ❌ Bad practice
items = [
    "item1",
    "item2",
    "item3"  # Missing trailing comma
]

# ✅ Good practice
items = [
    "item1",
    "item2",
    "item3",  # Trailing comma included
]
```

### Nested If Statements (SIM102)

**Issue**: Nested if statements that can be collapsed.

```python
# ❌ Bad practice
if condition_a:
    if condition_b:
        do_something()

# ✅ Good practice
if condition_a and condition_b:
    do_something()
```

### Long Exception Messages (TRY003)

**Issue**: Long exception messages outside the exception class.

```python
# ❌ Bad practice
raise ValueError("This is a very long error message explaining in great detail what went wrong")

# ✅ Good practice
class InvalidConfigurationError(ValueError):
    """Raised when the configuration is invalid."""
    pass

raise InvalidConfigurationError("Required parameter missing")
```

### Blind Exception Catching (BLE001)

**Issue**: Catching exceptions without specifying which ones.

```python
# ❌ Bad practice
try:
    do_something()
except Exception:  # Catches all exceptions
    handle_error()

# ✅ Good practice
try:
    do_something()
except (ValueError, KeyError, TypeError):  # Catches only specific exceptions
    handle_error()
```

### Logging in Exception Handlers (TRY400)

**Issue**: Using logging.error in exception handlers.

```python
# ❌ Bad practice
try:
    authenticate()
except AuthError as e:
    logging.error(f"Authentication failed: {e}")

# ✅ Good practice
try:
    authenticate()
except AuthError:
    logging.exception("Authentication failed")  # Automatically includes traceback
```

### Too Many Local Variables (WPS210)

**Issue**: Functions with many local variables are difficult to understand.

```python
# ❌ Bad practice
def process_data(data):
    temp1 = data[0]
    temp2 = data[1]
    result1 = temp1 * 2
    result2 = temp2 * 3
    combined = result1 + result2
    formatted = f"{combined:.2f}"
    validated = validate(formatted)
    normalized = normalize(validated)
    return normalized

# ✅ Good practice
def multiply_data(data):
    return data[0] * 2, data[1] * 3

def process_data(data):
    result1, result2 = multiply_data(data)
    combined = result1 + result2
    return post_process(combined)

def post_process(value):
    formatted = f"{value:.2f}"
    return normalize(validate(formatted))
```

### Too Many Imports (WPS201)

**Issue**: Modules with many imports are difficult to maintain.

```python
# ❌ Bad practice
import os
import sys
import json
import time
import datetime
import requests
import pandas
# ... many more imports

# ✅ Good practice
# core.py
from typing import Dict, List
import json
import os
import sys

# network.py
import requests
from requests.exceptions import RequestException

# analysis.py
import pandas as pd
import numpy as np
```

### Inconsistent Return Statements (RET505)

**Issue**: Different return statement styles within the same function.

```python
# ❌ Bad practice
def process_value(value):
    if value < 0:
        return
    if value > 100:
        return None
    processed = transform(value)
    return processed

# ✅ Good practice
def process_value(value):
    if value < 0 or value > 100:
        return None
    return transform(value)
```

### Implicit String Concatenation (ISC001)

**Issue**: Relying on Python's implicit string concatenation.

```python
# ❌ Bad practice
message = "This is a very long message "
         "that spans multiple lines"

# ✅ Good practice
message = (
    "This is a very long message "
    "that spans multiple lines"
)

# ✅ Better practice
message = "\n".join([
    "This is a very long message",
    "that spans multiple lines",
])
```

### Mutable Default Arguments (B006)

**Issue**: Using mutable objects as default arguments.

```python
# ❌ Bad practice
def process_items(items=[]):  # Default list is mutable and shared
    items.append('new')
    return items

# ✅ Good practice
def process_items(items=None):
    if items is None:
        items = []
    items.append('new')
    return items
```

## PEP 585 Type Annotation Guidelines

Starting with Python 3.10, we prefer using built-in container types directly as generic annotations, as defined in PEP 585:

```python
# ❌ Avoid: importing from typing for built-in containers
from typing import Dict, List, Optional, Set, Tuple

def old_style(users: List[Dict[str, str]], active: Optional[bool] = None) -> Tuple[int, Set[str]]:
    pass

# ✅ Prefer: built-in types as generic containers (PEP 585, Python 3.10+)
def modern_style(users: list[dict[str, str]], active: bool | None = None) -> tuple[int, set[str]]:
    pass
```

## Common Mypy Errors and How to Fix Them

The project uses `mypy` with `--strict` mode to ensure robust type safety. This section covers the most common mypy errors and how to fix them.

### 1. Missing Return Type Annotations [no-untyped-def]

This is one of the most common errors in the project. All functions must have explicit return type annotations, even if they don't return a value.

```python
# ❌ Error: Function is missing a return type annotation [no-untyped-def]
def process_data(data):
    return data.get("result")

# ✅ Fix: Add explicit return type annotation
def process_data(data: dict[str, Any]) -> str | None:
    return data.get("result")

# ✅ For functions that don't return anything, use -> None
def log_action(message: str) -> None:
    logger.info(message)
```

For test functions, even though they're not part of the production code, they should still have return type annotations:

```python
# ❌ Error in tests
def test_api_client():
    client = ApiClient()
    assert client.is_connected() is False

# ✅ Fix for test functions
def test_api_client() -> None:
    client = ApiClient()
    assert client.is_connected() is False
```

### 2. Missing Type Parameters for Generic Types [type-arg]

When using generic types like `list`, `dict`, `Callable`, etc., you must specify the type parameters:

```python
# ❌ Error: Missing type parameters for generic type "list" [type-arg]
def get_items() -> list:
    return ["item1", "item2"]

# ✅ Fix: Add type parameters for generics
def get_items() -> list[str]:
    return ["item1", "item2"]

# More examples
items: dict = {}  # ❌ Error
items: dict[str, int] = {}  # ✅ Fix

callback: Callable = lambda x: x  # ❌ Error
callback: Callable[[int], int] = lambda x: x  # ✅ Fix

# For BasePaginator, Entity, and other generic classes
paginator: BasePaginator = BasePaginator()  # ❌ Error
paginator: BasePaginator[UserModel] = BasePaginator[UserModel]()  # ✅ Fix
```

### 3. Union Type Attribute Access [union-attr]

When a variable can be `None`, you need to check for `None` before accessing attributes:

```python
# ❌ Error: Item "None" of "Error | None" has no attribute "detail" [union-attr]
def get_error_detail(error: Error | None) -> str:
    return error.detail  # Error: could be None

# ✅ Fix: Check for None before accessing attributes
def get_error_detail(error: Error | None) -> str | None:
    if error is None:
        return None
    return error.detail

# ✅ Alternative: Use assertion if None is not expected
def get_error_detail(error: Error | None) -> str:
    assert error is not None, "Error must not be None"
    return error.detail
```

### 4. Incompatible Return Value Type [return-value]

Ensure the function's return values match the declared return type:

```python
# ❌ Error: Incompatible return value type (got "str | None", expected "str")
def get_username() -> str:
    username = get_value_from_config()  # Returns str | None
    return username

# ✅ Fix: Ensure the return type matches or handle possible None
def get_username() -> str:
    username = get_value_from_config()
    if username is None:
        return "default"  # Default value when None
    return username

# ✅ Alternative: Change the return type to match
def get_username() -> str | None:
    username = get_value_from_config()
    return username
```

### 5. Returning Any from Function with Explicit Return Type [no-any-return]

```python
# ❌ Error: Returning Any from function declared to return "dict[str, Any]"
def get_config() -> dict[str, Any]:
    return json.loads(data)  # Returns Any

# ✅ Fix: Use type assertion to enforce return type
def get_config() -> dict[str, Any]:
    result = json.loads(data)
    assert isinstance(result, dict), "Expected a dictionary"
    return result

# ✅ Alternative: Use TypedDict for more precise typing
class ConfigDict(TypedDict):
    host: str
    port: int
    debug: bool

def get_config() -> ConfigDict:
    result = json.loads(data)
    return cast(ConfigDict, result)
```

### 6. Incompatible Types in Assignment [assignment]

Make sure the assigned value matches the variable's type:

```python
# ❌ Error: Incompatible types in assignment (expression has type "str", variable has type "SecretStr")
password: SecretStr = "mypassword"  # Type error

# ✅ Fix: Use proper constructors for special types
from pydantic import SecretStr
password: SecretStr = SecretStr("mypassword")

# Another example with None
data: list[str] = None  # ❌ Error
data: list[str] | None = None  # ✅ Fix
```

### 7. Incorrect Arguments to Functions [call-arg]

```python
# ❌ Error: Unexpected keyword argument "filters" for "list" of "BaseEntity"
results = entity.list(filters={"name": "test"})

# ✅ Fix: Check the method signature and use correct parameters
# If the method signature is: def list(self, filter_by: dict | None = None) -> list[T]:
results = entity.list(filter_by={"name": "test"})
```

### 8. Missing Named Arguments [call-arg]

```python
# ❌ Error: Missing named argument "url" for "Config"
config = Config()  # Missing required arguments

# ✅ Fix: Provide all required arguments
config = Config(
    url="https://api.example.com",
    username="user",
    password=SecretStr("pass"),
    timeout=30,
    verify_ssl=True,
    # Add all other required parameters...
)
```

### 9. Cannot Find Implementation or Library Stub [import-not-found]

```python
# ❌ Error: Cannot find implementation or library stub for module named "logfire"
import logfire

# ✅ Fix options:
# 1. Install missing package: pip install logfire
# 2. Install type stubs: pip install types-logfire
# 3. Create a stub file if needed:

# In a file named logfire.pyi (in project or typings directory):
class Logger:
    def __init__(self, name: str) -> None: ...
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
```

### 10. Type Variable Issues [type-var]

```python
# ❌ Error: Type argument "T" of "BasePaginator" must be a subtype of "BaseModel"
class BasePaginator(Generic[T]):
    # Type constrained to BaseModel

# ✅ Fix: Add proper type variable bounds
T = TypeVar('T', bound=BaseModel)

class BasePaginator(Generic[T]):
    # Now T is properly constrained to BaseModel
```

### 11. Method Override Signature Incompatibility [override]

```python
# ❌ Error: Signature of "process_request" incompatible with supertype "LoggingHook"
# Superclass:
#   def process_request(self, method: str, url: str, kwargs: dict[str, Any]) -> dict[str, Any]
# Subclass:
#   def process_request(self, request: Any) -> Any

# ✅ Fix: Match the signature of the parent class method
class MyLoggingHook(LoggingHook):
    def process_request(
        self, method: str, url: str, kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        # Implementation
        return kwargs
```

### 12. Unused Type Ignore Comments [unused-ignore]

```python
# ❌ Error: Unused "type: ignore" comment
def format_string(value: str) -> str:  # type: ignore
    return value.strip()

# ✅ Fix: Remove unused type ignore comments
def format_string(value: str) -> str:
    return value.strip()
```

### 13. Module Has No Attribute [attr-defined]

```python
# ❌ Error: Module has no attribute "critical"
import logfire
logfire.critical("Error message")

# ✅ Fix: Check the module's actual API
import logfire
logger = logfire.get_logger(__name__)
logger.critical("Error message")
```

### 14. Cannot Instantiate Abstract Class [abstract]

```python
# ❌ Error: Cannot instantiate abstract class "HttpAdapter" with abstract attributes
adapter = HttpAdapter(timeout=30)

# ✅ Fix: Implement all abstract methods or use a concrete subclass
class ConcreteHttpAdapter(HttpAdapter):
    def connect(self) -> None:
        # Implementation
        pass
    
    def disconnect(self) -> None:
        # Implementation
        pass
    
    # Implement all other abstract methods...

adapter = ConcreteHttpAdapter(timeout=30)
```

### Best Practices for Working with Mypy

1. **Start gradually**: If adding types to a large codebase, consider using `# type: ignore` temporarily and fix errors incrementally.

2. **Use reveal_type()**: For debugging type issues, add `reveal_type(variable)` to see what mypy thinks the type is.

3. **Add stronger assertions**: Sometimes mypy needs help understanding flow control:

   ```python
   data = get_data()
   if isinstance(data, dict):
       # mypy now knows data is a dict in this branch
       process_dict(data)
   ```

4. **Avoid using Any**: While `Any` can silence type errors, it defeats the purpose of static typing. Use it only as a last resort.

5. **Handle None cases explicitly**: Always consider if a value can be `None` and handle it appropriately.

6. **Use TypedDict for dictionary shapes**: Instead of `dict[str, Any]`, use `TypedDict` to describe the expected structure.

7. **Use Literal for constrained strings**: For values that can only be certain strings, use `Literal`:

   ```python
   from typing import Literal
   
   HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
   
   def make_request(method: HttpMethod, url: str) -> None:
       # Only accepts specific HTTP methods
       pass
   ```

8. **Create Protocol classes for duck typing**: Use `Protocol` to define interface requirements without inheritance:

   ```python
   from typing import Protocol
   
   class Loggable(Protocol):
       def log(self, message: str) -> None: ...
   
   def process_with_logging(item: Loggable) -> None:
       item.log("Processing started")
   ```

9. **Keep types in sync with Pydantic models**: Ensure your type annotations match your Pydantic model definitions.

10. **Use overload for functions with multiple signatures**: For functions that can accept different argument types:

    ```python
    from typing import overload
    
    @overload
    def process_input(data: str) -> str: ...
    
    @overload
    def process_input(data: bytes) -> bytes: ...
    
    def process_input(data: str | bytes) -> str | bytes:
        if isinstance(data, str):
            return data.upper()
        else:
            return data.upper()
    ```

### Fixing Common Test Function Errors

Test files should follow the same type annotation rules as production code. Here are common patterns:

```python
# Test functions should have -> None return type
def test_something() -> None:
    # Test implementation
    pass

# Test fixtures should specify their return type
@pytest.fixture
def mock_client() -> ApiClient:
    return MockApiClient()

# Parametrized tests should have properly typed parameters
@pytest.mark.parametrize("input_val,expected", [
    (1, "one"),
    (2, "two"),
])
def test_with_params(input_val: int, expected: str) -> None:
    assert convert(input_val) == expected
```

### Handling Third-Party Libraries

When working with third-party libraries without type stubs:

1. **Install type stubs if available**:

   ```bash
   pip install types-requests types-jwt types-cryptography
   ```

2. **Create stub files for uncommon libraries**:

   ```python
   # In a file named thirdparty.pyi
   def some_function(arg1: str, arg2: int) -> bool: ...
   ```

3. **Use strategic type ignores for third-party issues**:

   ```python
   from problematic_lib import function  # type: ignore[import]
   result = function()  # type: ignore[no-any-return]
   ```

## Testing Guidelines

- Minimum 90% code coverage required for all PRs
- Each new feature must include corresponding tests
- Tests should be independent and not rely on external systems
- Use pytest fixtures to reduce test setup duplication
- Mock external dependencies for unit tests

```python
# ❌ Bad practice: Tests with external dependencies
def test_api_fetch():
    # Makes real HTTP call
    result = api.fetch_data("https://api.example.com/data")
    assert result["status"] == "success"

# ✅ Good practice: Mocking external dependencies
@pytest.mark.parametrize("mock_response", [
    {"status": "success", "data": [1, 2, 3]},
    {"status": "error", "message": "Not found"}
])
def test_api_fetch(mocker, mock_response):
    # Mock the HTTP call
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = mock_response
    
    result = api.fetch_data("https://api.example.com/data")
    assert result["status"] == mock_response["status"]
```

### Test Organization

Tests should be organized to mirror the package structure:

```asciidoc
src/
  dc_api_x/
    client.py
    models.py
tests/
  test_client.py  # Tests for client.py
  test_models.py  # Tests for models.py
```

### Pytest Best Practices

- Use descriptive test names that explain what's being tested
- Use `parametrize` for testing multiple inputs
- Organize fixtures by scope (function, module, session)
- Use markers to categorize tests (unit, integration, slow)

```python
@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double_function(input_value, expected):
    """Test that double() multiplies values by 2."""
    assert double(input_value) == expected
```

## Running Lint Checks

You can run lint checks using the following commands:

```bash
# Run all lint checks
make lint

# Run only wemake-python-styleguide checks
make lint-wps

# Get lint statistics
make lint-stats

# Auto-fix lint issues
make lint-fix

# Run full lint fix including security checks
make lint-fix-all
```

## Integration with CI/CD

Lint checks are automatically run in our CI/CD pipeline to ensure code quality standards are met before merging:

- GitHub Actions workflow: `.github/workflows/lint.yml`
- Pre-commit hooks: `.pre-commit-config.yaml`

## Pre-commit Hooks

We use pre-commit hooks to automatically check code quality before commits. To set up:

```bash
# Install pre-commit
poetry run pre-commit install

# Run hooks manually on all files
poetry run pre-commit run --all-files
```

This will run all configured hooks from `.pre-commit-config.yaml` when you commit code.

## Creating Clean, Maintainable Code

Beyond passing linters, aim for:

1. **Clear Intent**: Code should clearly express its purpose.
2. **Single Responsibility**: Functions and classes should do one thing well.
3. **DRY (Don't Repeat Yourself)**: Avoid duplicating code.
4. **Composition Over Inheritance**: Prefer composition patterns to deep inheritance hierarchies.
5. **Testability**: Write code that's easy to test.
6. **Fail Fast**: Validate inputs early and raise clear exceptions.

### Function Design Principles

1. **Small and Focused**: Functions should be short (< 30 lines) and focused on a single task.
2. **Appropriate Abstraction**: Functions should operate at a consistent level of abstraction.
3. **Descriptive Names**: Function names should clearly describe what the function does.
4. **Minimal Side Effects**: Functions should minimize side effects and be as pure as possible.

```python
# ❌ Bad practice: Function does too many things
def process_order(order_id):
    # Load data
    order = database.get_order(order_id)
    customer = database.get_customer(order.customer_id)
    
    # Validate
    if not order.items:
        raise ValueError("Order has no items")
    
    # Calculate
    total = sum(item.price for item in order.items)
    tax = total * 0.07
    
    # Update database
    database.update_order(order_id, {"total": total, "tax": tax})
    
    # Send notification
    email.send(customer.email, "Order processed", f"Your order total is ${total + tax}")
    
    return total + tax

# ✅ Good practice: Single responsibility functions
def get_order_details(order_id):
    """Load order and customer information."""
    order = database.get_order(order_id)
    customer = database.get_customer(order.customer_id)
    return order, customer

def validate_order(order):
    """Ensure order is valid."""
    if not order.items:
        raise ValueError("Order has no items")

def calculate_order_totals(order):
    """Calculate order totals and tax."""
    total = sum(item.price for item in order.items)
    tax = total * 0.07
    return total, tax

def update_order_in_database(order_id, total, tax):
    """Save updated order information."""
    database.update_order(order_id, {"total": total, "tax": tax})

def notify_customer(customer, total, tax):
    """Send order confirmation to customer."""
    email.send(
        customer.email, 
        "Order processed", 
        f"Your order total is ${total + tax}"
    )

def process_order(order_id):
    """Process an order end-to-end."""
    order, customer = get_order_details(order_id)
    validate_order(order)
    total, tax = calculate_order_totals(order)
    update_order_in_database(order_id, total, tax)
    notify_customer(customer, total, tax)
    return total + tax
```

## Performance Guidelines

- Avoid unnecessary computation in critical paths
- Profile before optimizing
- Document performance characteristics of public APIs
- Consider asyncio for I/O-bound operations

```python
# ❌ Bad practice: Redundant computation in loop
def process_items(items):
    results = []
    for item in items:
        # Recalculates the same thing for each item
        expensive_calculation = calculate_complex_value()
        results.append(transform(item, expensive_calculation))
    return results

# ✅ Good practice: Calculate once, reuse
def process_items(items):
    # Calculate once outside the loop
    expensive_calculation = calculate_complex_value()
    return [transform(item, expensive_calculation) for item in items]
```

### Common Performance Optimizations

1. **Use appropriate data structures**:
   - Lists for ordered sequences
   - Sets for unique values and fast lookups
   - Dictionaries for key-value mappings

2. **Reduce database calls**:
   - Batch queries where possible
   - Use joins instead of multiple queries
   - Cache frequently accessed data

3. **Optimize I/O operations**:
   - Use async for I/O-bound operations
   - Batch file operations
   - Stream large files instead of loading into memory

4. **Optimize expensive operations**:
   - Cache results of expensive calculations
   - Use generators for large data processing
   - Consider numpy/pandas for numerical operations

## Security Practices

- Never hard-code credentials or sensitive information
- Always validate and sanitize user inputs
- Use SecretStr for password fields
- Apply proper access controls
- Keep dependencies updated

```python
# ❌ Bad practice: Hard-coded credentials
API_KEY = "1234567890abcdef"
db_connection = connect("localhost", "root", "password")

# ✅ Good practice: Environment variables or secure configuration
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise EnvironmentError("API_KEY environment variable is not set")

db_config = config.get_database_config()  # From secure source
db_connection = connect(**db_config)
```

## Resolving Lint Warnings

When facing lint warnings, prefer making the code better rather than adding ignores:

1. First, understand why the warning exists
2. Refactor to address the underlying issue
3. Only add ignores (`# noqa: CODE`) when refactoring isn't practical

Seek guidance if you're unsure about the best approach to resolve a linting issue.

## Common Ignores and When to Use Them

| Code | Description | When to Ignore |
|------|-------------|----------------|
| WPS433 | Found nested import | In `__init__.py` files that re-export symbols |
| ARG002 | Unused method argument | In interface implementations or hooks where parameters are part of the API |
| PLR2004 | Magic value used in comparison | In test files, but prefer constants in production code |
| WPS110 | Wrong variable name | For domain-specific names that make sense in context |
| WPS202 | Found too many module members | In module APIs that intentionally expose many symbols |
| WPS230 | Found too many public instance attributes | In data container classes |

## Documentation Best Practices

All documentation should follow these principles:

1. **Clarity**: Be concise and unambiguous
2. **Completeness**: Document all public APIs
3. **Examples**: Include usage examples for complex functionality
4. **Consistency**: Use consistent terminology and formatting

### Docstring Format

```python
def fetch_user_data(user_id: int, include_history: bool = False) -> dict:
    """Fetch user data from the API.
    
    Args:
        user_id: The unique identifier of the user
        include_history: Whether to include user history in the response
        
    Returns:
        A dictionary containing user information
        
    Raises:
        ValueError: If user_id is negative
        ApiError: If the API request fails
        
    Example:
        >>> fetch_user_data(42)
        {'id': 42, 'name': 'John Doe', 'email': 'john@example.com'}
    """
```

## Continuous Improvement

Code quality is an ongoing process. We continuously improve our standards by:

1. **Regular reviews**: Code reviews are mandatory for all changes
2. **Retrospectives**: Regular team discussions about code quality challenges
3. **Benchmarking**: Comparing our practices against industry standards
4. **Automation**: Increasing our use of automated tools and checks
5. **Training**: Ongoing education about best practices

## Conclusion

Following these code quality guidelines ensures that dc-api-x remains maintainable, reliable, and performant. When in doubt, prioritize readability and simplicity over cleverness, and always consider the developer who will read your code in the future (which might be you!).
