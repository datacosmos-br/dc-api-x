"""
CLI helper utilities.

This module provides utility functions for CLI operations,
including output formatting, error handling, and API client creation.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console

from dc_api_x import (
    ApiClient,
    ApiConnectionError,
    BaseAPIError,
    CLIError,
    ConfigurationError,
    NotFoundError,
    ValidationError,
)
from dc_api_x.utils.formatting import format_json, format_table

# Set up console for rich output
console = Console()


def handle_common_errors(func: Callable) -> Callable:
    """Decorator to handle common API client errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConfigurationError as e:
            console.print(f"[red]Configuration error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except ApiConnectionError as e:
            console.print(f"[red]Connection error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except ValidationError as e:
            console.print(f"[red]Validation error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except NotFoundError as e:
            console.print(f"[red]Not found: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except OSError as e:
            console.print(f"[red]File error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except json.JSONDecodeError as e:
            console.print(f"[red]JSON error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except BaseAPIError as e:
            console.print(f"[red]API error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except CLIError as e:
            console.print(f"[red]CLI error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e

    return wrapper


def create_api_client(profile: Optional[str] = None) -> ApiClient:
    """Create an API client with optional profile."""
    return ApiClient.from_profile(profile) if profile else ApiClient()


def format_output_data(
    data: Any,
    output_format: str,
) -> str:
    """Format output data based on format and structure."""
    if output_format.lower() == "json":
        return format_json(data, indent=2)

    if isinstance(data, list):
        return format_table(data)

    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        return format_table(data["data"])

    console.print(
        "[yellow]Warning: Data is not a list, falling back to JSON format[/yellow]",
    )
    return format_json(data, indent=2)


def output_result(data: str, output_file: Optional[Path] = None) -> None:
    """Output result to console or file."""
    if output_file:
        output_file.write_text(data)
        console.print(f"Output written to: [bold]{output_file}[/bold]")
    else:
        console.print(data)


def parse_key_value_params(
    params: list[str],
    param_name: str = "parameter",
) -> dict[str, str]:
    """Parse key=value parameters from command line."""
    result = {}
    for p in params:
        try:
            name, value = p.split("=", 1)
            result[name] = value
        except ValueError:
            console.print(
                f"[yellow]Warning: Ignoring invalid {param_name} format: {p}[/yellow]",
            )
    return result
