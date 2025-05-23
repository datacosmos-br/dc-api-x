"""
Logging utilities for the API client.

This module provides functions for setting up and configuring logging for the API client.
"""

import logging
import sys
from pathlib import Path
from typing import Any, TextIO, Union

import structlog
from rich.logging import RichHandler


def setup_logger(  # noqa: PLR0913
    name: str = "dc_api_x",
    level: int | str = logging.INFO,
    format_string: str | None = None,
    log_file: str | Path | None = None,
    *,
    console: bool = True,
    structured: bool = False,
    processors: list[Any] | None = None,
) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        format_string: Format string for log messages (optional)
        log_file: Path to log file (optional)
        console: Whether to log to console (default: True)
        structured: Whether to use structured logging (default: False)
        processors: list of structlog processors (optional)

    Returns:
        logging.Logger: Configured logger
    """
    # Convert level string to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Default format string
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []  # Remove existing handlers

    # Add console handler
    if console:
        if structured:
            # Set up structured logging with console output
            console_handler: Union[logging.StreamHandler[TextIO], RichHandler] = (
                logging.StreamHandler(sys.stdout)
            )
        else:
            # Use rich for prettier console output
            console_handler = RichHandler(rich_tracebacks=True, markup=True)

        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(console_handler)

    # Add file handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    # Configure structlog if requested
    if structured:
        if processors is None:
            processors = [
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ]

        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (optional)

    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = "dc_api_x"
    elif not name.startswith("dc_api_x"):
        name = f"dc_api_x.{name}"

    return logging.getLogger(name)
