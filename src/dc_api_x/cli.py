"""
Command-line interface for API X.

This module provides CLI commands for interacting with the API using Typer with doctyper
enhancement for better documentation and UI generation from Google-style docstrings.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

import doctyper
import typer
from rich.console import Console

import dc_api_x as apix

from .utils.cli_exceptions import (
    JsonValidationError,
    SchemaEntityNotSpecifiedError,
    SchemaExtractionFailedError,
)
from .utils.cli_helpers import (
    create_api_client,
    format_output_data,
    handle_common_errors,
    output_result,
    parse_key_value_params,
)
from .utils.logging import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Set up console for rich output
console = Console()

# Create Typer app instances with doctyper enhancement
app = doctyper.Typer(help="Command-line interface for API X.")
config_app = doctyper.Typer(help="Manage API client configuration.")
request_app = doctyper.Typer(help="Make API requests.")
schema_app = doctyper.Typer(help="Manage API schemas.")
entity_app = doctyper.Typer(help="Work with API entities.")

# Register sub-apps
app.add_typer(config_app, name="config")
app.add_typer(request_app, name="request")
app.add_typer(schema_app, name="schema")
app.add_typer(entity_app, name="entity")


# Define state object for debug flag
class State:
    debug: bool = False


state = State()


@app.callback()
def app_callback(
    *,  # Make all arguments keyword-only to fix FBT002
    version: Annotated[
        bool,
        doctyper.Option(
            param_decls=["--version"],
            help="Show version and exit",
            is_flag=True,
        ),
    ] = False,
    debug: Annotated[
        bool,
        doctyper.Option(param_decls=["--debug/--no-debug"], help="Enable debug output"),
    ] = False,
) -> None:
    """Command-line interface for API X.

    Provides a hierarchical structure of commands and sub-commands for interacting
    with the API, with rich formatting and detailed help documentation.

    Args:
        version: Show application version and exit
        debug: Enable debug output
    """
    if version:
        typer.echo(f"API X CLI version: {apix.__version__}")
        raise typer.Exit()

    # Store debug flag
    state.debug = debug

    # Configure logging
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")


@config_app.command("list")
@handle_common_errors
def config_list() -> None:
    """List available configuration profiles.

    Displays all available configuration profiles found in the environment
    that can be used with the API client.
    """
    profiles = apix.list_available_profiles()

    if not profiles:
        console.print("[yellow]No configuration profiles found.[/yellow]")
        console.print("Create .env.{profile} files to define profiles.")
        return

    console.print("[bold]Available configuration profiles:[/bold]")
    for profile in profiles:
        console.print(f"  • [green]{profile}[/green]")


@config_app.command("show")
@handle_common_errors
def config_show(
    profile: Annotated[
        Optional[str],
        doctyper.Argument(help="Configuration profile to show"),
    ] = None,
) -> None:
    """Show configuration for a profile.

    Displays the configuration settings for a specific profile or the default
    configuration if no profile is specified.

    Args:
        profile: The name of the configuration profile to show
    """
    # Use ternary operator to simplify the code
    cfg = apix.Config.from_profile(profile) if profile else apix.Config()

    # Convert to dictionary (excluding sensitive fields)
    config_dict = cfg.to_dict()
    if "password" in config_dict:
        config_dict["password"] = "********"  # noqa: S105, B105 - placeholder password

    # Pretty print configuration
    console.print("[bold]Configuration:[/bold]")
    console.print(json.dumps(config_dict, indent=2))


@config_app.command("test")
@handle_common_errors
def config_test(
    profile: Annotated[
        Optional[str],
        doctyper.Option(help="Configuration profile to use"),
    ] = None,
) -> None:
    """Test API connection with configuration.

    Attempts to connect to the API using the specified configuration profile
    or the default configuration if no profile is specified.

    Args:
        profile: The configuration profile to use for testing
    """
    # Create client
    client = create_api_client(profile)

    if profile:
        console.print(f"Using configuration profile: [green]{profile}[/green]")
    else:
        console.print("Using default configuration from environment")

    # Test connection
    console.print("Testing connection...")
    success, message = client.test_connection()

    if success:
        console.print(f"[green]Connection successful: {message}[/green]")
    else:
        console.print(f"[red]Connection failed: {message}[/red]")
        raise typer.Exit(code=1)


@dataclass
class RequestOptions:
    """Common options for API requests."""

    profile: Optional[str] = None
    params: Optional[list[str]] = None
    output_format: str = "json"
    output_file: Optional[Path] = None

    def __post_init__(self):
        if self.params is None:
            self.params = []


@request_app.callback()
def request_app_callback(
    _profile: Annotated[  # Prefix with underscore to indicate intentionally unused
        Optional[str],
        doctyper.Option(help="Configuration profile to use"),
    ] = None,
    param: Annotated[
        list[str],
        doctyper.Option(
            param_decls=["--param", "-p"],
            help="Query parameters (name=value)",
        ),
    ] = None,  # Use None instead of [] to avoid mutable default
    _output_format: Annotated[  # Prefix with underscore to indicate intentionally unused
        str,
        doctyper.Option(
            param_decls=["--format", "-f"],
            help="Output format",
            show_default=True,
            case_sensitive=False,
        ),
    ] = "json",
    _output: Annotated[  # Prefix with underscore to indicate intentionally unused
        Optional[Path],
        doctyper.Option(param_decls=["--output", "-o"], help="Output file"),
    ] = None,
) -> None:
    """Configure common options for API requests.

    Args:
        _profile: Configuration profile to use
        param: Query parameters in name=value format
        _output_format: Format for displaying results
        _output: File to save output to
    """
    # Initialize mutable default
    if param is None:
        param = []

    # Options are handled by typer and passed to command functions


@request_app.command("get")
@handle_common_errors
def request_get(
    endpoint: Annotated[str, doctyper.Argument(help="API endpoint")],
) -> None:
    """Make GET request to API endpoint.

    Sends a GET request to the specified API endpoint with optional
    query parameters and formats the response according to the output
    format setting.

    Args:
        endpoint: The API endpoint to send the request to
    """
    # Get options from typer context
    ctx = typer.get_current_context()
    profile = ctx.params.get("profile")
    param = ctx.params.get("param", [])
    output_format = ctx.params.get("output_format", "json")
    output = ctx.params.get("output")

    # Create client
    client = create_api_client(profile)

    # Parse parameters
    params = parse_key_value_params(param)

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

        # Format and output result
        formatted_output = format_output_data(response.data, output_format)
        output_result(formatted_output, output)
    else:
        console.print(
            f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
        )
        raise typer.Exit(code=1)


@request_app.command("post")
@handle_common_errors
def request_post(
    endpoint: Annotated[str, doctyper.Argument(help="API endpoint")],
    data: Annotated[
        Optional[str],
        doctyper.Option(param_decls=["--data", "-d"], help="JSON data string"),
    ] = None,
    data_file: Annotated[Optional[Path], doctyper.Option(help="JSON data file")] = None,
) -> None:
    """Make POST request to API endpoint.

    Sends a POST request to the specified API endpoint with optional
    data and query parameters, formatting the response according to the
    output format setting.

    Args:
        endpoint: API endpoint to send request to
        data: JSON data string
        data_file: JSON data file
    """
    # Get options from typer context
    ctx = typer.get_current_context()
    profile = ctx.params.get("profile")
    param = ctx.params.get("param", [])
    output_format = ctx.params.get("output_format", "json")
    output = ctx.params.get("output")

    # Create options object
    request_options = RequestOptions(
        profile=profile,
        params=param,
        output_format=output_format,
        output_file=output,
    )

    # Create client
    client = create_api_client(request_options.profile)

    # Parse parameters
    request_params = parse_key_value_params(request_options.params)

    # Get data
    json_data = None
    if data_file:
        try:
            with data_file.open() as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            raise JsonValidationError(JsonValidationError.DATA_FILE, e) from e
    elif data:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise JsonValidationError(JsonValidationError.DATA_STRING, e) from e

    # Make request
    console.print(f"Making POST request to: [bold]{endpoint}[/bold]")
    if request_params:
        console.print(f"Parameters: {request_params}")

    response = client.post(
        endpoint,
        params=request_params,
        json_data=json_data,
    )

    # Handle response
    if response.success:
        console.print(
            f"[green]Request successful (status: {response.status_code})[/green]",
        )

        # Format and output result
        formatted_output = format_output_data(
            response.data,
            request_options.output_format,
        )
        output_result(formatted_output, request_options.output_file)
    else:
        console.print(
            f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
        )
        raise typer.Exit(code=1)


def _get_extraction_error(entity: str) -> SchemaExtractionFailedError:
    """Create a schema extraction error for an entity.

    Args:
        entity: The entity name

    Returns:
        SchemaExtractionFailedError: The error object
    """
    return SchemaExtractionFailedError(entity)


def _get_entity_not_specified_error() -> SchemaEntityNotSpecifiedError:
    """Create entity not specified error.

    Returns:
        SchemaEntityNotSpecifiedError: The error object
    """
    return SchemaEntityNotSpecifiedError()


@schema_app.command("extract")
@handle_common_errors
def schema_extract(
    entity: Annotated[
        Optional[str],
        doctyper.Argument(help="Entity name to extract schema for"),
    ] = None,
    profile: Annotated[
        Optional[str],
        doctyper.Option(help="Configuration profile to use"),
    ] = None,
    output_dir: Annotated[Path, doctyper.Option(help="Schema cache directory")] = Path(
        "./schemas",
    ),
    *,  # Make remaining arguments keyword-only to fix FBT002
    extract_all: Annotated[
        bool,
        doctyper.Option(param_decls=["--all"], help="Extract all entity schemas"),
    ] = False,
) -> None:
    """Extract schema for an entity.

    Extracts JSON schema for a specific entity or for all entities
    and saves them to the specified directory.

    Args:
        entity: Entity name to extract schema for
        profile: Configuration profile to use
        output_dir: Directory to save extracted schemas
        extract_all: Extract schemas for all entities
    """
    # Create client
    client = create_api_client(profile)

    # Create schema manager
    schema_manager = apix.SchemaManager(client, cache_dir=str(output_dir))

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
            file_path = schema.save(str(output_dir))
            console.print(f"[green]Schema saved to: {file_path}[/green]")
        else:
            # Create the error and raise it
            error = _get_extraction_error(entity)
            raise error

    else:
        # Create the error and raise it
        error = _get_entity_not_specified_error()
        raise error


@schema_app.command("list")
@handle_common_errors
def schema_list(
    cache_dir: Annotated[Path, doctyper.Option(help="Schema cache directory")] = Path(
        "./schemas",
    ),
) -> None:
    """List available schemas.

    Lists all available JSON schemas found in the cache directory.

    Args:
        cache_dir: Directory containing cached schemas
    """
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


@schema_app.command("show")
@handle_common_errors
def schema_show(
    entity: Annotated[str, doctyper.Argument(help="Entity name to show schema for")],
    cache_dir: Annotated[Path, doctyper.Option(help="Schema cache directory")] = Path(
        "./schemas",
    ),
    output: Annotated[
        Optional[Path],
        doctyper.Option(param_decls=["--output", "-o"], help="Output file"),
    ] = None,
) -> None:
    """Show schema for an entity.

    Displays the JSON schema for a specific entity.

    Args:
        entity: Entity name to show schema for
        cache_dir: Directory containing cached schemas
        output: File to save output to
    """
    # Check cache directory
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        console.print(
            f"[yellow]Cache directory does not exist: {cache_dir}[/yellow]",
        )
        console.print("Run 'schema extract --all' to download schemas.")
        raise typer.Exit(code=1)

    # Find schema file
    schema_file = cache_path / f"{entity.lower()}.schema.json"
    if not schema_file.exists():
        console.print(f"[red]Schema file not found: {schema_file}[/red]")
        console.print(
            f"Run 'schema extract {entity}' to download the schema.",
        )
        raise typer.Exit(code=1)

    # Load and display schema
    schema = apix.SchemaManager.load_schema(schema_file)

    # Format as JSON and output
    formatted_output = format_output_data(schema.to_json_schema(), "json")

    if output:
        output_result(formatted_output, output)
    else:
        console.print(f"[bold]Schema for {entity}:[/bold]")
        console.print(formatted_output)


@dataclass
class EntityQueryOptions:
    """Options for entity queries with pagination and filtering."""

    profile: Optional[str] = None
    filters: Optional[list[str]] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    limit: Optional[int] = None
    offset: Optional[int] = None
    output_format: str = "json"
    output_file: Optional[Path] = None

    def __post_init__(self):
        if self.filters is None:
            self.filters = []


@dataclass
class EntityCommandOptions:
    """Options for entity command callback."""

    profile: Optional[str] = None
    output_format: str = "json"
    output_file: Optional[Path] = None
    filter_params: Optional[list[str]] = None
    sort: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: str = "asc"

    def __post_init__(self):
        if self.filter_params is None:
            self.filter_params = []


@entity_app.callback()
def entity_app_callback(  # noqa: PLR0913
    _profile: Annotated[  # Prefix with underscore to indicate intentionally unused
        Optional[str],
        doctyper.Option(help="Configuration profile to use"),
    ] = None,
    _output_format: Annotated[  # Prefix with underscore to indicate intentionally unused
        str,
        doctyper.Option(
            param_decls=["--format", "-f"],
            help="Output format",
            show_default=True,
            case_sensitive=False,
        ),
    ] = "json",
    _output: Annotated[  # Prefix with underscore to indicate intentionally unused
        Optional[Path],
        doctyper.Option(param_decls=["--output", "-o"], help="Output file"),
    ] = None,
    filter_params: Annotated[
        list[str],
        doctyper.Option(
            param_decls=["--filter", "-f"],
            help="Filter conditions (name=value)",
        ),
    ] = None,  # Use None instead of [] to avoid mutable default
    _sort: Annotated[
        Optional[str],
        doctyper.Option(help="Sort field"),
    ] = None,  # Prefix with underscore
    _limit: Annotated[  # Prefix with underscore
        Optional[int],
        doctyper.Option(help="Maximum number of results"),
    ] = None,
    _offset: Annotated[  # Prefix with underscore
        Optional[int],
        doctyper.Option(help="Starting position for pagination"),
    ] = None,
    _order: Annotated[
        str,
        doctyper.Option(help="Sort order"),
    ] = "asc",  # Prefix with underscore
) -> None:
    """Configure common options for entity commands.

    Args:
        _profile: Configuration profile to use
        _output_format: Format for displaying results
        _output: File to save output to
        filter_params: Filter conditions in name=value format
        _sort: Field to sort results by
        _limit: Maximum number of results to return
        _offset: Starting position for pagination
        _order: Sort order (asc or desc)
    """
    # Initialize mutable default
    if filter_params is None:
        filter_params = []


@entity_app.command("list")
@handle_common_errors
def entity_list(
    profile: Annotated[
        Optional[str],
        doctyper.Option(help="Configuration profile to use"),
    ] = None,
) -> None:
    """List available entities.

    Discovers and lists all available entities from the API.

    Args:
        profile: Configuration profile to use
    """
    # Create client
    client = create_api_client(profile)

    # Create entity manager
    entity_manager = apix.EntityManager(client)

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


@entity_app.command("get")
@handle_common_errors
def entity_get(
    entity: Annotated[str, doctyper.Argument(help="Entity name")],
    entity_id: Annotated[Optional[str], doctyper.Argument(help="Entity ID")] = None,
) -> None:
    """Get entity data.

    Retrieves data for a specific entity, either a single record by ID
    or a list of records with optional filtering and pagination.

    Args:
        entity: Entity name
        entity_id: Entity ID (retrieves a single entity if specified)
    """
    # Get options from typer context
    ctx = typer.get_current_context()
    profile = ctx.params.get("profile")
    filter_params = ctx.params.get("filter_params", [])
    sort = ctx.params.get("sort")
    order = ctx.params.get("order", "asc")
    limit = ctx.params.get("limit")
    offset = ctx.params.get("offset")
    output_format = ctx.params.get("output_format", "json")
    output = ctx.params.get("output")

    # Create options object
    options = EntityQueryOptions(
        profile=profile,
        filters=filter_params,
        sort_by=sort,
        sort_order=order,
        limit=limit,
        offset=offset,
        output_format=output_format,
        output_file=output,
    )

    # Create client
    client = create_api_client(options.profile)

    # Create entity manager
    entity_manager = apix.EntityManager(client)

    # Get entity
    entity_obj = entity_manager.get_entity(entity)

    # Parse filters
    filters = parse_key_value_params(options.filters, "filter")

    # Make request
    if entity_id:
        # Get single resource
        console.print(
            f"Getting {entity} with ID: [bold]{entity_id}[/bold]",
        )
        response = entity_obj.get(entity_id)
    else:
        # list resources
        console.print(f"Listing {entity} resources")
        if filters:
            console.print(f"Filters: {filters}")

        response = entity_obj.list(
            filters=filters,
            sort_by=options.sort_by,
            sort_order=options.sort_order,
            limit=options.limit,
            offset=options.offset,
        )

    # Handle response
    if response.success:
        console.print(
            f"[green]Request successful (status: {response.status_code})[/green]",
        )

        # Format and output result
        formatted_output = format_output_data(response.data, options.output_format)
        output_result(formatted_output, options.output_file)
    else:
        console.print(
            f"[red]Request failed (status: {response.status_code}): {response.error}[/red]",
        )
        raise typer.Exit(code=1)


def main() -> None:
    """Run the CLI application.

    Runs the CLI application with proper error handling and exit codes.
    """
    try:
        app()
    except apix.CLIError as e:
        console.print(f"[red]CLI error: {str(e)}[/red]")
        sys.exit(1)
    except apix.ApiConnectionError as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)
    except apix.BaseAPIError as e:
        console.print(f"[red]API error: {str(e)}[/red]")
        sys.exit(1)
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except Exception as e:  # noqa: BLE001
        # Keep broad exception handler for top-level function to catch all unexpected errors
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        if os.environ.get("PYAPIX_DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
