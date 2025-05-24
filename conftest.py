"""
DC-API-X Custom Pytest Conftest.

This conftest.py file sets up global fixtures and configuration for pytest.
It ensures Logfire modules are properly mocked before any tests are run.
"""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pytest_configure(config) -> None:
    """
    Configure pytest before collecting tests.

    This hook runs before any tests are collected, allowing us to mock
    Logfire modules before any imports happen.
    """
    logger.info("Configuring pytest - mocking Logfire modules")

    # Create a mock for the pydantic plugin
    pydantic_plugin_mock = MagicMock()
    # Make the new_schema_validator method return 3 values as expected
    pydantic_plugin_mock.new_schema_validator = MagicMock(
        return_value=(MagicMock(), MagicMock(), MagicMock()),
    )

    # Set environment variables for tests
    os.environ["LOGFIRE_LOCAL"] = "1"
    os.environ["LOGFIRE_SERVICE_NAME"] = "dc-api-x-test"
    os.environ["LOGFIRE_ENVIRONMENT"] = "test"

    # Create logs directory
    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(exist_ok=True)
    os.environ["LOGFIRE_LOG_DIR"] = str(logs_dir)

    # Set log level to DEBUG for tests
    os.environ["LOGFIRE_LOG_LEVEL"] = "DEBUG"

    logger.info("Pytest configuration complete")
