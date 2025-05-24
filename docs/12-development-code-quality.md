# Code Quality Guide

> *"Quality is not an act, it is a habit."* — Aristotle
> This guide outlines the coding standards, tools, and practices used in DCApiX
> to maintain high code quality across the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [11 - Development: Contributing](11-development-contributing.md) | **12 - Development: Code Quality** | [13 - Development: Plugin System](13-development-plugin-system.md) |

---

## 1. Introduction

DCApiX maintains a high standard of code quality through a combination of coding standards, automated tools, and best practices. This document serves as a comprehensive guide to these standards and practices.

---

## 2. Coding Standards

### 2.1 Style Guides

* **PEP 8**: We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style, with slight modifications indicated in our configuration files
* **Google Python Style Guide**: For docstrings and more detailed conventions, we follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### 2.2 Documentation Standards

* All public modules, classes, methods, and functions must have docstrings
* We use Google-style docstrings for all documentation
* Type hints must be used for all function parameters and return values

---

## 3. Automated Code Quality Workflow

DCApiX provides an automated workflow to maintain high code quality standards.

### 3.1 Makefile Commands

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

### 3.2 Continuous Linting and Fixing Workflow

For efficient development, follow this workflow:

1. Write code
2. Run `make lint` to check for issues
3. Run `make lint-fix` to automatically fix the issues
4. Run `make format` to ensure consistent formatting
5. Repeat as necessary

The script in `scripts/auto_lint_fix.sh` automates this workflow:

```bash
# Run from project root
./scripts/auto_lint_fix.sh
```

### 3.3 Benefits of Automated Quality Workflow

* **Consistency**: Ensures all code follows the same style guidelines
* **Efficiency**: Automatically fixes common issues without manual intervention
* **Incremental Improvement**: Gradually improves code quality with each run
* **Focus on Logic**: Lets developers focus on business logic rather than style

---

## 4. Linting and Code Quality Tools

We use a comprehensive set of linting and code quality tools:

### 4.1 Primary Tools

1. **Black**: Automatic code formatter that ensures consistent code style
   * Configuration: `pyproject.toml` (section [tool.black])
   * Run with: `make format` or `make lint-fix-black`

2. **Ruff**: Fast Python linter that combines multiple linting tools into one
   * Configuration: `pyproject.toml` (section [tool.ruff])
   * Run with: `make lint` or `make lint-fix`

3. **isort**: Sorts imports alphabetically and automatically separates them into sections
   * Configuration: `pyproject.toml` (section [tool.isort])
   * Run with: `make format` or `make lint-fix-imports`

4. **Mypy**: Static type checker for Python
   * Configuration: `pyproject.toml` (section [tool.mypy])
   * Run with: `make lint`

5. **Bandit**: Security-focused linter that looks for common security issues
   * Configuration: `pyproject.toml` (section [tool.bandit])
   * Run with: `make security`

---

## 5. Common Linting Issues and Solutions

DCApiX's linting configuration catches common issues. Here are some patterns to follow:

### 5.1 Magic Values (PLR2004)

Use named constants instead of literals:

```python
# ✅ Good practice
HTTP_OK = 200
if status_code == HTTP_OK:
    return "Success"
```

### 5.2 Unused Arguments (ARG002)

Prefix unused arguments with underscore:

```python
# ✅ Good practice
def process_data(data, _options):
    return transform(data)
```

### 5.3 Complex Expressions (WPS221)

Extract complex logic into helper functions:

```python
# ✅ Good practice
def is_valid_item(x):
    return x > 10 and x % 2 == 0 and is_valid(x)

result = [x for x in items if is_valid_item(x)]
```

### 5.4 Too Many Arguments (PLR0913)

Use data classes or parameter objects:

```python
# ✅ Good practice
@dataclass
class ConnectionConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    timeout: int = 30

def create_connection(config: ConnectionConfig):
    # Implementation
    pass
```

---

## 6. Modern Python Typing

DCApiX leverages modern Python typing features:

```python
# ✅ PREFER: built-in types as generic containers (PEP 585, Python 3.10+)
def modern_style(users: list[dict[str, str]], active: bool | None = None) -> tuple[int, set[str]]:
    pass
```

### 6.1 Best Practices

* Use built-in types directly for generic annotations (Python 3.10+)
* Prefer `|` union operator over `Union` (PEP 604)
* Reserve `typing` imports for special types without built-in equivalents
* Use type aliases to improve readability: `UserDict = dict[str, str]`

---

## 7. Testing Guidelines

* Minimum 90% code coverage required for all PRs
* Each new feature must include corresponding tests
* Tests should be independent and not rely on external systems
* Use pytest fixtures to reduce test setup duplication
* Mock external dependencies for unit tests

See [23 - Tech: Testing](23-tech-testing.md) for detailed testing guidelines.

---

## 8. Performance Guidelines

* Avoid unnecessary computation in critical paths
* Profile before optimizing
* Document performance characteristics of public APIs
* Consider asyncio for I/O-bound operations

---

## 9. Security Practices

* Never hard-code credentials or sensitive information
* Always validate and sanitize user inputs
* Use SecretStr for password fields
* Apply proper access controls
* Keep dependencies updated

---

## 10. Documentation Best Practices

All documentation should follow these principles:

1. **Clarity**: Be concise and unambiguous
2. **Completeness**: Document all public APIs
3. **Examples**: Include usage examples for complex functionality
4. **Consistency**: Use consistent terminology and formatting

### 10.1 Docstring Format

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

---

## 11. Continuous Improvement

Code quality is an ongoing process. We continuously improve our standards by:

1. **Regular reviews**: Code reviews are mandatory for all changes
2. **Retrospectives**: Regular team discussions about code quality challenges
3. **Benchmarking**: Comparing our practices against industry standards
4. **Automation**: Increasing our use of automated tools and checks
5. **Training**: Ongoing education about best practices

---

## Related Documentation

* [10 - Development: Workflow](10-development-workflow.md) - Development workflow guide
* [11 - Development: Contributing](11-development-contributing.md) - Contribution guidelines
* [13 - Development: Plugin System](13-development-plugin-system.md) - Plugin development guide
* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [23 - Tech: Testing](23-tech-testing.md) - Testing guidelines
* [25 - Tech: Typing](25-tech-typing.md) - Type systems and Pydantic
