"""
Pytest configuration file.

This module contains pytest fixtures and configuration for the dc_api_x test suite.
"""

import json
import logging
import os
import tempfile
import warnings
import xml.etree.ElementTree as ET
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock, patch

import httpx
import jwt
import pytest
import responses
from pydantic import BaseModel

import dc_api_x as apix
from dc_api_x.config import Config
from tests import (
    LOGFIRE_AVAILABLE,
    CapturedLogs,
    info,
    setup_test_logging,
    test_context,
    testing,
)

# -----------------------------------------------------------------------------
# Pytest Configuration
# -----------------------------------------------------------------------------

# Register plugins
pytest_plugins = [
    "pytest_asyncio",
    "pytest_mock",
    "pytest_cov",
    "pytest_html",
]


def pytest_addoption(parser) -> None:
    """Add custom command line options to pytest."""
    parser.addoption(
        "--mock-services",
        action="store_true",
        default=False,
        help="Enable mock services for testing",
    )

    # Add logfire option
    parser.addoption(
        "--logfire",
        action="store_true",
        default=False,
        help="Enable Logfire structured logging during tests",
    )


def pytest_configure(config) -> None:
    """Configure pytest based on command line options."""
    # Register test markers
    markers = [
        "unit: marks tests as unit tests",
        "integration: marks tests requiring external services",
        "functional: marks tests as functional tests",
        "performance: marks tests for performance benchmarking",
        "security: marks tests for security validation",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
        "plugins: tests for plugin system",
        "logfire: marks tests that use or require structured logging with Logfire (run with --logfire flag)",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)

    # Configure Logfire if enabled
    if LOGFIRE_AVAILABLE and config.getoption("--logfire"):
        setup_test_logging(
            service_name="dc-api-x-tests",
            environment="test",
            level="DEBUG",
        )

        # Add test execution context
        info(
            "Starting test execution",
            test_session_id=config.rootdir.basename,
            pytest_version=pytest.__version__,
        )


def pytest_unconfigure(config) -> None:
    """Clean up after test execution."""
    # Log test completion with Logfire
    if LOGFIRE_AVAILABLE and config.getoption("--logfire"):
        info("Test execution completed")


# -----------------------------------------------------------------------------
# Helper Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def mock_services_enabled(request) -> bool:
    """Check if mock services are enabled."""
    return request.config.getoption("--mock-services")


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


# -----------------------------------------------------------------------------
# Logging Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def captured_logs(caplog) -> Any:
    """Capture logs during tests."""
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture
def logfire_testing(
    request,
) -> Generator[Optional[CapturedLogs], None, None]:
    """Setup Logfire structured logging for tests.

    This fixture configures Logfire for testing with proper context
    and enables the capture of logs for assertions. It provides helper
    methods for finding logs based on criteria.

    Example:
        def test_example(logfire_testing):
            info("Test message", value=42)
            log = logfire_testing.find_log(message="Test message")
            assert log.value == 42

    Returns:
        Generator with captured logs for assertions
    """
    if not LOGFIRE_AVAILABLE:
        pytest.skip("Logfire not available, skipping test")
        yield None
        return

    # Configure Logfire for testing if not already configured
    setup_test_logging()

    # Get test metadata
    test_name = request.node.name if hasattr(request, "node") else "unknown-test"
    test_module = (
        request.module.__name__ if hasattr(request, "module") else "unknown-module"
    )
    test_class = request.cls.__name__ if hasattr(request, "cls") and request.cls else ""
    test_file = (
        Path(request.module.__file__).name
        if hasattr(request, "module") and hasattr(request.module, "__file__")
        else "unknown-file"
    )

    # Create test context with all test metadata
    with test_context(
        test_name=test_name,
        test_module=test_module,
        test_class=test_class,
        test_file=test_file,
        pytest_nodeid=request.node.nodeid if hasattr(request, "node") else "",
    ):
        # Log test start
        info(f"Starting test: {test_name}", module=test_module)

        # Use testing capture context manager
        with testing.capture() as captured:
            yield captured

        # Log test completion
        if hasattr(request, "node") and hasattr(request.node, "rep_call"):
            outcome = request.node.rep_call.outcome
            info(
                f"Test completed: {test_name}",
                module=test_module,
                outcome=outcome,
            )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator[None, Any, None]:  # noqa: ARG001
    """Store test result for access in fixtures."""
    outcome = yield
    rep = outcome.get_result()

    # Set report attributes on the node for use in fixtures
    setattr(item, f"rep_{rep.when}", rep)


