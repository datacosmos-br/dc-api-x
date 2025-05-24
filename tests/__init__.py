"""
Test package for dc-api-x.

This package contains tests for the dc-api-x library, organized into
unit tests and integration tests.
"""

import functools
import os
from collections.abc import Callable
from typing import (
    Any,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    overload,
)

# Create a standard logging interface for tests that works with or without Logfire
# This allows tests to always use the same interface regardless of Logfire availability

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class LogEntry(dict[str, Any]):
    """Type for log entries captured during tests."""

    @property
    def message(self) -> str:
        """Get the log message."""
        return str(self.get("message", ""))

    @property
    def level(self) -> str:
        """Get the log level."""
        return str(self.get("level", ""))

    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to dictionary keys."""
        if name in self:
            return self[name]
        msg = f"No such attribute: {name}"
        raise AttributeError(msg)


class CapturedLogsProtocol(Protocol):
    """Protocol for captured logs."""

    @property
    def logs(self) -> list[LogEntry]:
        """Get the captured logs."""
        ...


# Try to import logfire
try:
    import logfire
    from logfire import context, span, testing

    from dc_api_x.utils import logging as dc_logfire

    LOGFIRE_AVAILABLE = True

    # Re-export standard Logfire functions
    debug = logfire.debug
    info = logfire.info
    warning = logfire.warning
    error = logfire.error
    critical = logfire.critical
    exception = logfire.exception

    # Define the captured logs type for type hints
    class CapturedLogs(testing.CapturedLogs):
        """Enhanced captured logs with additional helper methods."""

        @property
        def logs(self) -> list[LogEntry]:
            """Get the captured logs as enhanced LogEntry objects."""
            return [LogEntry(log) for log in super().logs]

        def find_logs(self, **kwargs: Any) -> list[LogEntry]:
            """Find logs matching the given criteria.

            Args:
                **kwargs: Key-value pairs to match in logs

            Returns:
                List of matching log entries
            """
            result = []
            for log in self.logs:
                matches = True
                for key, value in kwargs.items():
                    if key not in log or log[key] != value:
                        matches = False
                        break
                if matches:
                    result.append(log)
            return result

        def find_log(self, **kwargs: Any) -> Optional[LogEntry]:
            """Find first log matching the given criteria.

            Args:
                **kwargs: Key-value pairs to match in logs

            Returns:
                Matching log entry or None if not found
            """
            logs = self.find_logs(**kwargs)
            return logs[0] if logs else None

    # Configure the default test service name
    TEST_SERVICE_NAME = "dc-api-x-tests"

    def setup_test_logging(
        service_name: str = TEST_SERVICE_NAME,
        environment: str = "test",
        level: str = "DEBUG",
    ) -> None:
        """Set up Logfire for testing.

        Args:
            service_name: Name of the service for logs
            environment: Environment name for logs
            level: Logging level (DEBUG, INFO, etc.)
        """
        if not os.environ.get("LOGFIRE_CONFIGURED"):
            dc_logfire.setup_logging(
                service_name=service_name,
                environment=environment,
                level=level,
                local=True,
            )
            os.environ["LOGFIRE_CONFIGURED"] = "1"

except ImportError:
    LOGFIRE_AVAILABLE = False

    # Create dummy/no-op functions to use when Logfire is not available
    class DummyCapturedLogs:
        """Dummy class that mimics CapturedLogs when Logfire is not available."""

        def __init__(self) -> None:
            """Initialize empty logs list."""
            self.logs: list[LogEntry] = []

        def find_logs(self, **kwargs: Any) -> list[LogEntry]:
            """Find logs matching the given criteria (always empty list).

            Args:
                **kwargs: Key-value pairs to match in logs

            Returns:
                Empty list since no logs are captured
            """
            return []

        def find_log(self, **kwargs: Any) -> Optional[LogEntry]:
            """Find first log matching the given criteria (always None).

            Args:
                **kwargs: Key-value pairs to match in logs

            Returns:
                None since no logs are captured
            """
            return None

    # Type definition for dummy captured logs
    CapturedLogs = DummyCapturedLogs

    # Create dummy context manager
    class DummyContextManager:
        """Dummy context manager that mimics logfire.context when Logfire is not available."""

        def __init__(self, **kwargs: Any) -> None:
            """Initialize with context values (ignored)."""

        def __enter__(self) -> "DummyContextManager":
            """Enter context."""
            return self

        def __exit__(self, *args: Any) -> None:
            """Exit context."""

    # Create dummy span
    class DummySpan(DummyContextManager):
        """Dummy span that mimics logfire.span when Logfire is not available."""

    # Create dummy testing context
    class DummyTestingCapture(DummyContextManager):
        """Dummy capture context that mimics logfire.testing.capture when Logfire is not available."""

        def __enter__(self) -> DummyCapturedLogs:
            """Enter context and return dummy captured logs."""
            return DummyCapturedLogs()

    # Create dummy testing module
    class DummyTesting:
        """Dummy testing module that mimics logfire.testing when Logfire is not available."""

        @staticmethod
        def capture() -> DummyTestingCapture:
            """Dummy capture function."""
            return DummyTestingCapture()

    # Create no-op logging functions
    def _noop(*args: Any, **kwargs: Any) -> None:
        """No-op function for when Logfire is not available."""

    # Assign no-op functions to the exported names
    debug = _noop
    info = _noop
    warning = _noop
    error = _noop
    critical = _noop
    exception = _noop

    # Create dummy context functions
    def context(**kwargs: Any) -> DummyContextManager:
        """Dummy context function."""
        return DummyContextManager(**kwargs)

    def span(name: str, **kwargs: Any) -> DummySpan:  # noqa: ARG001
        """Dummy span function."""
        return DummySpan(**kwargs)

    # Create dummy testing module
    testing = DummyTesting()

    # Define dummy setup function
    def setup_test_logging(
        service_name: str = "dc-api-x-tests",
        environment: str = "test",
        level: str = "DEBUG",
    ) -> None:
        """Dummy setup function for when Logfire is not available."""


# Function to check if a test should be skipped due to Logfire unavailability
@overload
def requires_logfire(func: F) -> F: ...


@overload
def requires_logfire(*, strict: bool = True) -> Callable[[F], F]: ...


def requires_logfire(
    func: Optional[F] = None,
    *,
    strict: bool = True,
) -> Union[F, Callable[[F], F]]:
    """Decorator to skip tests that require Logfire if it's not available.

    Args:
        func: Test function to wrap
        strict: If True, skip test when Logfire is not available.
               If False, run test but with mock Logfire

    Returns:
        Wrapped function that skips if Logfire is not available
    """
    import pytest

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not LOGFIRE_AVAILABLE and strict:
                pytest.skip("Logfire not available")
            return f(*args, **kwargs)

        # Add marker for pytest
        wrapper.logfire = True  # type: ignore[attr-defined]

        return cast(F, wrapper)

    if func is None:
        return decorator
    return decorator(func)


# Helper for creating test context
def test_context(**kwargs: Any) -> Any:
    """Create a context for tests with standard test metadata.

    Args:
        **kwargs: Additional context values

    Returns:
        Context manager
    """
    ctx = {"test": True}
    ctx.update(kwargs)
    return context(**ctx)


__all__ = [
    "LOGFIRE_AVAILABLE",
    "CapturedLogs",
    "LogEntry",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "context",
    "span",
    "testing",
    "setup_test_logging",
    "requires_logfire",
    "test_context",
]
