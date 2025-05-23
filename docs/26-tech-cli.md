# Command-Line Interface

> *"A great CLI is the foundation of developer experience."*
> This guide explains how DCApiX creates a powerful, intuitive command-line interface using Typer and doctyper
> across the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [25 - Tech: Typing](25-tech-typing.md) | **26 - Tech: CLI** | [27 - Tech: Plugin](27-tech-plugin.md) |

---

## 1. Introduction

DCApiX leverages [Typer](https://typer.tiangolo.com/) for building its command-line interface (CLI), enhanced with
[doctyper](https://github.com/audivir/doctyper) for rich documentation generation. This creates an intuitive and
discoverable interface for working with the integration ecosystem.

---

## 2. Core Features

### 2.1 Command Structure

Typer organizes commands into a hierarchical structure that makes the CLI intuitive and discoverable:

* **Command Groups**: Organize related commands under a common namespace
* **Subcommands**: Provide specific functionality within a command group
* **Command Parameters**: Define options and arguments with type checking

### 2.2 Parameter Types

DCApiX uses Typer's type-driven parameter definition:

* **Arguments**: Required positional inputs
* **Options**: Named parameters with flags (`--option`)
* **Typed Parameters**: Automatic validation and conversion based on Python type hints
* **Default Values**: Sensible defaults with clear documentation

### 2.3 Documentation and Help

The CLI provides rich help text through doctyper integration:

* **Command Help**: Detailed description of each command and its purpose
* **Parameter Help**: Description of each parameter, including type and default values
* **Examples**: Usage examples for common scenarios
* **Rich Formatting**: Colorized output, tables, and highlight formatting

---

## 3. Command Organization

The DCApiX CLI follows this structure:

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

---

## 4. Command Definition

DCApiX uses doctyper to enhance Typer with Google-style docstring parsing:

```python
import typer
from typing import Annotated
import doctyper

app = doctyper.Typer(help="DCApiX CLI")

# Create a subcommand group
config_app = doctyper.Typer(help="Configuration management")
app.add_typer(config_app, name="config")

@config_app.command("list")
def list_configs() -> None:
    """List all available configuration profiles.

    This command scans the config directory and environment for available
    profiles and displays them in a table format.
    """
    # Implementation...
    profiles = ["dev", "prod", "staging"]
    for profile in profiles:
        typer.echo(f"- {profile}")

@config_app.command("test")
def test_connection(
    profile: Annotated[str, doctyper.Option(help="Profile to test")] = "default",
    timeout: Annotated[int, doctyper.Option(help="Connection timeout in seconds")] = 30,
) -> None:
    """Test connection using the specified profile.

    Attempts to connect to the API using the configuration from the
    specified profile and reports success or failure.

    Args:
        profile: The profile name to use for configuration
        timeout: Connection timeout in seconds
    """
    # Implementation...
    typer.echo(f"Testing connection with profile '{profile}'...")
    # Test logic here
    typer.echo(typer.style("✓ Connection successful", fg=typer.colors.GREEN))
```

---

## 5. Advanced Features

### 5.1 Rich Output Formatting

DCApiX CLI uses Typer's rich output capabilities:

```python
import typer
from rich.table import Table
from rich.console import Console

@app.command("list-users")
def list_users() -> None:
    """List all users with formatted output."""
    # Create a rich table
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email", style="yellow")

    # Add data
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    ]

    for user in users:
        table.add_row(str(user["id"]), user["name"], user["email"])

    # Display the table
    console = Console()
    console.print(table)
```

### 5.2 Progress Bars

For long-running operations, DCApiX provides progress feedback:

```python
import typer
import time

@app.command("sync")
def sync_data() -> None:
    """Synchronize data with remote server."""
    total = 100
    with typer.progressbar(range(total), label="Syncing data") as progress:
        for i in progress:
            # Perform work
            time.sleep(0.05)

    typer.echo(typer.style("✓ Sync completed", fg=typer.colors.GREEN))
```

### 5.3 Interactive Input

The CLI supports interactive prompts and confirmations:

```python
import typer

@app.command("login")
def login() -> None:
    """Log in to the API."""
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)

    # Authentication logic
    typer.echo(f"Logging in as {username}...")
    # Success message
    typer.echo(typer.style("✓ Login successful", fg=typer.colors.GREEN))

@app.command("delete")
def delete_entity(
    entity_id: Annotated[str, doctyper.Argument(help="ID of entity to delete")]
) -> None:
    """Delete an entity from the system.

    This is a destructive operation that permanently removes an entity.

    Args:
        entity_id: The unique identifier of the entity to delete
    """
    # Confirm before deleting
    if typer.confirm(f"Are you sure you want to delete entity {entity_id}?"):
        # Deletion logic
        typer.echo(f"Deleting entity {entity_id}...")
        typer.echo(typer.style("✓ Entity deleted", fg=typer.colors.GREEN))
    else:
        typer.echo("Operation cancelled")
```

---

## 6. Extending the CLI

### 6.1 Plugin Integration

Plugins can extend the DCApiX CLI with their own commands:

```python
from dc_api_x.cli import app as main_app
import doctyper

# Create a new command group
plugin_app = doctyper.Typer(help="My plugin commands")

@plugin_app.command("run")
def run_plugin_command(
    param: Annotated[str, doctyper.Argument(help="Plugin parameter")]
) -> None:
    """Run a plugin-specific command.

    This command demonstrates how plugins can extend the DCApiX CLI
    with their own functionality.

    Args:
        param: The parameter for the plugin command
    """
    # Plugin command implementation
    print(f"Running plugin command with parameter: {param}")

# Register with main CLI
main_app.add_typer(plugin_app, name="plugin")
```

### 6.2 Output Formats

Commands can support multiple output formats:

```python
import typer
import json
import yaml

@app.command("get-data")
def get_data(
    format: Annotated[str, doctyper.Option(help="Output format")] = "table"
) -> None:
    """Get data in various formats.

    Args:
        format: Output format (table, json, yaml)
    """
    data = {"name": "Example", "values": [1, 2, 3]}

    if format == "json":
        typer.echo(json.dumps(data, indent=2))
    elif format == "yaml":
        typer.echo(yaml.dump(data))
    else:
        # Table format (default)
        typer.echo("Name: Example")
        typer.echo("Values:")
        for value in data["values"]:
            typer.echo(f"- {value}")
```

---

## 7. Best Practices

1. **Use Google-style Docstrings**: Include detailed `Args:` sections for all parameters

2. **Follow Command Hierarchy**: Group related commands logically

3. **Type Everything**: Use proper type annotations for all parameters

4. **Provide Examples**: Include example usages in command help

5. **Descriptive Names**: Use clear, descriptive names for commands and parameters

6. **Defaults Where Appropriate**: Provide sensible defaults for optional parameters

7. **Confirmation for Destructive Actions**: Always confirm before destructive operations

8. **Rich Feedback**: Use progress bars for long operations and clear success/error messages

9. **Consistent Style**: Maintain consistent naming and style across all commands

10. **Error Handling**: Provide clear error messages and non-zero exit codes for failures

---

## 8. Command Reference

### 8.1 Configuration Commands

| Command | Description | Example |
|---------|-------------|---------|
| `config list` | List available profiles | `dcapix config list` |
| `config show` | Show profile details | `dcapix config show dev` |
| `config test` | Test connection | `dcapix config test --profile prod` |

### 8.2 Request Commands

| Command | Description | Example |
|---------|-------------|---------|
| `request get` | Make GET request | `dcapix request get /users` |
| `request post` | Make POST request | `dcapix request post /users --data '{"name":"John"}'` |

### 8.3 Schema Commands

| Command | Description | Example |
|---------|-------------|---------|
| `schema extract` | Extract API schema | `dcapix schema extract --all` |
| `schema list` | List available schemas | `dcapix schema list` |
| `schema show` | Show schema details | `dcapix schema show User` |

### 8.4 Entity Commands

| Command | Description | Example |
|---------|-------------|---------|
| `entity list` | List available entities | `dcapix entity list` |
| `entity get` | Get entity data | `dcapix entity get user 123` |

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools
* [25 - Tech: Typing](25-tech-typing.md) - Type system and Pydantic
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Structured logging
* [27 - Tech: Plugin](27-tech-plugin.md) - Plugin system architecture