# -----------------------------------------------------------------------------
# HTTP/API Testing Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_response() -> MagicMock:
    """Create a mock HTTP response for testing."""
    response = MagicMock()
    response.status_code = 200
    response.text = '{"success": true, "data": {"id": 1}}'
    response.json.return_value = {"success": True, "data": {"id": 1}}
    return response


@pytest.fixture
def mock_error_response() -> MagicMock:
    """Create a mock error HTTP response for testing."""
    response = MagicMock()
    response.status_code = 400
    response.text = '{"error": "Bad Request", "code": "ERR_001"}'
    response.json.return_value = {"error": "Bad Request", "code": "ERR_001"}
    response.raise_for_status.side_effect = Exception("HTTP Error")
    return response


@pytest.fixture
def mock_http_service() -> Generator[responses.RequestsMock, None, None]:
    """Create a mock HTTP service for testing."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Setup common endpoints
        rsps.add(
            responses.GET,
            "https://api.example.com/ping",
            json={"status": "ok"},
            status=200,
        )

        # Success responses
        rsps.add(
            responses.GET,
            "https://api.example.com/users",
            json={"data": [{"id": 1, "name": "John"}]},
            status=200,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John"}},
            status=200,
        )
        rsps.add(
            responses.POST,
            "https://api.example.com/users",
            json={"data": {"id": 2, "name": "Jane"}},
            status=201,
        )
        rsps.add(
            responses.PUT,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John Updated"}},
            status=200,
        )
        rsps.add(
            responses.DELETE,
            "https://api.example.com/users/1",
            json={"success": True},
            status=204,
        )
        rsps.add(
            responses.PATCH,
            "https://api.example.com/users/1",
            json={"data": {"id": 1, "name": "John Patched"}},
            status=200,
        )

        # Error responses
        rsps.add(
            responses.GET,
            "https://api.example.com/users/999",
            json={"error": "User not found"},
            status=404,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/server-error",
            json={"error": "Internal Server Error"},
            status=500,
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/unauthorized",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Connection errors
        rsps.add(
            responses.GET,
            "https://api.example.com/error",
            body=apix.ApiConnectionError("Connection refused"),
        )
        rsps.add(
            responses.GET,
            "https://api.example.com/timeout",
            body=apix.ApiTimeoutError("Request timed out"),
        )

        yield rsps


@pytest.fixture
def mock_response_factory() -> Callable[..., httpx.Response]:
    """Create a factory for generating mock responses."""

    def _factory(
        status_code=200,
        json_data=None,
        text=None,
        headers=None,
    ) -> httpx.Response:
        response = httpx.Response(
            status_code=status_code,
            headers=headers or {},
            text=text or "",
        )
        if json_data is not None:
            response._content = json.dumps(json_data).encode()
            response.headers["Content-Type"] = "application/json"
        return response

    return _factory


@pytest.fixture
def mock_api_client() -> Any:
    """Create a mock API client for testing."""
    from tests.factories import create_mock_client_with_responses

    return create_mock_client_with_responses(
        {
            ("GET", "status"): {"status": "ok", "version": "1.0.0"},
        },
    )


# -----------------------------------------------------------------------------
# Authentication Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_auth_provider() -> MagicMock:
    """Create a mock authentication provider for testing."""
    auth_provider = MagicMock(spec=apix.AuthProvider)
    auth_provider.authenticate.return_value = {"token": "mock-token"}
    auth_provider.get_auth_headers.return_value = {"Authorization": "Bearer mock-token"}
    auth_provider.username = "testuser"
    auth_provider.password = "testpass"
    return auth_provider


@pytest.fixture
def jwt_payload() -> dict[str, Any]:
    """Return a sample JWT payload for testing."""
    return {
        "sub": "1234567890",
        "name": "Test User",
        "admin": True,
        "iat": 1516239022,
    }


@pytest.fixture
def jwt_token(jwt_payload: dict[str, Any]) -> str:
    """Return a sample JWT token for testing."""
    secret = os.environ.get("JWT_SECRET_KEY", "test-secret-key")
    algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
    return jwt.encode(jwt_payload, secret, algorithm=algorithm)


# -----------------------------------------------------------------------------
# Database Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def in_memory_db() -> Generator[Any, None, None]:
    """Create an in-memory SQLite database."""
    import sqlite3

    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def db_schema(in_memory_db) -> Generator[Any, None, None]:
    """Create a test schema in the database."""
    cursor = in_memory_db.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    )
    in_memory_db.commit()
    yield in_memory_db

    # Clean up
    cursor.execute("DROP TABLE IF EXISTS users")
    in_memory_db.commit()


# -----------------------------------------------------------------------------
# Model Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_pydantic_model() -> type[BaseModel]:
    """Return a sample Pydantic model for testing."""

    class User(BaseModel):
        id: int
        name: str
        email: str
        is_active: bool = True

    return User


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Provide sample data for tests."""
    return {
        "id": 1,
        "name": "Test Entity",
        "active": True,
        "tags": ["tag1", "tag2"],
        "metadata": {
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        },
    }


