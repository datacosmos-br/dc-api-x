"""
Command-line interface for API X.

This module provides CLI commands for interacting with the API using Typer with doctyper
enhancement for better documentation and UI generation from Google-style docstrings.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, cast

import doctyper
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing_extensions import (  # or from typing import ... in newer versions
    TypeAliasType,
)

import dc_api_x as apix

from .utils import logging
from .utils.cli import (
    create_api_client,
    create_data_table,
    create_error_panel,
    create_info_panel,
    create_success_panel,
    create_tree_view,
    create_warning_panel,
    display_key_value_data,
    extract_common_options,
    extract_entity_options,
    format_output_data,
    get_entity_manager,
    get_schema_manager,
    handle_common_errors,
    log_operation,
    make_api_request,
    output_result,
    parse_key_value_params,
    run_with_spinner,
    show_welcome_banner,
    spinner_context,
    validate_directory,
)
from .utils.definitions import (
    EntityId,
    EntityName,
    JsonObject,
    LogLevel,
    OutputFormat,
    PageNumber,
    PageSize,
    PathLike,
    ProfileName,
    QueryParams,
)
from .utils.exceptions import (
    JsonValidationError,
    SchemaEntityNotSpecifiedError,
    SchemaExtractionFailedError,
)
from .utils.logging import create_cli_logger

# Doctyper type aliases
Alias = TypeAliasType("Alias", int)

# Set up logger
logger = create_cli_logger()

# Set up console for rich output
console = Console()

# Detyperão de constantes para doctyper a fim de evitar o erro B008
PROFILE_ARG = doctyper.Argument(None, help="Configuration profile to show")
PROFILE_OPT = doctyper.Option(None, help="Configuration profile to use")
SCHEMAS_DIR_OPT = doctyper.Option(Path("./schemas"), help="Schema cache directory")
OUTPUT_OPT = doctyper.Option(
    None,
    # param_decls=["--output", "-o"],
    help="Output file",
)
ENTITY_ARG = doctyper.Argument(help="Entity name to show schema for")
ENTITY_ID_ARG = doctyper.Argument(None, help="Entity ID")
ENDPOINT_ARG = doctyper.Argument(help="API endpoint")
ENTITY_EXTRACT_ARG = doctyper.Argument(
    default=None,
    help="Entity name to extract schema for",
)

# Opções para app_callback
VERSION_OPT = doctyper.Option(
    default=False,
    # param_decls=["--version"],
    help="Show version and exit",
    is_flag=True,
)
DEBUG_OPT = doctyper.Option(
    default=False,
    # param_decls=["--debug/--no-debug"],
    help="Enable debug output",
)

# Opções para request_app_callback
PARAM_OPT = doctyper.Option(
    default=None,
    # param_decls=["--param", "-p"],
    help="Query parameters (name=value)",
)
FORMAT_OPT = doctyper.Option(
    default="json",
    # param_decls=["--format", "-f"],
    help="Output format",
    show_default=True,
    case_sensitive=False,
)

# Opções para entity_app_callback
FILTER_OPT = doctyper.Option(
    default=None,
    # param_decls=["--filter", "-f"],
    help="Filter conditions (name=value)",
)
SORT_OPT = doctyper.Option(
    default=None,
    help="Sort field",
)
LIMIT_OPT = doctyper.Option(
    default=None,
    help="Maximum number of results",
)
OFFSET_OPT = doctyper.Option(
    default=None,
    help="Starting position for pagination",
)
ORDER_OPT = doctyper.Option(
    default="asc",
    help="Sort order",
)

# Opções para schema_extract
EXTRACT_ALL_OPT = doctyper.Option(
    default=False,
    # param_decls=["--all"],
    help="Extract all entity schemas",
)

# Opções para request_post
DATA_OPT = doctyper.Option(
    default=None,
    # param_decls=["--data", "-d"],
    help="JSON data string",
)
DATA_FILE_OPT = doctyper.Option(
    default=None,
    help="JSON data file",
)

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


@app.command("version")
def version_command() -> None:
    """Show the application version."""
    version_panel = Panel(
        f"API X CLI version: [bold cyan]{apix.__version__}[/bold cyan]",
        title="Version Information",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(version_panel)


@app.callback()
def app_callback(
    *,  # Make all arguments keyword-only to fix FBT002
    version: Annotated[bool, VERSION_OPT] = False,
    debug: Annotated[bool, DEBUG_OPT] = False,
) -> None:
    """Command-line interface for API X.

    Provides a hierarchical structure of commands and sub-commands for interacting
    with the API, with rich formatting and detailed help documentation.

    Args:
        version: Show application version and exit
        debug: Enable debug output
    """
    if version:
        doctyper.echo(f"API X CLI version: {apix.__version__}")
        raise doctyper.Exit()

    # Store debug flag
    state.debug = debug

    # Always set the level on the standard logger
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    if debug:
        logger.debug("Debug mode enabled")

    # Configure logging with Logfire
    log_level: LogLevel = "DEBUG" if debug else "INFO"
    try:
        # Initialize Logfire for CLI
        logging.setup_logging(
            service_name="dc-api-x-cli",
            level=log_level,
            local=True,  # Always use local logging for CLI
        )

        # Log initialization with context
        logging.info("CLI initialized", cli_version=apix.__version__, debug_mode=debug)
    except ImportError:
        # Already set up standard logging above, so no need to do it again
        pass


@config_app.command("list")
@handle_common_errors
def config_list() -> None:
    """List available configuration profiles.

    Displays all available configuration profiles found in the environment
    that can be used with the API client.
    """
    profiles = apix.list_available_profiles()

    # Log with Logfire
    logging.info("Listing configuration profiles", profile_count=len(profiles))

    if not profiles:
        no_profiles_text = Text("No configuration profiles found.", style="yellow")
        help_text = Text(
            "\nCreate .env.{profile} files to define profiles.",
            style="dim",
        )
        no_profiles_text.append(help_text)

        console.print(
            create_warning_panel(
                no_profiles_text,
                title="Configuration Profiles",
            ),
        )
    else:
        # Prepare data for table
        rows = [[profile, "Available"] for profile in sorted(profiles)]
        columns = [("Profile Name", "green"), ("Status", "cyan")]

        # Create and display table
        table = create_data_table(
            title="Available Configuration Profiles",
            columns=columns,
            rows=rows,
        )
        console.print(table)


@config_app.command("show")
@handle_common_errors
def config_show(
    profile: ProfileName = PROFILE_ARG,
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
    config_dict: JsonObject = {}
    config_dict = cast(JsonObject, cfg.to_dict())
    if "password" in config_dict:
        config_dict["password"] = "********"  # noqa: S105, B105 - placeholder password

    # Display the configuration
    title = f"Configuration{f' for profile: {profile}' if profile else ''}"
    display_key_value_data(config_dict, title=title)


@config_app.command("test")
@handle_common_errors
def config_test(
    profile: ProfileName = PROFILE_OPT,
) -> None:
    """Test API connection with configuration.

    Attempts to connect to the API using the specified configuration profile
    or the default configuration if no profile is specified.

    Args:
        profile: The configuration profile to use for testing
    """
    # Create client
    client = create_api_client(profile)

    title_text = Text()
    if profile:
        title_text.append("Testing connection with profile: ")
        title_text.append(profile, style="green bold")
    else:
        title_text.append("Testing connection with default configuration")

    console.print(title_text)

    # Use run_with_spinner to simplify the operation
    def test_connection():
        return client.test_connection()

    try:
        success, message = run_with_spinner(
            test_connection,
            message="Testing connection...",
            success_message="Connection test completed",
            error_message="Connection test failed",
        )

        # Display result
        if success:
            result_text = Text("✓ ", style="bold green")
            result_text.append(f"Connection successful: {message}", style="green")
            console.print(
                create_success_panel(
                    result_text,
                    title="Connection Test Result",
                ),
            )
        else:
            result_text = Text("✗ ", style="bold red")
            result_text.append(f"Connection failed: {message}", style="red")
            console.print(
                create_error_panel(
                    result_text,
                    title="Connection Test Result",
                ),
            )
            raise doctyper.Exit(code=1)
    except Exception:
        raise doctyper.Exit(code=1)


@dataclass
class RequestOptions:
    """Common options for API requests."""

    profile: ProfileName | None = None
    params: list[str] | None = None
    output_format: OutputFormat = "json"
    output_file: PathLike | None = None

    def __post_init__(self) -> None:
        if self.params is None:
            self.params = []


@request_app.callback()
def request_app_callback(
    _profile: ProfileName = PROFILE_OPT,
    param: list[str] = PARAM_OPT,
    _output_format: OutputFormat = FORMAT_OPT,
    _output: PathLike = OUTPUT_OPT,
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

    # Options are handled by doctyper and passed to command functions


@request_app.command("get")
@handle_common_errors
def request_get(
    endpoint: str = ENDPOINT_ARG,
) -> None:
    """Make GET request to API endpoint.

    Sends a GET request to the specified API endpoint with optional
    query parameters and formats the response according to the output
    format setting.

    Args:
        endpoint: The API endpoint to send the request to
    """
    # Extract options from context
    options = extract_common_options()
    profile: ProfileName | None = options.get("profile")
    output_format: OutputFormat = options.get("output_format", "json")
    output_file: PathLike | None = options.get("output_file")

    # Get parameters from context
    ctx = doctyper.get_current_context()
    param_list: list[str] = ctx.params.get("param", [])

    # Create client
    client = create_api_client(profile)

    # Parse parameters
    params: QueryParams = parse_key_value_params(param_list)

    # Log request with Logfire
    log_operation(
        "Making GET request",
        endpoint=endpoint,
        parameters=params,
        profile=profile,
    )

    # Show request information
    request_info = f"Endpoint: [bold]{endpoint}[/bold]\n"
    request_info += f"Parameters: {params}" if params else "No parameters"
    console.print(create_info_panel(request_info, title="API Request"))

    # Make the request with standardized helper
    make_api_request(
        method=client.get,
        description=f"Making GET request to {endpoint}",
        success_title="GET Request Successful",
        error_title="GET Request Failed",
        display_data=True,
        output_format=output_format,
        output_file=output_file,
        endpoint=endpoint,
        params=params,
    )


@request_app.command("post")
@handle_common_errors
def request_post(
    endpoint: str = ENDPOINT_ARG,
    data: str = DATA_OPT,
    data_file: PathLike = DATA_FILE_OPT,
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
    # Get options from doctyper context
    ctx = doctyper.get_current_context()
    profile: ProfileName | None = ctx.params.get("profile")
    param: list[str] = ctx.params.get("param", [])
    output_format: str = ctx.params.get("output_format", "json")
    output: PathLike | None = ctx.params.get("output")

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
    request_params: QueryParams = parse_key_value_params(request_options.params)

    # Get data
    json_data: JsonObject | None = None
    if data_file:
        try:
            with Path(data_file).open() as f:
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
        raise doctyper.Exit(code=1)


def _get_extraction_error(entity: EntityName) -> SchemaExtractionFailedError:
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
    entity: EntityName = ENTITY_EXTRACT_ARG,
    profile: ProfileName = PROFILE_OPT,
    output_dir: PathLike = SCHEMAS_DIR_OPT,
    *,  # Make remaining arguments keyword-only to fix FBT002
    extract_all: bool = EXTRACT_ALL_OPT,
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
    # Validate and create output directory if it doesn't exist
    output_path = validate_directory(output_dir, create=True)

    # Get schema manager
    schema_manager = get_schema_manager(profile, cache_dir=str(output_path))

    # Log operation
    log_operation(
        "Extracting schemas",
        entity=entity,
        extract_all=extract_all,
        output_dir=str(output_path),
        profile=profile,
    )

    if extract_all:
        # Extract all schemas with spinner
        with spinner_context("Extracting schemas for all entities") as _:
            schemas = schema_manager.extract_all_schemas()

        if not schemas:
            console.print(create_warning_panel("No schemas found."))
            return

        # Show success message
        success_message = (
            f"Successfully extracted {len(schemas)} schemas to {output_dir}"
        )
        console.print(create_success_panel(success_message))

        # Prepare data for tree view
        extracted_schemas = {}

        # Group schemas by status (success/failure)
        successful = []
        failed = []

        for name, schema in schemas.items():
            if schema:
                successful.append(name)
            else:
                failed.append(name)

        if successful:
            extracted_schemas["Successful"] = successful
        if failed:
            extracted_schemas["Failed"] = failed

        # Display as tree
        tree = create_tree_view(
            root_label=f"Extracted Schemas ({len(schemas)})",
            items=extracted_schemas,
            category_style="yellow bold",
            item_style="green",
        )
        console.print(tree)

    elif entity:
        # Extract specific schema
        info_message = f"Extracting schema for entity: [bold]{entity}[/bold]"
        console.print(create_info_panel(info_message))

        # Use run_with_spinner for the extraction
        try:
            schema = run_with_spinner(
                schema_manager.get_schema,
                message=f"Extracting schema for {entity}",
                success_message=f"Schema extracted for {entity}",
                error_message=f"Failed to extract schema for {entity}",
                entity=entity,
            )

            if schema:
                file_path = schema.save(str(output_path))
                console.print(create_success_panel(f"Schema saved to: {file_path}"))
            else:
                # Create the error and raise it
                error = _get_extraction_error(entity)
                raise error
        except Exception as e:
            console.print(create_error_panel(f"Schema extraction failed: {str(e)}"))
            raise

    else:
        # Create the error and raise it
        error = _get_entity_not_specified_error()
        raise error


@schema_app.command("list")
@handle_common_errors
def schema_list(
    cache_dir: PathLike = SCHEMAS_DIR_OPT,
) -> None:
    """List available schemas.

    Lists all available JSON schemas found in the cache directory.

    Args:
        cache_dir: Directory containing cached schemas
    """
    # Check cache directory
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        warning_message = (
            f"Cache directory does not exist: {cache_dir}\n"
            "Run 'schema extract --all' to download schemas."
        )
        console.print(
            create_warning_panel(
                warning_message,
                title="Schema Cache Not Found",
            ),
        )
        return

    # list schema files
    schema_files = list(cache_path.glob("*.schema.json"))

    if not schema_files:
        warning_message = (
            f"No schema files found in: {cache_dir}\n"
            "Run 'schema extract --all' to download schemas."
        )
        console.print(
            create_warning_panel(
                warning_message,
                title="No Schemas Found",
            ),
        )
        return

    # Organize schemas by category
    schema_by_category = {}

    for file_path in sorted(schema_files):
        name = file_path.stem
        if name.endswith(".schema"):
            name = name[:-7]

        # Try to identify categories by prefixes (optional)
        parts = name.split("_", 1)
        if len(parts) > 1 and parts[0]:
            category = parts[0].upper()
            schema_name = parts[1]

            if category not in schema_by_category:
                schema_by_category[category] = []

            schema_by_category[category].append((schema_name, name))
        else:
            if "GENERAL" not in schema_by_category:
                schema_by_category["GENERAL"] = []

            schema_by_category["GENERAL"].append((name, name))

    # Convert to format needed by create_tree_view
    tree_data = {}
    for category, schemas in schema_by_category.items():
        tree_data[category] = [name for name, _ in sorted(schemas)]

    # Create and display tree view
    tree = create_tree_view(
        root_label=f"Available Schemas ({len(schema_files)})",
        items=tree_data,
    )
    console.print(tree)


@schema_app.command("show")
@handle_common_errors
def schema_show(
    entity: EntityName = ENTITY_ARG,
    cache_dir: PathLike = SCHEMAS_DIR_OPT,
    output: PathLike = OUTPUT_OPT,
) -> None:
    """Show schema for an entity.

    Displays the JSON schema for a specific entity, either from the cache
    or by fetching it from the API if not found in the cache.

    Args:
        entity: Entity name to show schema for
        cache_dir: Directory containing cached schemas
        output: File to save schema to
    """
    # Check cache directory
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        console.print(
            f"[yellow]Cache directory does not exist: {cache_dir}[/yellow]",
        )
        console.print("Run 'schema extract --all' to download schemas.")
        raise doctyper.Exit(code=1)

    # Find schema file
    schema_file = cache_path / f"{entity.lower()}.schema.json"
    if not schema_file.exists():
        console.print(f"[red]Schema file not found: {schema_file}[/red]")
        console.print(
            f"Run 'schema extract {entity}' to download the schema.",
        )
        raise doctyper.Exit(code=1)

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

    profile: ProfileName | None = None
    filters: list[str] | None = None
    sort_by: str | None = None
    sort_order: str = "asc"
    limit: PageSize | None = None
    offset: PageNumber | None = None
    output_format: OutputFormat = "json"
    output_file: PathLike | None = None

    def __post_init__(self) -> None:
        if self.filters is None:
            self.filters = []


@dataclass
class EntityCommandOptions:
    """Options for entity command callback."""

    profile: ProfileName | None = None
    output_format: OutputFormat = "json"
    output_file: PathLike | None = None
    filter_params: list[str] | None = None
    sort: str | None = None
    limit: PageSize | None = None
    offset: PageNumber | None = None
    order: str = "asc"

    def __post_init__(self) -> None:
        if self.filter_params is None:
            self.filter_params = []


@entity_app.callback()
def entity_app_callback(  # noqa: PLR0913
    _profile: ProfileName = PROFILE_OPT,
    _output_format: OutputFormat = FORMAT_OPT,
    _output: PathLike = OUTPUT_OPT,
    filter_params: list[str] = FILTER_OPT,
    _sort: str = SORT_OPT,
    _limit: PageSize = LIMIT_OPT,
    _offset: PageNumber = OFFSET_OPT,
    _order: str = ORDER_OPT,
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
    profile: ProfileName = PROFILE_OPT,
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

    # Display operation message
    console.print(
        create_info_panel(
            "Discovering available entities from API...",
            title="Entity Discovery",
        ),
    )

    # Use spinner_context for the operation
    with spinner_context("Discovering entities...") as _:
        entities = entity_manager.discover_entities()

    if not entities:
        console.print(
            create_warning_panel(
                "No entities found in the API.",
                title="No Entities Found",
            ),
        )
        return

    # Prepare data for table
    rows = []
    for name in sorted(entities):
        # Try to determine type based on name (optional)
        entity_type = name.split("_", 1)[0].upper() if "_" in name else "ENTITY"
        rows.append([name, entity_type])

    columns = [("Entity Name", "green"), ("Type", "cyan")]

    # Create and display table
    table = create_data_table(
        title=f"Available Entities ({len(entities)})",
        columns=columns,
        rows=rows,
    )
    console.print(table)


@entity_app.command("get")
@handle_common_errors
def entity_get(
    entity: EntityName = ENTITY_ARG,
    entity_id: EntityId = ENTITY_ID_ARG,
) -> None:
    """Get entity data.

    Retrieves data for a specific entity, either a single record by ID
    or a list of records with optional filtering and pagination.

    Args:
        entity: Entity name
        entity_id: Entity ID (retrieves a single entity if specified)
    """
    # Extract options from context
    options = extract_entity_options()

    # Get entity manager
    entity_manager = get_entity_manager(options["profile"])

    # Get entity
    entity_obj = entity_manager.get_entity(entity)

    # Log operation
    log_operation(
        "Getting entity data",
        entity=entity,
        entity_id=entity_id,
        filters=options.get("filters"),
        profile=options["profile"],
    )

    if entity_id:
        # Get single resource
        description = f"Getting {entity} with ID: {entity_id}"
        console.print(create_info_panel(description))

        # Make request with our helper
        make_api_request(
            method=entity_obj.get,
            description=f"Fetching {entity}",
            success_title=f"{entity.title()} Retrieved",
            error_title=f"Failed to retrieve {entity}",
            output_format=options["output_format"],
            output_file=options["output_file"],
            entity_id=entity_id,
        )
    else:
        # List resources
        description = f"Listing {entity} resources"
        if options.get("filters"):
            description += f"\nFilters: {options['filters']}"
        console.print(create_info_panel(description))

        # Make request with our helper
        make_api_request(
            method=entity_obj.list,
            description=f"Fetching {entity} list",
            success_title=f"{entity.title()} List Retrieved",
            error_title=f"Failed to list {entity}",
            output_format=options["output_format"],
            output_file=options["output_file"],
            filters=options.get("filters", {}),
            sort_by=options.get("sort_by"),
            sort_order=options.get("sort_order", "asc"),
            limit=options.get("limit"),
            offset=options.get("offset"),
        )


def main() -> None:
    """Run the CLI application.

    Runs the CLI application with proper error handling and exit codes.
    """
    try:
        # Verifica se não há argumentos e exibe um banner informativo
        if len(sys.argv) == 1:
            show_welcome_banner()

        app()
    except apix.CLIError as e:
        console.print(
            Panel(
                Text(f"{str(e)}", style="red"),
                title="CLI Error",
                border_style="red",
                padding=(1, 2),
            ),
        )
        sys.exit(1)
    except apix.ApiConnectionError as e:
        console.print(
            Panel(
                Text(f"{str(e)}", style="red"),
                title="Connection Error",
                border_style="red",
                padding=(1, 2),
            ),
        )
        sys.exit(1)
    except apix.BaseAPIError as e:
        console.print(
            Panel(
                Text(f"{str(e)}", style="red"),
                title="API Error",
                border_style="red",
                padding=(1, 2),
            ),
        )
        sys.exit(1)
    except doctyper.Exit as e:
        sys.exit(e.exit_code)
    except Exception as e:  # noqa: BLE001
        # Keep broad exception handler for top-level function to catch all unexpected errors
        error_panel = Panel(
            Text(f"{str(e)}", style="red"),
            title="Unexpected Error",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)

        if os.environ.get("PYAPIX_DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            console.print(
                Panel(
                    traceback.format_exc(),
                    title="Debug Traceback",
                    border_style="red",
                    padding=(1, 2),
                ),
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
