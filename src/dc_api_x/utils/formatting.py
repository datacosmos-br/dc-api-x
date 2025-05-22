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
from pathlib import Path
from typing import Any, TextIO, cast

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
    if isinstance(data, str):
        # If data is already a string, try to parse it first
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return data

    return cast(
        str,
        json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True),
    )


def format_table(
    data: list[dict[str, Any]],
    fields: list[str] | None = None,
    headers: dict[str, str] | None = None,
    title: str | None = None,
    console: Console | None = None,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as a table.

    Args:
        data: Data to format
        fields: Fields to include (optional)
        headers: Field header mapping (optional)
        title: Table title (optional)
        console: Rich console instance (optional)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted table string
    """
    # Create console if not provided
    if console is None:
        console = Console(record=True)

    # Determine fields if not provided
    if fields is None and data:
        fields = list(data[0].keys())

    # Default to empty list if fields is None
    fields = fields or []

    # Create header mapping if not provided
    if headers is None:
        headers = {field: field.replace("_", " ").title() for field in fields}

    # Create table
    table = RichTable(title=title)

    # Add columns
    for field in fields:
        header = headers.get(field, field)
        table.add_column(header)

    # Add rows
    for item in data:
        row = [str(item.get(field, "")) for field in fields]
        table.add_row(*row)

    # Output table
    console.print(table)

    # Get string representation
    table_str = console.export_text()

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with Path(output_file).open("w") as f:
                f.write(table_str)
        else:
            output_file.write(table_str)

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
    writer = csv.writer(output, delimiter=delimiter)

    # Write header row
    header_row = [headers.get(field, field) for field in fields]
    writer.writerow(header_row)

    # Write data rows
    for item in data:
        row = [item.get(field, "") for field in fields]
        writer.writerow(row)

    # Get string representation
    csv_str = output.getvalue()

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with Path(output_file).open("w") as f:
                f.write(csv_str)
        else:
            output_file.write(csv_str)

    return csv_str


def format_text(
    data: list[dict[str, Any]],
    template: str,
    field_func: Callable[[str, Any], Any] | None = None,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data using a text template.

    Args:
        data: Data to format
        template: Format template with field placeholders
        field_func: Function to transform field values (optional)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted text string
    """
    # Default field transformation function
    if field_func is None:

        def field_func(_: str, value: Any) -> Any:
            return value

    # Format each item
    lines = []
    for item in data:
        # Create context with transformed field values
        context = {name: field_func(name, value) for name, value in item.items()}

        # Format template with context
        try:
            line = template.format(**context)
            lines.append(line)
        except KeyError:
            # Skip items that don't have all template fields
            pass

    # Join lines
    text = "\n".join(lines)

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with Path(output_file).open("w") as f:
                f.write(text)
        else:
            output_file.write(text)

    return text


def normalize_key(key: str) -> str:
    """Normalize a key for consistent formatting.

    Args:
        key: The key to normalize

    Returns:
        Normalized key string
    """
    return key.lower().replace(" ", "_").replace("-", "_")


def format_datetime(dt: datetime.datetime) -> str:
    """Format a datetime object to ISO format.

    Args:
        dt: Datetime object to format

    Returns:
        Formatted datetime string
    """
    return dt.isoformat()


def format_value(value: Any) -> str:
    """Format any value as a string.

    Args:
        value: Value to format

    Returns:
        Formatted string representation
    """
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, datetime.datetime):
        return format_datetime(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    # For any other type, ensure we return a string
    return str(value)


def format_response_data(data: dict[str, Any]) -> dict[str, Any]:
    """Format response data for consistent output.

    Args:
        data: Response data to format

    Returns:
        Formatted response data
    """
    result = {}
    for key, value in data.items():
        normalized_key = normalize_key(key)
        if isinstance(value, dict):
            result[normalized_key] = format_response_data(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            result[normalized_key] = [format_response_data(item) for item in value]
        else:
            result[normalized_key] = value
    return result