# -----------------------------------------------------------------------------
# Miscellaneous Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def xml_document() -> ET.Element:
    """Return a sample XML document for testing."""
    root = ET.Element("root")
    child = ET.SubElement(root, "child")
    child.text = "This is a test"
    return root


@pytest.fixture
def benchmark_data() -> list[dict[str, Any]]:
    """Generate data for benchmarks."""
    return [
        {
            "id": i,
            "name": f"Item {i}",
            "value": i * 10,
            "active": i % 2 == 0,
        }
        for i in range(1000)
    ]


# -----------------------------------------------------------------------------
# Test Data Files
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_xml_file(temp_dir) -> Path:
    """Create a sample XML file for testing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="1">
        <name>Item 1</name>
        <value>100</value>
    </item>
    <item id="2">
        <name>Item 2</name>
        <value>200</value>
    </item>
</root>
"""
    file_path = temp_dir / "sample.xml"
    with Path(file_path).open("w") as f:
        f.write(xml_content)
    return file_path


@pytest.fixture
def sample_json_file(temp_dir) -> Path:
    """Create a sample JSON file for testing."""
    json_content = {
        "items": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
        ],
        "metadata": {
            "count": 2,
            "timestamp": "2023-01-01T00:00:00Z",
        },
    }

    file_path = temp_dir / "sample.json"
    with Path(file_path).open("w") as f:
        json.dump(json_content, f, indent=2)
    return file_path


# -----------------------------------------------------------------------------
# Mock Env File and Secrets
# -----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_env_file(mock_services_enabled) -> Generator[None, None, None]:
    """Mock environment file for testing."""
    if mock_services_enabled:
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "pydantic_settings.sources.providers.secrets.path_type_label",
                return_value="directory",
            ),
            patch("os.path.isdir", return_value=True),
        ):
            yield
    else:
        yield


@pytest.fixture(autouse=True)
def mock_secrets_dir(mock_services_enabled) -> Generator[None, None, None]:
    """Mock secrets directory for testing."""
    if mock_services_enabled:
        with (
            patch(
                "pydantic_settings.sources.providers.secrets.SecretsSettingsSource.__call__",
                return_value={},
            ),
            patch("os.path.isdir", return_value=True),
            patch("os.path.exists", return_value=True),
            patch("pathlib.Path.exists", return_value=True),
        ):
            yield
    else:
        yield


@pytest.fixture(scope="session", autouse=True)
def suppress_pydantic_warnings() -> Generator[None, None, None]:
    """Suppress UserWarning about non-existent secrets directory."""
    # Filter out the specific warning
    warnings.filterwarnings(
        "ignore",
        message="directory .* does not exist",
        module="pydantic_settings.sources",
    )

    # Create a temporary directory for tests
    temp_secrets_dir = tempfile.mkdtemp()

    # Store original configuration
    orig_config = Config.model_config.copy()

    # Update model_config with the temporary directory
    Config.model_config["secrets_dir"] = temp_secrets_dir

    yield

    # Restore original configuration
    Config.model_config = orig_config

    # Clean up the temporary directory
    try:
        import shutil

        shutil.rmtree(temp_secrets_dir, ignore_errors=True)
    except ImportError:
        # Log warning instead of using pass
        import logging

        logging.warning("Failed to clean up temporary secrets directory")


# -----------------------------------------------------------------------------
# CI/Test skipping
# -----------------------------------------------------------------------------


def pytest_runtest_setup(item) -> None:
    """Skip tests that require external services in CI environment."""
    # If running in CI environment and test is marked as requiring external services
    if os.environ.get("CI") == "true" and any(
        mark.name == "integration" for mark in item.iter_markers()
    ):
        requires_external = any(
            mark.name == "integration" for mark in item.iter_markers()
        )
        if requires_external:
            pytest.skip(
                "Skipping test that requires external services in CI environment",
            )
