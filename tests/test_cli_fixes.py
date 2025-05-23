"""Tests for CLI fixes."""

from typer.testing import CliRunner

from dc_api_x.cli import app

runner = CliRunner()


def test_app_version():
    """Test the app version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "API X CLI version:" in result.stdout


def test_config_list():
    """Test the config list command."""
    result = runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0
    # Either should show profiles or a message about no profiles
    assert (
        "Available configuration profiles" in result.stdout
        or "No configuration profiles found" in result.stdout
    )


def test_debug_flag():
    """Test the debug flag."""
    # This should work without errors even though nothing actually happens
    result = runner.invoke(app, ["--debug", "config", "list"])
    assert result.exit_code == 0
