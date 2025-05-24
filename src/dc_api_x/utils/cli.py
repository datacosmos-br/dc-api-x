"""
CLI helper functions for DCApiX.

This module provides utility functions for CLI operations, such as
configuration file handling, environment loading, and output formatting.
"""

import contextlib
import functools
import json
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, cast

import doctyper as typer
import dotenv
from doctyper import Context
from rich import box as rich_box  # Added for compatibility with existing code
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

if TYPE_CHECKING:
    import dc_api_x as apix
    from dc_api_x.client import ApiClient, ApiResponse
    from dc_api_x.entity import EntityManager
    from dc_api_x.schema import SchemaManager
else:
    import dc_api_x as apix

from dc_api_x.utils import logging
from dc_api_x.utils.definitions import (
    ConfigDict,
    OutputFormat,
    PathLike,
    ProfileName,
    QueryParams,
    ResponseData,
)
from dc_api_x.utils.exceptions import (
    ConfigFileNotFoundError,
    DirectoryNotFoundError,
    FilePathNotDirectoryError,
    InvalidOutputFormatError,
    InvalidParameterFormatError,
    JsonValidationError,
    MissingEnvironmentVariableError,
    UnsupportedJsonTypeError,
)

# Type aliases for improved readability
JsonObject = dict[str, Any]

# Console for rich output
console = Console()

# Type variables for function decorators
T = TypeVar("T")


def show_welcome_banner() -> None:
    """Display a welcome banner with usage information."""
    # Cria um banner atraente para a aplicação
    banner = Text("\n")
    banner.append("╔═══════════════════════════════════════╗\n", style="cyan")
    banner.append("║              ", style="cyan")
    banner.append("API X CLI", style="bold cyan")
    banner.append("              ║\n", style="cyan")
    banner.append("╚═══════════════════════════════════════╝\n", style="cyan")

    # Adiciona informações de versão e uso
    banner.append("\nVersion: ", style="dim")
    banner.append(apix.__version__, style="bold blue")

    banner.append("\n\nUsage Examples:\n", style="yellow")
    banner.append("  • List configuration profiles: ", style="green dim")
    banner.append("config list\n", style="bold white")
    banner.append("  • Test API connection: ", style="green dim")
    banner.append("config test\n", style="bold white")
    banner.append("  • List available entities: ", style="green dim")
    banner.append("entity list\n", style="bold white")
    banner.append("  • Get entity data: ", style="green dim")
    banner.append("entity get <entity_name>\n", style="bold white")
    banner.append("  • Make API request: ", style="green dim")
    banner.append("request get <endpoint>\n", style="bold white")

    banner.append("\nFor more information, use the ", style="dim")
    banner.append("--help", style="bold white")
    banner.append(" flag with any command.\n", style="dim")

    # Exibe o banner em um painel
    console.print(
        Panel(
            banner,
            title="Welcome to API X CLI",
            border_style="blue",
            padding=(1, 2),
        ),
    )


