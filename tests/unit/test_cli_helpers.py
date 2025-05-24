"""
Tests for cli_helpers module.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from dc_api_x import (
    ApiConnectionError,
    BaseAPIError,
    CLIError,
    ConfigurationError,
    NotFoundError,
    ValidationError,
)
from dc_api_x.utils.cli_helpers import (
    create_api_client,
    format_output_data,
    handle_common_errors,
    output_result,
    parse_key_value_params,
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestHandleCommonErrors:
    """Test suite for the handle_common_errors decorator."""

    def test_no_error(self) -> None:
        """Test function with no error."""

        @handle_common_errors
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_configuration_error(self) -> None:
        """Test function with ConfigurationError."""

        @handle_common_errors
        def test_func() -> None:
            raise ConfigurationError("Invalid configuration")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "Configuration error" in mock_print.call_args[0][0]

    def test_api_connection_error(self) -> None:
        """Test function with ApiConnectionError."""

        @handle_common_errors
        def test_func() -> None:
            raise ApiConnectionError("Connection failed")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "Connection error" in mock_print.call_args[0][0]

    def test_validation_error(self) -> None:
        """Test function with ValidationError."""

        @handle_common_errors
        def test_func() -> None:
            raise ValidationError("Invalid data")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "Validation error" in mock_print.call_args[0][0]

    def test_not_found_error(self) -> None:
        """Test function with NotFoundError."""

        @handle_common_errors
        def test_func() -> None:
            raise NotFoundError("Resource not found")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "Not found" in mock_print.call_args[0][0]

    def test_os_error(self) -> None:
        """Test function with OSError."""

        @handle_common_errors
        def test_func() -> None:
            raise OSError("File not found")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "File error" in mock_print.call_args[0][0]

    def test_json_decode_error(self) -> None:
        """Test function with JSONDecodeError."""

        @handle_common_errors
        def test_func() -> None:
            raise json.JSONDecodeError("Invalid JSON", "", 0)

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "JSON error" in mock_print.call_args[0][0]

    def test_base_api_error(self) -> None:
        """Test function with BaseAPIError."""

        @handle_common_errors
        def test_func() -> None:
            raise BaseAPIError("API error")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "API error" in mock_print.call_args[0][0]

    def test_cli_error(self) -> None:
        """Test function with CLIError."""

        @handle_common_errors
        def test_func() -> None:
            raise CLIError("CLI error")

        with (
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
            pytest.raises(typer.Exit),
        ):
            test_func()
            mock_print.assert_called_once()
            assert "CLI error" in mock_print.call_args[0][0]


class TestCreateApiClient:
    """Test suite for the create_api_client function."""

    def test_default_client(self) -> None:
        """Test creating default client."""
        with patch("dc_api_x.utils.cli_helpers.ApiClient") as mock_api_client:
            create_api_client()
            mock_api_client.assert_called_once()

    def test_client_with_profile(self) -> None:
        """Test creating client with profile."""
        with patch(
            "dc_api_x.utils.cli_helpers.ApiClient.from_profile",
        ) as mock_from_profile:
            create_api_client("test")
            mock_from_profile.assert_called_once_with("test")


class TestFormatOutputData:
    """Test suite for the format_output_data function."""

    def test_json_format(self) -> None:
        """Test formatting as JSON."""
        data = {"name": "test", "value": 123}
        with patch("dc_api_x.utils.cli_helpers.format_json") as mock_format_json:
            mock_format_json.return_value = '{"name": "test", "value": 123}'
            result = format_output_data(data, "json")
            mock_format_json.assert_called_once_with(data, indent=2)
            assert result == '{"name": "test", "value": 123}'

    def test_table_format_list(self) -> None:
        """Test formatting list as table."""
        data = [{"name": "test1"}, {"name": "test2"}]
        with patch("dc_api_x.utils.cli_helpers.format_table") as mock_format_table:
            mock_format_table.return_value = "Table output"
            result = format_output_data(data, "table")
            mock_format_table.assert_called_once_with(data)
            assert result == "Table output"

    def test_table_format_dict_with_data(self) -> None:
        """Test formatting dict with data field as table."""
        data = {"data": [{"name": "test1"}, {"name": "test2"}], "count": 2}
        with patch("dc_api_x.utils.cli_helpers.format_table") as mock_format_table:
            mock_format_table.return_value = "Table output"
            result = format_output_data(data, "table")
            mock_format_table.assert_called_once_with(data["data"])
            assert result == "Table output"

    def test_fallback_to_json(self) -> None:
        """Test fallback to JSON for non-list data."""
        data = {"name": "test", "value": 123}
        with (
            patch("dc_api_x.utils.cli_helpers.format_json") as mock_format_json,
            patch("dc_api_x.utils.cli_helpers.console.print") as mock_print,
        ):
            mock_format_json.return_value = '{"name": "test", "value": 123}'
            result = format_output_data(data, "table")
            mock_format_json.assert_called_once_with(data, indent=2)
            assert result == '{"name": "test", "value": 123}'
            mock_print.assert_called_once()
            assert "Warning" in mock_print.call_args[0][0]


class TestOutputResult:
    """Test suite for the output_result function."""

    def test_output_to_console(self) -> None:
        """Test output to console."""
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            output_result("Test output")
            mock_print.assert_called_once_with("Test output")

    def test_output_to_file(self) -> None:
        """Test output to file."""
        mock_file = MagicMock(spec=Path)
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            output_result("Test output", mock_file)
            mock_file.write_text.assert_called_once_with("Test output")
            mock_print.assert_called_once()
            assert "Output written to" in mock_print.call_args[0][0]


class TestParseKeyValueParams:
    """Test suite for the parse_key_value_params function."""

    def test_valid_params(self) -> None:
        """Test parsing valid parameters."""
        params = ["name=test", "value=123"]
        result = parse_key_value_params(params)
        assert result == {"name": "test", "value": "123"}

    def test_empty_params(self) -> None:
        """Test parsing empty parameters."""
        result = parse_key_value_params([])
        assert result == {}

    def test_invalid_format(self) -> None:
        """Test handling invalid parameter format."""
        params = ["name=test", "invalid_param"]
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            result = parse_key_value_params(params)
            assert result == {"name": "test"}
            mock_print.assert_called_once()
            assert "Warning" in mock_print.call_args[0][0]
            assert "invalid_param" in mock_print.call_args[0][0]

    def test_custom_param_name(self) -> None:
        """Test using custom parameter name in warnings."""
        params = ["invalid_filter"]
        with patch("dc_api_x.utils.cli_helpers.console.print") as mock_print:
            result = parse_key_value_params(params, param_name="filter")
            assert result == {}
            mock_print.assert_called_once()
            assert "filter" in mock_print.call_args[0][0]
