"""
Formatting utilities for the API client.

This module provides functions for formatting API response data in various formats,
including JSON, tables, CSV, and text.
"""

import csv
import datetime
import io
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from rich.console import Console
from rich.table import Table as RichTable


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format JSON data with proper indentation.

    Args:
        data: Data to format as JSON
        indent: Number of spaces for indentation

    Returns:
        Formatted JSON string
    """
    # Define error message as constant
    json_serialization_error = "Failed to serialize data to JSON: {}"

    # Handle string input
    if isinstance(data, str):
        try:
            # If parsing succeeds, use the parsed object
            json.dumps(
                json.loads(data),
                indent=indent,
                ensure_ascii=False,
                sort_keys=True,
            )
        except json.JSONDecodeError:
            # If it's not valid JSON, return the string as is
            return data

    # Handle dict, list, or other JSON-serializable types
    try:
        # Format the data as JSON
        return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True)
    except TypeError as err:
        # Raise a helpful error message
        raise TypeError(json_serialization_error.format(err)) from err


@dataclass
class TableFormatConfig:
    """Configuration for table formatting."""

    fields: list[str] | None = None
    headers: dict[str, str] | None = None
    title: str | None = None
    console: Any | None = None
    output_file: str | TextIO | None = None


def format_table(
    data: list[dict[str, Any]],
    *,
    config: TableFormatConfig | None = None,
) -> str:
    """
    Format data as a table.

    Args:
        data: Data to format
        config: Table formatting configuration

    Returns:
        str: Formatted table string
    """
    # Use default config if not provided
    if config is None:
        config = TableFormatConfig()

    # Create console if not provided
    if config.console is None:
        config.console = Console(record=True)

    # Determine fields if not provided
    if config.fields is None and data:
        config.fields = list(data[0].keys())

    # Default to empty list if fields is None
    fields = config.fields or []

    # Create header mapping if not provided
    if config.headers is None:
        config.headers = {field: field.replace("_", " ").title() for field in fields}

    # Create table
    table = RichTable(title=config.title)

    # Add columns
    for field in fields:
        header = config.headers.get(field, field)
        table.add_column(header)

    # Add rows
    for item in data:
        row = [str(item.get(field, "")) for field in fields]
        table.add_row(*row)

    # Output table
    config.console.print(table)

    # Get string representation
    table_str = config.console.export_text()

    # Write to file if requested
    if config.output_file is not None:
        if isinstance(config.output_file, str):
            try:
                with Path(config.output_file).open("w") as f:
                    f.write(table_str)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(
                        f"Failed to write table to file {config.output_file}: {err}",
                    )

                raise _file_write_error(err) from err
        else:
            try:
                config.output_file.write(table_str)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(f"Failed to write table to output file: {err}")

                raise _file_write_error(err) from err

    return table_str


def format_csv(
    data: list[dict[str, Any]],
    fields: list[str] | None = None,
    headers: dict[str, str] | None = None,
    delimiter: str = ",",
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as CSV.

    Args:
        data: Data to format
        fields: Fields to include (optional)
        headers: Field header mapping (optional)
        delimiter: CSV delimiter (default: ",")
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted CSV string
    """
    # Determine fields if not provided
    if fields is None and data:
        fields = list(data[0].keys())

    # Default to empty list if fields is None
    fields = fields or []

    # Create header mapping if not provided
    if headers is None:
        headers = {field: field.replace("_", " ").title() for field in fields}

    # Create CSV
    output = io.StringIO()
    try:
        writer = csv.writer(output, delimiter=delimiter)

        # Write header row
        header_row = [headers.get(field, field) for field in fields]
        writer.writerow(header_row)

        # Write data rows
        for item in data:
            row = [item.get(field, "") for field in fields]
            writer.writerow(row)
    except csv.Error as err:

        def _csv_format_error(err) -> None:
            return ValueError(f"Failed to format data as CSV: {err}")

        raise _csv_format_error(err) from err

    # Get string representation
    csv_str = output.getvalue()

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            try:
                with Path(output_file).open("w") as f:
                    f.write(csv_str)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(f"Failed to write CSV to file {output_file}: {err}")

                raise _file_write_error(err) from err
        else:
            try:
                output_file.write(csv_str)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(f"Failed to write CSV to output file: {err}")

                raise _file_write_error(err) from err

    return csv_str


def format_text(
    data: list[dict[str, Any]],
    template: str,
    field_func: Callable[[str, Any], Any] | None = None,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as text using a template.

    Args:
        data: Data to format
        template: Template string with {field} placeholders
        field_func: Function to process field values (optional)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted text string
    """
    # Use identity function if field_func not provided
    if field_func is None:

        def field_func(_: str, value: Any) -> Any:
            return value

    # Apply template to each item
    result = []
    for item in data:
        try:
            # Process fields with field_func
            processed_item = {
                k: field_func(k, v) for k, v in item.items() if k in template
            }
            # Format item with template
            result.append(template.format(**processed_item))
        except KeyError as err:

            def _template_format_error(err) -> None:
                return KeyError(f"Missing field in template: {err}")

            raise _template_format_error(err) from err
        except ValueError as err:

            def _template_format_error(err) -> None:
                return ValueError(f"Failed to format template: {err}")

            raise _template_format_error(err) from err

    # Join results
    text = "\n".join(result)

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            try:
                with Path(output_file).open("w") as f:
                    f.write(text)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(f"Failed to write text to file {output_file}: {err}")

                raise _file_write_error(err) from err
        else:
            try:
                output_file.write(text)
            except OSError as err:

                def _file_write_error(err) -> None:
                    return OSError(f"Failed to write text to output file: {err}")

                raise _file_write_error(err) from err

    return text


def normalize_key(key: str) -> str:
    """
    Normalize a key for consistent formatting.

    Args:
        key: Key to normalize

    Returns:
        Normalized key
    """
    # Convert to lowercase
    key = key.lower()
    # Replace spaces and underscores with hyphens
    return key.replace(" ", "-").replace("_", "-")


def format_datetime(dt: datetime.datetime) -> str:
    """
    Format a datetime object as an ISO 8601 string.

    Args:
        dt: Datetime object

    Returns:
        Formatted datetime string
    """
    # Format as ISO 8601
    return dt.isoformat()


def format_value(value: Any) -> str:
    """
    Format a value for display.

    Args:
        value: Value to format

    Returns:
        Formatted value string
    """
    if value is None:
        return ""
    if isinstance(value, datetime.datetime):
        return format_datetime(value)
    if isinstance(value, dict | list):
        return format_json(value)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int | float):
        return str(value)
    return str(value)


def format_response_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Format response data for display.

    This function walks through a dictionary and formats all values
    using format_value().

    Args:
        data: Response data

    Returns:
        Formatted response data
    """

    def format_nested(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: format_nested(v) for k, v in value.items()}
        if isinstance(value, list):
            return [format_nested(v) for v in value]
        return format_value(value)

    return format_nested(data)