def handle_common_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to handle common errors in CLI commands.

    This decorator catches common exceptions and displays them in a user-friendly way,
    with appropriate exit codes.

    Args:
        func: The function to decorate

    Returns:
        Decorated function that handles common errors
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except apix.ConfigError as e:
            console.print(f"[red]Configuration error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except apix.AuthenticationError as e:
            console.print(f"[red]Authentication error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except apix.ApiConnectionError as e:
            console.print(f"[red]Connection error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except apix.ValidationError as e:
            console.print(f"[red]Validation error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except apix.NotFoundError as e:
            console.print(f"[red]Not found: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except apix.CLIError as e:
            console.print(f"[red]CLI error: {str(e)}[/red]")
            raise typer.Exit(code=1) from e
        except Exception as e:  # noqa: BLE001
            # We want a broad exception handler for a decorator that's specifically for handling errors
            console.print(f"[red]Error: {str(e)}[/red]")
            if os.environ.get("DCAPIX_DEBUG", "").lower() in ("1", "true", "yes"):
                import traceback

                console.print(traceback.format_exc())
            raise typer.Exit(code=1) from e

    return wrapper


def resolve_config_file(config_file_path: PathLike | None = None) -> Path:
    """
    Resolve a configuration file path.

    This function handles converting relative paths to absolute,
    checking if the file exists, and providing default paths.

    Args:
        config_file_path: Path to the config file (optional)

    Returns:
        Path: Resolved absolute path to the config file

    Raises:
        ConfigFileNotFoundError: If the file does not exist
    """
    # If no path provided, use default
    if config_file_path is None:
        # Check for file in current directory
        default_path = Path.cwd() / ".dcapix.json"
        if default_path.exists():
            return default_path

        # Check for file in user's home directory
        home_path = Path.home() / ".dcapix" / "config.json"
        if home_path.exists():
            return home_path

        # If none found, return default location for creation
        return default_path

    # Convert to Path if string
    path = Path(config_file_path)

    # Make absolute if relative
    if not path.is_absolute():
        path = Path.cwd() / path

    # Check if file exists
    if not path.exists():
        raise ConfigFileNotFoundError(path)

    return path


def parse_json_data(data: str | Path) -> JsonObject:
    """
    Parse JSON data from a string or file.

    Args:
        data: JSON string or path to JSON file

    Returns:
        dict: Parsed JSON data

    Raises:
        JsonValidationError: If the JSON is invalid
    """
    # Handle file path
    if isinstance(data, str | Path) and (
        str(data).endswith(".json") or Path(data).is_file()
    ):
        path = Path(data)
        try:
            with path.open() as f:
                try:
                    return cast(JsonObject, json.load(f))
                except json.JSONDecodeError as e:
                    # Pass file path as source
                    raise JsonValidationError(str(path), e) from e
        except OSError as e:
            # Pass file path as source
            raise JsonValidationError(str(path), e) from e

    # Handle JSON string
    if isinstance(data, str):
        try:
            return cast(JsonObject, json.loads(data))
        except json.JSONDecodeError as e:
            # Pass "data string" as source
            raise JsonValidationError(JsonValidationError.DATA_STRING, e) from e

    # If we got here, the input is not a valid JSON string or file
    raise UnsupportedJsonTypeError(type(data).__name__)


def create_client_from_env(
    env_file: PathLike | None = None,
    env_prefix: str = "DCAPIX_",
) -> "ApiClient":
    """
    Create a client instance from environment variables.

    This function loads environment variables from a .env file and
    creates a client instance using those variables.

    Args:
        env_file: Path to .env file (optional)
        env_prefix: Prefix for environment variables (default: DCAPIX_)

    Returns:
        ApiClient: Configured client instance

    Raises:
        MissingEnvironmentVariableError: If required environment variables are missing
    """
    # Load environment variables from file if provided
    if env_file:
        dotenv.load_dotenv(env_file)

    # Get required variables
    url = os.environ.get(f"{env_prefix}URL")
    username = os.environ.get(f"{env_prefix}USERNAME")
    password = os.environ.get(f"{env_prefix}PASSWORD")

    # Check required variables
    if not url:
        raise MissingEnvironmentVariableError("URL", env_prefix)
    if not username:
        raise MissingEnvironmentVariableError("USERNAME", env_prefix)
    if not password:
        raise MissingEnvironmentVariableError("PASSWORD", env_prefix)

    # Get optional variables
    timeout = os.environ.get(f"{env_prefix}TIMEOUT")
    verify_ssl = os.environ.get(f"{env_prefix}VERIFY_SSL")

    # Create client config
    config: ConfigDict = {
        "url": url,
        "username": username,
        "password": password,
    }

    # Add optional config
    if timeout:
        with contextlib.suppress(ValueError):
            config["timeout"] = int(timeout)
    if verify_ssl is not None:
        config["verify_ssl"] = verify_ssl.lower() in ("true", "1", "yes")

    # Create and return client
    return ApiClient(**config)


def create_api_client(profile: ProfileName | None = None) -> "ApiClient":
    """
    Create an API client instance with the given profile.

    Args:
        profile: Configuration profile to use

    Returns:
        ApiClient: Configured client instance
    """
    if profile:
        # Create configuration from profile
        return ApiClient.from_profile(profile)
    # Create configuration from environment variables
    return create_client_from_env()


def parse_key_value_params(params: list[str], param_type: str = "param") -> QueryParams:
    """
    Parse a list of key=value parameters into a dictionary.

    Args:
        params: List of strings in "key=value" format
        param_type: Parameter type for error messages (default: "param")

    Returns:
        dict: Dictionary of parsed parameters

    Raises:
        InvalidParameterFormatError: If a parameter is not in the correct format
    """
    result: QueryParams = {}
    for param in params:
        if "=" not in param:
            raise InvalidParameterFormatError(param, param_type)

        key, value = param.split("=", 1)
        result[key] = value

    return result


def format_output_data(data: ResponseData, output_format: OutputFormat = "json") -> str:
    """
    Format data in the specified output format.

    Args:
        data: Data to format
        output_format: Output format (json, yaml, etc.)

    Returns:
        str: Formatted data as string

    Raises:
        InvalidOutputFormatError: If the output format is not supported
    """
    if output_format.lower() == "json":
        return json.dumps(data, indent=2)
    raise InvalidOutputFormatError(output_format)


def output_result(formatted_output: str, output_file: PathLike | None = None) -> None:
    """
    Output the formatted result to a file or stdout.

    Args:
        formatted_output: Formatted data as string
        output_file: Output file path (optional)
    """
    if output_file:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            f.write(formatted_output)
        print(f"Output saved to {path}")
    else:
        print(formatted_output)


# New helper functions for Rich UI


def create_info_panel(message: str | Text, title: str = "Information") -> Panel:
    """
    Create an informational panel with Rich.

    Args:
        message: Message to display in the panel
        title: Panel title (default: "Information")

    Returns:
        Panel: Rich Panel object
    """
    return Panel(
        message,
        title=title,
        border_style="blue",
        padding=(1, 2),
    )


def create_success_panel(message: str | Text, title: str = "Success") -> Panel:
    """
    Create a success panel with Rich.

    Args:
        message: Message to display in the panel
        title: Panel title (default: "Success")

    Returns:
        Panel: Rich Panel object
    """
    if isinstance(message, str):
        text = Text("✓ ", style="bold green")
        text.append(message, style="green")
        message = text

    return Panel(
        message,
        title=title,
        border_style="green",
        padding=(1, 2),
    )


def create_error_panel(message: str | Text, title: str = "Error") -> Panel:
    """
    Create an error panel with Rich.

    Args:
        message: Error message to display in the panel
        title: Panel title (default: "Error")

    Returns:
        Panel: Rich Panel object
    """
    if isinstance(message, str):
        text = Text("✗ ", style="bold red")
        text.append(message, style="red")
        message = text

    return Panel(
        message,
        title=title,
        border_style="red",
        padding=(1, 2),
    )


def create_warning_panel(message: str | Text, title: str = "Warning") -> Panel:
    """
    Create a warning panel with Rich.

    Args:
        message: Warning message to display in the panel
        title: Panel title (default: "Warning")

    Returns:
        Panel: Rich Panel object
    """
    if isinstance(message, str):
        text = Text("! ", style="bold yellow")
        text.append(message, style="yellow")
        message = text

    return Panel(
        message,
        title=title,
        border_style="yellow",
        padding=(1, 2),
    )


def create_data_table(
    title: str,
    columns: list[tuple[str, str]],
    rows: list[list[Any]],
    box_style: str = "ROUNDED",
) -> Table:
    """
    Create a formatted data table with Rich.

    Args:
        title: Table title
        columns: List of (column_name, column_style) tuples
        rows: List of row data (list of values)
        box_style: Table box style (default: "ROUNDED")

    Returns:
        Table: Rich Table object
    """
    box_styles = {
        "ROUNDED": rich_box.ROUNDED,
        "SIMPLE": rich_box.SIMPLE,
        "MINIMAL": rich_box.MINIMAL,
        "SQUARE": rich_box.SQUARE,
    }

    selected_box = box_styles.get(box_style.upper(), rich_box.ROUNDED)

    table = Table(
        title=title,
        box=selected_box,
        highlight=True,
        show_header=True,
        border_style="blue",
    )

    # Add columns
    for col_name, col_style in columns:
        table.add_column(col_name, style=col_style)

    # Add rows
    for row in rows:
        table.add_row(*[str(item) for item in row])

    return table


@contextlib.contextmanager
def spinner_context(message: str = "Processing...") -> Any:
    """
    Context manager for displaying a spinner during operations.

    Args:
        message: Message to display next to the spinner

    Yields:
        Progress: Rich Progress object
    """
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{message}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("", total=None)  # Indeterminate spinner
        yield progress


def display_key_value_data(data: dict[str, Any], title: str = "Data") -> None:
    """
    Display a dictionary as key-value pairs in a table.

    Args:
        data: Dictionary to display
        title: Table title
    """
    table = Table(
        title=title,
        box=rich_box.ROUNDED,
        highlight=True,
        show_header=True,
        border_style="blue",
    )

    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        # Format special values
        if isinstance(value, dict | list):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)

        table.add_row(key, value_str)

    console.print(table)


def get_typer_context_params() -> dict[str, Any]:
    """
    Get parameters from the current Typer context.

    Returns:
        dict: Dictionary of parameters from the current context
    """
    try:
        ctx = Context.get_current()
        if ctx is None:
            return {}
        return dict(ctx.params)
    except Exception:  # noqa: BLE001
        # No active context or other context access error
        return {}


class CliContext(Generic[T]):
    """
    Context manager for CLI operations with progress indication.

    Provides a standardized way to show progress, success, and error states
    for CLI operations.
    """

    def __init__(
        self,
        operation_name: str,
        success_message: str,
        error_message: str = "Operation failed",
    ):
        """
        Initialize a CLI operation context.

        Args:
            operation_name: Name of the operation (shown during progress)
            success_message: Message to show on success
            error_message: Message to show on error
        """
        self.operation_name = operation_name
        self.success_message = success_message
        self.error_message = error_message
        self.result: T | None = None

    def __enter__(self) -> "CliContext[T]":
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]{self.operation_name}..."),
            console=console,
            transient=True,
        )
        self.progress.start()
        self.task = self.progress.add_task("", total=None)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> Literal[False]:
        self.progress.stop()

        if exc_type is None:
            # Operation succeeded
            console.print(create_success_panel(self.success_message))
            return False

        # Operation failed
        if isinstance(exc_val, Exception):
            error_msg = f"{self.error_message}: {str(exc_val)}"
        else:
            error_msg = self.error_message

        console.print(create_error_panel(error_msg))
        return False  # Don't suppress the exception

    def set_result(self, result: T) -> None:
        """
        Set the operation result.

        Args:
            result: Operation result
        """
        self.result = result


def create_tree_view(
    root_label: str,
    items: dict[str, Sequence[str]],
    root_style: str = "bold cyan",
    category_style: str = "yellow bold",
    item_style: str = "green",
) -> Tree:
    """
    Create a tree view of hierarchical data.

    Args:
        root_label: Label for the root node
        items: Dictionary mapping category names to lists of items
        root_style: Style for the root node
        category_style: Style for category nodes
        item_style: Style for item nodes

    Returns:
        Tree: Rich Tree object
    """
    tree = Tree(
        Text(root_label, style=root_style),
        guide_style="blue",
    )

    for category, category_items in sorted(items.items()):
        category_node = tree.add(Text(category, style=category_style))

        for item in sorted(category_items):
            category_node.add(Text(item, style=item_style))

    return tree


def run_with_spinner(
    func: Callable[..., T],
    message: str,
    success_message: str,
    error_message: str = "Operation failed",
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Run a function with a spinner, showing success or error messages.

    Args:
        func: Function to run
        message: Message to display during operation
        success_message: Message to display on success
        error_message: Message to display on error
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        T: Function result

    Raises:
        Exception: Any exception raised by the function
    """
    with spinner_context(message):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            console.print(create_error_panel(f"{error_message}: {str(e)}"))
            raise
        else:
            console.print(create_success_panel(success_message))
            return result


# Additional helper functions for API interactions


def get_entity_manager(profile: ProfileName | None = None) -> "EntityManager":
    """
    Create an entity manager instance with the given profile.

    Args:
        profile: Configuration profile to use

    Returns:
        EntityManager: Configured entity manager instance
    """
    client = create_api_client(profile)
    return apix.EntityManager(client)


def get_schema_manager(
    profile: ProfileName | None = None,
    cache_dir: PathLike = "./schemas",
) -> "SchemaManager":
    """
    Create a schema manager instance with the given profile and cache directory.

    Args:
        profile: Configuration profile to use
        cache_dir: Directory for schema caching

    Returns:
        SchemaManager: Configured schema manager instance
    """
    client = create_api_client(profile)
    return apix.SchemaManager(client, cache_dir=str(cache_dir))


def confirm_action(
    message: str,
    abort_message: str = "Operation aborted by user.",
) -> bool:
    """
    Ask the user to confirm an action.

    Args:
        message: Message to display in the confirmation prompt
        abort_message: Message to display if the user aborts

    Returns:
        bool: True if confirmed, False otherwise
    """
    try:
        confirmed = typer.confirm(message)
        if not confirmed:
            console.print(create_warning_panel(abort_message))
            return False
        # We can't use else here as it triggers RET505, but without it we get TRY300
        return True  # noqa: TRY300
    except typer.Abort:
        console.print(create_warning_panel(abort_message))
        return False


def validate_directory(
    path: PathLike,
    *,  # Make create parameter keyword-only
    create: bool = False,
    error_message: str = "Directory does not exist",
) -> Path:
    """
    Validate that a directory exists and optionally create it if it doesn't.

    Args:
        path: Directory path to validate
        create: Whether to create the directory if it doesn't exist
        error_message: Error message if directory doesn't exist and create is False

    Returns:
        Path: Validated directory path

    Raises:
        DirectoryNotFoundError: If directory doesn't exist and create is False
        FilePathNotDirectoryError: If path exists but is not a directory
    """
    dir_path = Path(path)
    if not dir_path.exists():
        if create:
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(create_info_panel(f"Created directory: {dir_path}"))
        else:
            raise DirectoryNotFoundError(dir_path, error_message)
    elif not dir_path.is_dir():
        raise FilePathNotDirectoryError(dir_path)

    return dir_path


# Using dataclasses to avoid too many arguments in function definitions
@dataclass
class ApiRequestOptions:
    """Options for API requests."""

    method: Callable[..., "ApiResponse"]
    description: str
    kwargs: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class ApiResponseOptions:
    """Options for handling API responses."""

    success_title: str = "Success"
    error_title: str = "Error"
    display_data: bool = True
    output_format: OutputFormat = "json"
    output_file: PathLike | None = None


# Splitting the make_api_request into smaller functions to avoid too many arguments
def _prepare_api_request(options: ApiRequestOptions) -> "ApiResponse":
    """
    Execute an API request with a spinner.

    Args:
        options: API request options

    Returns:
        ApiResponse: API response
    """
    with spinner_context(f"{options.description}...") as _:
        if options.kwargs is None:
            return options.method()
        return options.method(**options.kwargs)


def _handle_api_response(
    response: "ApiResponse",
    options: ApiResponseOptions,
) -> "ApiResponse":
    """
    Handle API response with appropriate success or error messages.

    Args:
        response: API response to handle
        options: Response handling options

    Returns:
        ApiResponse: The original API response

    Raises:
        typer.Exit: If the request failed
    """
    success = getattr(response, "success", False)
    if success:
        status_msg = f"Request successful (status: {response.status_code})"
        console.print(create_success_panel(status_msg, title=options.success_title))

        if options.display_data:
            formatted_output = format_output_data(response.data, options.output_format)
            if options.output_file:
                output_result(formatted_output, options.output_file)
            else:
                # Display data in a panel if not sending to a file
                console.print(
                    create_info_panel(
                        formatted_output,
                        title="Response Data",
                    ),
                )

        return response

    # Handle error
    error_msg = f"Request failed (status: {response.status_code}): {response.error}"
    console.print(create_error_panel(error_msg, title=options.error_title))
    raise typer.Exit(code=1)


# Using a dataclass to encapsulate make_api_request parameters
@dataclass
class ApiRequestConfig:
    """Configuration for API requests."""

    method: Callable[..., "ApiResponse"]
    description: str
    success_title: str = "Success"
    error_title: str = "Error"
    display_data: bool = True
    output_format: OutputFormat = "json"
    output_file: PathLike | None = None
    kwargs: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.kwargs is None:
            self.kwargs = {}


def make_api_request_with_config(config: ApiRequestConfig) -> "ApiResponse":
    """
    Make an API request with standard error handling and output formatting.

    Args:
        config: Complete API request configuration

    Returns:
        ApiResponse: API response

    Raises:
        typer.Exit: If the request fails
    """
    request_options = ApiRequestOptions(
        method=config.method,
        description=config.description,
        kwargs=config.kwargs if config.kwargs is not None else {},
    )
    response_options = ApiResponseOptions(
        success_title=config.success_title,
        error_title=config.error_title,
        display_data=config.display_data,
        output_format=config.output_format,
        output_file=config.output_file,
    )
    response = _prepare_api_request(request_options)
    return _handle_api_response(response, response_options)


# Main API request function - using forwarding to avoid PLR0913
def make_api_request(
    method: Callable[..., "ApiResponse"],
    description: str,
    **kwargs: Any,
) -> "ApiResponse":
    """
    Make an API request with standard error handling and output formatting.

    This is a simplified entry point that forwards to make_api_request_with_options
    with sensible defaults.

    Args:
        method: API method to call
        description: Description of the operation for progress display
        **kwargs: Keyword arguments including:
            - success_title: Title for success message (default: "Success")
            - error_title: Title for error message (default: "Error")
            - display_data: Whether to display the response data (default: True)
            - output_format: Format for output (default: "json")
            - output_file: Output file path (default: None)
            - Any parameters to pass to the API method

    Returns:
        ApiResponse: API response

    Raises:
        typer.Exit: If the request fails
    """
    # Extract options from kwargs
    success_title = kwargs.pop("success_title", "Success")
    error_title = kwargs.pop("error_title", "Error")
    display_data = kwargs.pop("display_data", True)
    output_format = kwargs.pop("output_format", "json")
    output_file = kwargs.pop("output_file", None)

    # Create configuration
    config = ApiRequestConfig(
        method=method,
        description=description,
        success_title=success_title,
        error_title=error_title,
        display_data=display_data,
        output_format=output_format,
        output_file=output_file,
        kwargs=kwargs,
    )
    return make_api_request_with_config(config)


def extract_common_options() -> dict[str, Any]:
    """
    Extract common options from the current Typer context.

    This is useful for commands that share common options like profile,
    output format, etc.

    Returns:
        dict: Dictionary of common options
    """
    params = get_typer_context_params()

    # Common options used across multiple commands
    return {
        "profile": params.get("profile"),
        "output_format": params.get("output_format", "json"),
        "output_file": params.get("output"),
    }


def extract_entity_options() -> dict[str, Any]:
    """
    Extract entity-related options from the current Typer context.

    Returns:
        dict: Dictionary of entity options
    """
    params = get_typer_context_params()

    # Start with common options
    options = extract_common_options()

    # Add entity-specific options
    options.update(
        {
            "filters": parse_key_value_params(
                params.get("filter_params", []),
                "filter",
            ),
            "sort_by": params.get("sort"),
            "sort_order": params.get("order", "asc"),
            "limit": params.get("limit"),
            "offset": params.get("offset"),
        },
    )

    return options


def log_operation(
    operation: str,
    *,  # Make level parameter keyword-only
    level: str = "info",
    **kwargs: Any,
) -> None:
    """
    Log an operation with Logfire.

    Args:
        operation: Operation name
        level: Log level (info, error, warning, debug)
        **kwargs: Additional log context
    """
    try:
        if level == "info":
            logging.info(operation, **kwargs)
        elif level == "error":
            logging.error(operation, **kwargs)
        elif level == "warning":
            logging.warning(operation, **kwargs)
        elif level == "debug":
            logging.debug(operation, **kwargs)
    except ImportError:
        # Logfire not available, use standard logging
        import logging as std_logging

        logger = std_logging.getLogger("dc_api_x.cli")
        getattr(logger, level)(operation)


class ProgressBar:
    """Helper class for displaying progress bars with Rich."""

    def __init__(self, total: int, description: str):
        """
        Initialize a progress bar.

        Args:
            total: Total number of steps
            description: Description of the operation
        """
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        )
        self.total = total
        self.description = description

    def __enter__(self) -> tuple[Progress, int]:
        """
        Start the progress bar.

        Returns:
            tuple: (Progress object, task ID)
        """
        self.progress.start()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        return self.progress, self.task_id

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        """Stop the progress bar."""
        self.progress.stop()
        return False


# Utility function to validate output format
def validate_output_format(format_str: str) -> OutputFormat:
    """
    Validate the output format string.

    Args:
        format_str: Format string to validate

    Returns:
        OutputFormat: Valid output format

    Raises:
        InvalidOutputFormatError: If the format is not valid
    """
    valid_formats = {"json", "csv", "table", "text"}
    if format_str.lower() not in valid_formats:
        formats_str = ", ".join(valid_formats)
        raise InvalidOutputFormatError(
            f"Invalid output format: {format_str}. Valid formats: {formats_str}",
        )
    return cast(OutputFormat, format_str.lower())
