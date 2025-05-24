# dc-api-x CLI Documentation

The dc-api-x CLI is built using [Typer](https://typer.tiangolo.com) and enhanced with [doctyper](https://github.com/audivir/doctyper) to provide a rich, intuitive command-line interface with excellent documentation.

## Overview

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

## doctyper Integration

dc-api-x uses doctyper to enhance the CLI by:

1. **Parsing Google-style docstrings** - Automatically extracts descriptions from function docstrings
2. **Using type annotations** - Leverages Python type hints for parameter validation
3. **Rich formatting** - Provides clear, well-formatted help text with proper sections

### Before and After Example

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

## Common Commands

### Configuration Management

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

### API Requests

```bash
# Make GET request
dcapix request get /api/users --param page=1 --param limit=10

# Make POST request with data
dcapix request post /api/users --data '{"name": "John Doe", "email": "john@example.com"}'

# Make POST request with data from file
dcapix request post /api/users --data-file user.json
```

### Schema Management

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

### Entity Operations

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

## Advanced Usage

### Output Formatting

```bash
# Format output as pretty-printed JSON (default)
dcapix entity get user --format json

# Format output as table
dcapix entity get user --format table

# Save output to file
dcapix entity get user --output users.json
```

### Debugging

```bash
# Enable debug output
dcapix --debug entity get user

# Check version
dcapix --version
```

## Extending the CLI

The CLI is designed to be extensible through the plugin system. Plugin modules can register new commands and subcommands by implementing the appropriate hooks.

### Creating a CLI Plugin

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

## Development

When modifying the CLI, remember to:

1. Use Google-style docstrings for all commands and parameters
2. Add type hints with the `Annotated` pattern when using doctyper
3. Include detailed descriptions in docstrings
4. Add tests for new commands in `tests/test_cli_*.py` 
