"""
Tests for CLI helper utilities.
"""

import json
from unittest.mock import patch

import pytest
import typer

from dc_api_x.utils.cli import (
    create_api_client,
    format_output_data,
    handle_common_errors,
    output_result,
    parse_key_value_params,
)
from dc_api_x.utils.exceptions import (
    ApiConnectionError,
    BaseAPIError,
    CLIError,
    ConfigurationError,
    NotFoundError,
    ValidationError,
)
from tests.constants import (
    API_ERROR_MESSAGE,
    CLI_ERROR_MESSAGE,
    CONNECTION_FAILED_ERROR,
    FILE_NOT_FOUND_ERROR,
    INVALID_CONFIG_ERROR,
    INVALID_DATA_ERROR,
    INVALID_JSON_ERROR,
    RESOURCE_NOT_FOUND_ERROR,
)


class TestCLIHelpers:
    """Tests for CLI helper utilities."""

    def test_parse_key_value_params(self) -> None:
        """Test parsing key-value parameters."""
        params = ["name=John", "age=30", "active=true"]
        result = parse_key_value_params(params)
        assert result == {"name": "John", "age": "30", "active": "true"}

    def test_format_output_data_json(self) -> None:
        """Test formatting output data as JSON."""
        data = {"name": "John", "age": 30}
        result = format_output_data(data, "json")
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_configuration_error(self) -> None:
        """Test function with ConfigurationError."""

        @handle_common_errors
        def test_func() -> None:
            raise ConfigurationError(INVALID_CONFIG_ERROR)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "Configuration error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_api_connection_error(self) -> None:
        """Test function with ApiConnectionError."""

        @handle_common_errors
        def test_func() -> None:
            raise ApiConnectionError(CONNECTION_FAILED_ERROR)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "Connection error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_validation_error(self) -> None:
        """Test function with ValidationError."""

        @handle_common_errors
        def test_func() -> None:
            raise ValidationError(INVALID_DATA_ERROR)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "Validation error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_not_found_error(self) -> None:
        """Test function with NotFoundError."""

        @handle_common_errors
        def test_func() -> None:
            raise NotFoundError(RESOURCE_NOT_FOUND_ERROR)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "Not found" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_os_error(self) -> None:
        """Test function with OSError."""

        @handle_common_errors
        def test_func() -> None:
            raise OSError(FILE_NOT_FOUND_ERROR)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "File error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_json_decode_error(self) -> None:
        """Test function with JSONDecodeError."""

        @handle_common_errors
        def test_func() -> None:
            raise json.JSONDecodeError(INVALID_JSON_ERROR, "", 0)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "JSON error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_base_api_error(self) -> None:
        """Test function with BaseAPIError."""

        @handle_common_errors
        def test_func() -> None:
            raise BaseAPIError(API_ERROR_MESSAGE)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "API error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_cli_error(self) -> None:
        """Test function with CLIError."""

        @handle_common_errors
        def test_func() -> None:
            raise CLIError(CLI_ERROR_MESSAGE)

        # Create a function for the pytest.raises block
        def execute_test_func():
            test_func()

        # Test separately the assertion of mocks
        def verify_mock_calls():
            mock_print.assert_called_once()
            assert "Command error" in mock_print.call_args[0][0]

        # Use pytest.raises with a single statement
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            with pytest.raises(typer.Exit):
                execute_test_func()
            verify_mock_calls()

    def test_create_api_client(self) -> None:
        """Test create_api_client function."""
        # Just make sure it doesn't raise an error (actual integration tested elsewhere)
        with patch("dc_api_x.utils.cli_helpers.ApiClient") as mock_api_client:
            client = create_api_client(profile="example_profile")
            assert client is mock_api_client.return_value

    def test_output_result_json(self) -> None:
        """Test output_result with JSON format."""
        data = {"name": "John", "age": 30}
        with patch("dc_api_x.utils.cli_helpers.typer.echo") as mock_echo:
            output_result(data, "json")
            mock_echo.assert_called_once()
            # Check json output was passed to echo
            assert isinstance(mock_echo.call_args[0][0], str)

    def test_output_result_table(self) -> None:
        """Test output_result with table format."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            output_result(data, "table")
            mock_print.assert_called_once()
            # Check table was created
            assert "Table" in str(mock_print.call_args[0][0])

    def test_output_result_yaml(self) -> None:
        """Test output_result with YAML format."""
        data = {"name": "John", "age": 30, "address": {"city": "New York"}}
        with patch("dc_api_x.utils.cli_helpers.typer.echo") as mock_echo:
            output_result(data, "yaml")
            mock_echo.assert_called_once()
            # Check yaml output was passed to echo
            assert isinstance(mock_echo.call_args[0][0], str)
            assert "name: John" in mock_echo.call_args[0][0]
