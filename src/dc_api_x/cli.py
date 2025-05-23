"""
Command-line interface for DCApiX.

This module provides a command-line interface for working with API clients,
including commands for testing connections, making requests, and managing schemas.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .client import ApiClient
from .config import Config, list_available_profiles
from .entity import EntityManager
from .exceptions import (
    ApiConnectionError,
    AuthenticationError,
    BaseAPIError,
    CLIError,
    ConfigurationError,
    NotFoundError,
    ValidationError,
)
from .schema import SchemaManager
from .utils.formatting import format_json, format_table
from .utils.logging import setup_logger

# Set up logger
logger = setup_logger("dc_api_x.cli", level=logging.INFO)

# Create console for rich output
console = Console()


@click.group()
@click.version_option()
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug output",
)
@click.pass_context
def cli(ctx: click.Context, *, debug: bool = False) -> None:
    """
    DCApiX - Python API Extensions CLI.

    A tool for working with API clients created with DCApiX.
    """
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    # Configure logging
    if debug:
        setup_logger("dc_api_x", level=logging.DEBUG)


@cli.group()
def config() -> None:
    """Manage API client configuration."""


@config.command("list")
def config_list() -> None:
    """list available configuration profiles."""
    profiles = list_available_profiles()

    if not profiles:
        console.print("[yellow]No configuration profiles found.[/yellow]")
        console.print("Create .env.{profile} files to define profiles.")
        return

    console.print("[bold]Available configuration profiles:[/bold]")
    for profile in profiles:
        console.print(f"  • [green]{profile}[/green]")


@config.command("show")
@click.argument("profile", required=False)
def config_show(profile: str | None) -> None:
    """Show configuration for a profile."""
    try:
        # Use ternary operator to simplify the code
        cfg = Config.from_profile(profile) if profile else Config()

        # Convert to dictionary (excluding sensitive fields)
        config_dict = cfg.to_dict()
        if "password" in config_dict:
            config_dict["password"] = "********"  # noqa: S105, B105

        # Pretty print configuration
        console.print("[bold]Configuration:[/bold]")
        console.print(json.dumps(config_dict, indent=2))

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except OSError as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@config.command("test")
@click.argument("profile", required=False)
def config_test(profile: str | None) -> None:
    """Test API connection with configuration."""
    try:
        # Create client
        if profile:
            client = ApiClient.from_profile(profile)
            console.print(f"Using configuration profile: [green]{profile}[/green]")
        else:
            client = ApiClient()
            console.print("Using default configuration from environment")

        # Test connection
        console.print("Testing connection...")
        success, message = client.test_connection()

        if success:
            console.print(f"[green]Connection successful: {message}[/green]")
        else:
            console.print(f"[red]Connection failed: {message}[/red]")
            sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@cli.group()
def request() -> None:
    """Make API requests."""


@request.command("get")
@click.argument("endpoint")
@click.option("--profile", help="Configuration profile to use")
@click.option("--param", "-p", multiple=True, help="Query parameters (name=value)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.pass_context
def request_get(
    _: click.Context,  # Unused context parameter
    endpoint: str,
    profile: str | None,
    param: list[str],
    output_format: str,
    output: str | None,
) -> None:
    """Make GET request to API endpoint."""
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Parse parameters
        params = {}
        for p in param:
            try:
                name, value = p.split("=", 1)
                params[name] = value
            except ValueError:
                console.print(
                    f"[yellow]Warning: Ignoring invalid parameter format: {p}[/yellow]",
                )

        # Make request
        console.print(f"Making GET request to: [bold]{endpoint}[/bold]")
        if params:
            console.print(f"Parameters: {params}")

        response = client.get(endpoint, params=params)

        # Handle response
        if response.success:
            console.print(
                f"[green]Request successful (status: {response.status_code})[/green]",
            )

            # Format output
            if output_format == "json":
                formatted_output = format_json(response.data, indent=2)
            elif isinstance(response.data, list):
                formatted_output = format_table(response.data)
            elif (
                isinstance(response.data, dict)
                and "data" in response.data
                and isinstance(response.data["data"], list)
            ):
                formatted_output = format_table(response.data["data"])
            else:
                console.print(
                    "[yellow]Warning: Data is not a list, falling back to JSON format[/yellow]",
                )
                formatted_output = format_json(response.data, indent=2)

            # Output result
            if output:
                with Path(output).open("w") as f:
                    f.write(formatted_output)
                console.print(f"Output written to: [bold]{output}[/bold]")
            else:
                console.print(formatted_output)
        else:
            console.print(
                f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
            )
            sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except (IOError, OSError) as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@dataclass
class RequestPostParams:
    """Parameters for post request command."""

    endpoint: str
    profile: Optional[str] = None
    param: list[str] = None
    data: Optional[str] = None
    data_file: Optional[str] = None
    output_format: str = "json"
    output: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.param is None:
            self.param = []


@request.command("post")
@click.argument("endpoint")
@click.option("--profile", help="Configuration profile to use")
@click.option("--param", "-p", multiple=True, help="Query parameters (name=value)")
@click.option("--data", "-d", help="JSON data string")
@click.option("--data-file", type=click.Path(exists=True), help="JSON data file")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.pass_context
def request_post(
    _: click.Context,  # Unused context parameter
    endpoint: str,
    profile: str | None,
    param: list[str],
    data: str | None,
    data_file: str | None,
    format: str,
    output: str | None,
) -> None:
    """Make POST request to API endpoint."""
    params = RequestPostParams(
        endpoint=endpoint,
        profile=profile,
        param=list(param),
        data=data,
        data_file=data_file,
        output_format=format,
        output=output,
    )
    _handle_post_request(params)


def _handle_post_request(params: RequestPostParams) -> None:
    """Handle POST request with given parameters."""
    try:
        # Create client
        client = (
            ApiClient.from_profile(params.profile) if params.profile else ApiClient()
        )

        # Parse parameters
        request_params = {}
        for p in params.param:
            try:
                name, value = p.split("=", 1)
                request_params[name] = value
            except ValueError:
                console.print(
                    f"[yellow]Warning: Ignoring invalid parameter format: {p}[/yellow]",
                )

        # Get data
        json_data = None
        if params.data_file:
            try:
                with Path(params.data_file).open() as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON in data file: {e}")
        elif params.data:
            try:
                json_data = json.loads(params.data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON data: {e}")

        # Make request
        console.print(f"Making POST request to: [bold]{params.endpoint}[/bold]")
        if request_params:
            console.print(f"Parameters: {request_params}")

        response = client.post(
            params.endpoint, params=request_params, json_data=json_data
        )

        # Handle response
        if response.success:
            console.print(
                f"[green]Request successful (status: {response.status_code})[/green]",
            )

            # Format output
            if params.output_format == "json":
                formatted_output = format_json(response.data, indent=2)
            elif isinstance(response.data, list):
                formatted_output = format_table(response.data)
            elif (
                isinstance(response.data, dict)
                and "data" in response.data
                and isinstance(response.data["data"], list)
            ):
                formatted_output = format_table(response.data["data"])
            else:
                console.print(
                    "[yellow]Warning: Data is not a list, falling back to JSON format[/yellow]",
                )
                formatted_output = format_json(response.data, indent=2)

            # Output result
            if params.output:
                with Path(params.output).open("w") as f:
                    f.write(formatted_output)
                console.print(f"Output written to: [bold]{params.output}[/bold]")
            else:
                console.print(formatted_output)
        else:
            console.print(
                f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
            )
            sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[red]Validation error: {str(e)}[/red]")
        sys.exit(1)
    except (IOError, OSError) as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@cli.group()
def schema() -> None:
    """Manage API schemas."""


@schema.command("extract")
@click.argument("entity", required=False)
@click.option("--profile", help="Configuration profile to use")
@click.option(
    "--output-dir",
    type=click.Path(),
    default="./schemas",
    help="Output directory for schemas",
)
@click.option(
    "--all",
    is_flag=True,
    help="Extract all entity schemas",
    name="extract_all",
)
@click.pass_context
def schema_extract(
    _: click.Context,  # Unused context parameter
    entity: str | None,
    profile: str | None,
    output_dir: str,
    *,
    extract_all: bool,
) -> None:
    """Extract schema for an entity."""
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create schema manager
        schema_manager = SchemaManager(client, cache_dir=output_dir)

        if extract_all:
            # Extract all schemas
            console.print("Extracting schemas for all entities...")
            schemas = schema_manager.extract_all_schemas()

            if not schemas:
                console.print("[yellow]No schemas found.[/yellow]")
                return

            console.print(
                f"[green]Successfully extracted {len(schemas)} schemas to {output_dir}[/green]",
            )

            # list extracted schemas
            console.print("[bold]Extracted schemas:[/bold]")
            for name, schema in schemas.items():
                if schema:
                    console.print(f"  • [green]{name}[/green]")
                else:
                    console.print(f"  • [red]{name} (failed)[/red]")

        elif entity:
            # Extract specific schema
            console.print(f"Extracting schema for entity: [bold]{entity}[/bold]")
            schema = schema_manager.get_schema(entity)

            if schema:
                file_path = schema.save(output_dir)
                console.print(f"[green]Schema saved to: {file_path}[/green]")
            else:
                console.print(
                    f"[red]Failed to extract schema for entity: {entity}[/red]",
                )
                sys.exit(1)

        else:
            console.print(
                "[yellow]Please specify an entity name or use --all flag.[/yellow]",
            )
            sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except (IOError, OSError) as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@schema.command("list")
@click.option(
    "--cache-dir",
    type=click.Path(),
    default="./schemas",
    help="Schema cache directory",
)
@click.pass_context
def schema_list(
    _: click.Context,  # Unused context parameter
    cache_dir: str,
) -> None:
    """list available schemas."""
    try:
        # Check cache directory
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            console.print(
                f"[yellow]Cache directory does not exist: {cache_dir}[/yellow]",
            )
            console.print("Run 'schema extract --all' to download schemas.")
            return

        # list schema files
        schema_files = list(cache_path.glob("*.schema.json"))

        if not schema_files:
            console.print(f"[yellow]No schema files found in: {cache_dir}[/yellow]")
            console.print("Run 'schema extract --all' to download schemas.")
            return

        # Print schema list
        console.print(f"[bold]Available schemas ({len(schema_files)}):[/bold]")
        for file_path in sorted(schema_files):
            name = file_path.stem
            if name.endswith(".schema"):
                name = name[:-7]
            console.print(f"  • [green]{name}[/green]")

    except OSError as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@schema.command("show")
@click.argument("entity")
@click.option(
    "--cache-dir",
    type=click.Path(),
    default="./schemas",
    help="Schema cache directory",
)
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.pass_context
def schema_show(
    _: click.Context,  # Unused context parameter
    entity: str,
    cache_dir: str,
    output: str | None,
) -> None:
    """Show schema for an entity."""
    try:
        # Check cache directory
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            console.print(
                f"[yellow]Cache directory does not exist: {cache_dir}[/yellow]",
            )
            console.print("Run 'schema extract --all' to download schemas.")
            sys.exit(1)

        # Find schema file
        schema_file = cache_path / f"{entity.lower()}.schema.json"
        if not schema_file.exists():
            console.print(f"[red]Schema file not found: {schema_file}[/red]")
            console.print(f"Run 'schema extract {entity}' to download the schema.")
            sys.exit(1)

        # Load and display schema
        try:
            schema = SchemaManager.load_schema(schema_file)

            # Format as JSON
            formatted_output = format_json(schema.to_json_schema(), indent=2)

            # Output result
            if output:
                with Path(output).open("w") as f:
                    f.write(formatted_output)
                console.print(f"Output written to: [bold]{output}[/bold]")
            else:
                console.print(f"[bold]Schema for {entity}:[/bold]")
                console.print(formatted_output)

        except ValidationError as e:
            console.print(f"[red]Schema validation error: {str(e)}[/red]")
            sys.exit(1)

    except OSError as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[red]Validation error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@cli.group()
def entity() -> None:
    """Work with API entities."""


@entity.command("list")
@click.option("--profile", help="Configuration profile to use")
@click.pass_context
def entity_list(
    _: click.Context,  # Unused context parameter
    profile: str | None,
) -> None:
    """list available entities."""
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create entity manager
        entity_manager = EntityManager(client)

        # Discover entities
        console.print("Discovering available entities...")
        entities = entity_manager.discover_entities()

        if not entities:
            console.print("[yellow]No entities found.[/yellow]")
            return

        # Print entity list
        console.print(f"[bold]Available entities ({len(entities)}):[/bold]")
        for name in sorted(entities):
            console.print(f"  • [green]{name}[/green]")

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


@dataclass
class EntityGetParams:
    """Parameters for entity get command."""

    entity: str
    entity_id: Optional[str] = None
    profile: Optional[str] = None
    filter_params: list[str] = None
    sort: Optional[str] = None
    order: str = "asc"
    limit: Optional[int] = None
    offset: Optional[int] = None
    output_format: str = "json"
    output: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.filter_params is None:
            self.filter_params = []


@entity.command("get")
@click.argument("entity")
@click.argument("entity_id", required=False)
@click.option("--profile", help="Configuration profile to use")
@click.option(
    "--filter",
    "-f",
    multiple=True,
    help="Filter conditions (name=value)",
    name="filter_params",
)
@click.option("--sort", help="Sort field")
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    default="asc",
    help="Sort order",
)
@click.option("--limit", type=int, help="Maximum number of results")
@click.option("--offset", type=int, help="Starting position for pagination")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format",
    name="output_format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.pass_context
def entity_get(
    _: click.Context,  # Unused context parameter
    entity: str,
    entity_id: str | None,
    profile: str | None,
    filter_params: list[str],
    sort: str | None,
    order: str,
    limit: int | None,
    offset: int | None,
    output_format: str,
    output: str | None,
) -> None:
    """Get entity data."""
    params = EntityGetParams(
        entity=entity,
        entity_id=entity_id,
        profile=profile,
        filter_params=list(filter_params),
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
        output_format=output_format,
        output=output,
    )
    _handle_entity_get(params)


def _handle_entity_get(params: EntityGetParams) -> None:
    """Handle entity get with given parameters."""
    try:
        # Create client
        client = (
            ApiClient.from_profile(params.profile) if params.profile else ApiClient()
        )

        # Create entity manager
        entity_manager = EntityManager(client)

        # Get entity
        entity_obj = entity_manager.get_entity(params.entity)

        # Parse filters
        filters = {}
        for f in params.filter_params:
            try:
                name, value = f.split("=", 1)
                filters[name] = value
            except ValueError:
                console.print(
                    f"[yellow]Warning: Ignoring invalid filter format: {f}[/yellow]",
                )

        # Make request
        if params.entity_id:
            # Get single resource
            console.print(
                f"Getting {params.entity} with ID: [bold]{params.entity_id}[/bold]",
            )
            response = entity_obj.get(params.entity_id)
        else:
            # list resources
            console.print(f"Listing {params.entity} resources")
            if filters:
                console.print(f"Filters: {filters}")

            response = entity_obj.list(
                filters=filters,
                sort_by=params.sort,
                sort_order=params.order,
                limit=params.limit,
                offset=params.offset,
            )

        # Handle response
        if response.success:
            console.print(
                f"[green]Request successful (status: {response.status_code})[/green]",
            )

            # Format output
            if params.output_format == "json":
                formatted_output = format_json(response.data, indent=2)
            elif isinstance(response.data, list):
                formatted_output = format_table(response.data)
            elif (
                isinstance(response.data, dict)
                and "data" in response.data
                and isinstance(response.data["data"], list)
            ):
                formatted_output = format_table(response.data["data"])
            else:
                console.print(
                    "[yellow]Warning: Data is not a list, falling back to JSON format[/yellow]",
                )
                formatted_output = format_json(response.data, indent=2)

            # Output result
            if params.output:
                with Path(params.output).open("w") as f:
                    f.write(formatted_output)
                console.print(f"Output written to: [bold]{params.output}[/bold]")
            else:
                console.print(formatted_output)
        else:
            console.print(
                f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
            )
            sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[red]Validation error: {str(e)}[/red]")
        sys.exit(1)
    except NotFoundError as e:
        console.print(f"[red]Not found: {str(e)}[/red]")
        sys.exit(1)
    except OSError as e:
        console.print(f"[red]File error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)


def main() -> None:
    """Run the CLI application."""
    try:
        cli()
    except CLIError as e:
        console.print(f"[red]CLI error: {str(e)}[/red]")
        sys.exit(1)
    except ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        # Keep broad exception handler for top-level function to catch all unexpected errors
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        if os.environ.get("PYAPIX_DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
