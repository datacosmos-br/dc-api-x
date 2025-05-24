"""
Logging utilities for DCApiX.

This module provides functions for setting up and configuring logging for DCApiX,
with integration for both standard Python logging and structured Logfire logging.
"""

import logging
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

import structlog
from pydantic import BaseModel
from rich.logging import RichHandler

# Define standard logger for fallback
standard_logger = logging.getLogger("dc_api_x")
if not standard_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    standard_logger.addHandler(handler)
    standard_logger.setLevel(logging.INFO)

# Constants for configuration
DEFAULT_SCRUB_FIELDS = [
    "password",
    "api_key",
    "token",
    "secret",
    "credential",
    "auth",
    "authorization",
    "credit_card",
    "cvv",
]
DEFAULT_LOG_LEVEL = "INFO"


# Create a simple context manager for with_tags
class ContextManager:
    def __enter__(self) -> "ContextManager":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


# Define default implementations that will be used if logfire is not available
def debug(msg: str, **kwargs: Any) -> None:
    """Log debug message using standard logging."""
    standard_logger.debug(msg)


def info(msg: str, **kwargs: Any) -> None:
    """Log info message using standard logging."""
    standard_logger.info(msg)


def warning(msg: str, **kwargs: Any) -> None:
    """Log warning message using standard logging."""
    standard_logger.warning(msg)


def error(msg: str, **kwargs: Any) -> None:
    """Log error message using standard logging."""
    standard_logger.error(msg)


def critical(msg: str, **kwargs: Any) -> None:
    """Log critical message using standard logging."""
    standard_logger.critical(msg)


def exception(msg: str, **kwargs: Any) -> None:
    """Log exception message using standard logging."""
    standard_logger.exception(msg)


def with_tags(**kwargs: Any) -> ContextManager:
    """Context manager for adding tags to logs."""
    return ContextManager()


# Export the functions and classes
__all__ = [
    # Functions
    "setup_logger",
    "get_logger",
    "create_cli_logger",
    "setup_logging",
    "log_model",
    # Classes
    "LogfireConfig",
    "RequestTimer",
    # Direct logging functions
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "with_tags",
]


@dataclass
class LogfireConfig:
    """Configuration for Logfire setup."""

    service_name: str = "dc-api-x"
    service_version: str | None = None
    environment: str | None = None
    level: str | None = None
    scrub_fields: list[str] = field(default_factory=list)
    log_dir: str | None = None
    log_request_headers: bool = False
    log_request_body: bool = False
    log_response_headers: bool = False
    local: bool | None = None

    @classmethod
    def from_env(cls) -> "LogfireConfig":
        """Create configuration from environment variables."""
        return cls(
            service_name=os.environ.get("LOGFIRE_SERVICE_NAME", "dc-api-x"),
            environment=os.environ.get("LOGFIRE_ENVIRONMENT", "dev"),
            level=os.environ.get("LOGFIRE_LOG_LEVEL", DEFAULT_LOG_LEVEL),
            log_dir=os.environ.get("LOGFIRE_LOG_DIR"),
            local=os.environ.get("LOGFIRE_LOCAL", "0") == "1",
        )


def setup_logging(
    config: LogfireConfig | None = None,
    *,
    service_name: str | None = None,
    level: str | None = None,
    local: bool | None = None,
) -> None:
    """
    Initialize Logfire with DCApiX configuration.

    Args:
        config: Configuration object for detailed setup.
            Use this parameter for complete control over configuration.
        service_name: Name of the service for logging (overrides config)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (overrides config)
        local: Whether to log to local files only (overrides config)
    """
    # Start with config from environment or defaults
    cfg = config or LogfireConfig.from_env()

    # Override with explicitly provided parameters
    if service_name is not None:
        cfg.service_name = service_name
    if level is not None:
        cfg.level = level
    if local is not None:
        cfg.local = local

    # Ensure we have a valid service name
    if not cfg.service_name:
        cfg.service_name = "dc-api-x"

    # Combine default scrub fields with any provided
    all_scrub_fields = DEFAULT_SCRUB_FIELDS.copy()
    if cfg.scrub_fields:
        all_scrub_fields.extend(cfg.scrub_fields)

    # Try to import real logfire if available
    try:
        import logfire

        # Check if it's really available by accessing key functions
        if hasattr(logfire, "debug") and hasattr(logfire, "info"):
            # Configure Logfire
            logfire.configure(
                service_name=cfg.service_name,
                service_version=cfg.service_version,
                environment=cfg.environment,
                level=cfg.level,
                scrub_fields=all_scrub_fields,
                log_request_headers=cfg.log_request_headers,
                log_request_body=cfg.log_request_body,
                log_response_headers=cfg.log_response_headers,
                local=cfg.local,
            )

            # Set log directory if provided
            if cfg.log_dir:
                os.environ["LOGFIRE_LOG_DIR"] = cfg.log_dir

            # Add integrations automatically
            logfire.integrations.auto_install()

            # Override the default functions with logfire implementations
            # These need to be global so they're visible to other modules
            global debug, info, warning, error, critical, exception, with_tags
            debug = logfire.debug
            info = logfire.info
            warning = logfire.warning
            error = logfire.error
            critical = logfire.critical
            exception = logfire.exception

            def with_tags_impl(**kwargs: Any) -> Any:
                """Context manager for adding tags to logs."""
                if hasattr(logfire, "with_tags"):
                    return logfire.with_tags(**kwargs)
                return ContextManager()

            with_tags = with_tags_impl

            # Log successful initialization using logfire
            info(
                "Logfire initialized",
                service_name=cfg.service_name,
                environment=cfg.environment,
                level=cfg.level,
                local=cfg.local,
            )

            # Store the fact that logfire is configured
            os.environ["LOGFIRE_CONFIGURED"] = "1"
            return

    except ImportError:
        pass  # Continue with standard logging

    # If we got here, logfire is not available or failed to initialize
    # Configure standard logging as fallback
    log_level = getattr(logging, cfg.level or DEFAULT_LOG_LEVEL, logging.INFO)
    standard_logger.setLevel(log_level)

    # Log initialization using standard logger
    standard_logger.info(
        f"Standard logging initialized (logfire not available): {cfg.service_name}",
    )


