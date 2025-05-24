# CLI Reference

> *"A great CLI is the foundation of developer experience."*
> This document provides a comprehensive reference for the DCApiX command-line
> interface, built with Typer and enhanced with doctyper.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [22 - Tech: Developer Tools](22-tech-developer-tools.md) | **30 - CLI Reference** | [40 - Integration: Robot Framework](40-integration-robot-framework.md) |

---

## 1. Overview

The DCApiX CLI is built using [Typer](https://typer.tiangolo.com) and enhanced with [doctyper](https://github.com/audivir/doctyper) to provide a rich, intuitive command-line interface with excellent documentation.

The CLI follows a hierarchical command structure:

```asciidoc
dcapix
├── config
│   ├── list
│   ├── show
│   └── test
├── request
│   ├── get
│   └── post
├── schema
│   ├── extract
│   ├── list
│   └── show
└── entity
    ├── list
    └── get
```

---

## 2. doctyper Integration

DCApiX uses doctyper to enhance the CLI by:

1. **Parsing Google-style docstrings** – Automatically extracts descriptions from function docstrings
2. **Using type annotations** – Leverages Python type hints for parameter validation
3. **Rich formatting** – Provides clear, well-formatted help text with proper sections

### 2.1 Before and After Example

#### Before (Plain Typer)

```python
@app.command()
def example(
    name: str = typer.Argument(..., help="Name argument"),
    count: int = typer.Option(1, help="Count of iterations"),
):
    """Simple example command."""
    for _ in range(count):
        print(f"Hello {name}")
```

#### After (With doctyper)

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

---

## 3. Common Commands

### 3.1 Configuration Management

```bash
# List available profiles
dcapix config list

# Show configuration for default profile
dcapix config show

# Show configuration for specific profile
dcapix config show dev

# Test connection with default profile
dcapix config test

# Test connection with specific profile
dcapix config test --profile dev
```

### 3.2 API Requests

```bash
# Make GET request
dcapix request get /api/users --param page=1 --param limit=10

# Make POST request with data
dcapix request post /api/users --data '{"name": "John Doe", "email": "john@example.com"}'

# Make POST request with data from file
dcapix request post /api/users --data-file user.json
```

### 3.3 Schema Management

```bash
# Extract schema for specific entity
dcapix schema extract user

# Extract schemas for all entities
dcapix schema extract --all

# List available schemas
dcapix schema list

# Show schema for specific entity
dcapix schema show user
```

### 3.4 Entity Operations

```bash
# List available entities
dcapix entity list

# Get entity by ID
dcapix entity get user 123

# List entities with filtering
dcapix entity get user --filter status=active --filter role=admin

# List entities with pagination
dcapix entity get user --limit 10 --offset 20

# List entities with sorting
dcapix entity get user --sort name --order desc
```

---

## 4. Advanced Usage

### 4.1 Output Formatting

```bash
# Format output as pretty-printed JSON (default)
dcapix entity get user --format json

# Format output as table
dcapix entity get user --format table

# Save output to file
dcapix entity get user --output users.json
```

### 4.2 Debugging

```bash
# Enable debug output
dcapix --debug entity get user

# Check version
dcapix --version
```

---

## 5. Extending the CLI

The CLI is designed to be extensible through the plugin system. Plugin modules can register new commands and subcommands by implementing the appropriate hooks.

### 5.1 Creating a CLI Plugin

```python
from dc_api_x.cli import app as cli_app

# Create a new command group
my_plugin_app = doctyper.Typer(help="My plugin commands")

@my_plugin_app.command("execute")
def execute_command(
    param: Annotated[str, doctyper.Argument(help="Command parameter")],
) -> None:
    """Execute a plugin-specific command.

    Args:
        param: The parameter to use for execution
    """
    # Command implementation here

# Register with main CLI
cli_app.add_typer(my_plugin_app, name="myplugin")
```

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries like Pydantic
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools including Typer