class RequestTimer:
    """Context manager for timing requests with Logfire integration."""

    def __init__(self, method: str, url: str) -> None:
        """
        Initialize the request timer.

        Args:
            method: HTTP method
            url: Request URL
        """
        self.method = method
        self.url = url
        self.start_time = 0.0
        self.span_name = f"{method} request"

    def __enter__(self) -> "RequestTimer":
        """Enter the context manager and start the timer."""
        self.start_time = time.time()
        # Call debug directly - it will use either standard logger or logfire
        debug(f"Starting {self.method} request", method=self.method, url=self.url)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and log the result."""
        duration_ms = (time.time() - self.start_time) * 1000

        # Log completion or error using the correct function
        if exc_type is None:
            debug(
                f"Completed {self.method} request",
                method=self.method,
                url=self.url,
                duration_ms=duration_ms,
            )
        else:
            error(
                f"Error in {self.method} request",
                method=self.method,
                url=self.url,
                duration_ms=duration_ms,
                error=str(exc_val),
                error_type=exc_type.__name__ if exc_type else None,
            )


def log_model(level: str, message: str, model: BaseModel, **kwargs: Any) -> None:
    """
    Log a Pydantic model with the specified log level.

    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        model: Pydantic model to log
        **kwargs: Additional context fields
    """
    # Get the log function based on level
    log_func: Callable[..., None]
    if level.lower() == "debug":
        log_func = debug
    elif level.lower() == "info":
        log_func = info
    elif level.lower() == "warning":
        log_func = warning
    elif level.lower() == "error":
        log_func = error
    elif level.lower() == "critical":
        log_func = critical
    elif level.lower() == "exception":
        log_func = exception
    else:
        log_func = info  # Default to info

    # Convert model to dict for structured logging
    model_dict = model.model_dump() if hasattr(model, "model_dump") else model.dict()
    model_name = model.__class__.__name__

    # Log with model data
    # The log function will either use logfire or standard logging
    log_func(message, **{model_name.lower(): model_dict}, **kwargs)


def setup_logger(  # noqa: PLR0913
    name: str = "dc_api_x",
    level: int | str = logging.INFO,
    format_string: str | None = None,
    log_file: str | Path | None = None,
    *,
    console: bool = True,
    structured: bool = False,
    processors: list[Any] | None = None,
    use_logfire: bool | None = None,
    config: dict[str, Any] | None = None,
) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        format_string: Format string for log messages (optional)
        log_file: Path to log file (optional)
        console: Whether to log to console (default: True)
        structured: Whether to use structured logging with structlog (default: False)
        processors: List of structlog processors (optional)
        use_logfire: Whether to use Logfire for structured logging (default: auto-detect)
        config: Additional configuration for Logfire

    Returns:
        logging.Logger: Configured logger
    """
    # Auto-detect Logfire if not specified
    if use_logfire is None:
        use_logfire = os.environ.get("LOGFIRE_SERVICE_NAME") is not None

    # If Logfire is enabled and available, use it for structured logging
    if use_logfire and os.environ.get("LOGFIRE_CONFIGURED"):
        # Return a standard logger that will be captured by Logfire
        logger = logging.getLogger(name)

        # Make sure the level is set
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(level)

        return logger

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
            console_handler: logging.StreamHandler[TextIO] | RichHandler = (
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
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    # Configure structlog if requested and not using Logfire
    if structured and not use_logfire:
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


def get_logger(name: str | None = None, **kwargs: Any) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (optional)
        **kwargs: Additional configuration for setup_logger

    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = "dc_api_x"
    elif not name.startswith("dc_api_x"):
        name = f"dc_api_x.{name}"

    # Check if Logfire should be used
    use_logfire = kwargs.pop("use_logfire", None)

    # Check if config exists
    config = kwargs.pop("config", None)

    return setup_logger(name, use_logfire=use_logfire, config=config, **kwargs)


def create_cli_logger(
    name: str = "dc_api_x",
    level: int | str = logging.INFO,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """
    Create a logger suitable for CLI applications.

    This is a convenience wrapper around setup_logger that uses RichHandler
    by default for enhanced CLI output formatting.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)

    Returns:
        logging.Logger: Configured logger
    """
    # Check if logfire is configured via environment variables
    use_logfire = os.environ.get("LOGFIRE_CONFIGURED") == "1"

    # Setup the logger with the appropriate configuration
    return setup_logger(
        name,
        level,
        log_file=log_file,
        console=True,
        structured=False,
        use_logfire=use_logfire,
    )


# Initialize on import if environment is configured
if os.environ.get("LOGFIRE_SERVICE_NAME") and os.environ.get("LOGFIRE_CONFIGURED"):
    setup_logging()
