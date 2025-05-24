"""
Simple test script for Typer functionality.

This tests the Typer functionality directly without depending on dc_api_x modules.
"""

import typer
from typer.testing import CliRunner

app = typer.Typer(help="Test CLI.")

# Define options as module-level constants (our fix for B008)
VERBOSE_OPTION = typer.Option(
    False,  # noqa: S101 - First parameter should be the default value
    "--verbose",
    help="Enable verbose output",
    is_flag=True,
)  # noqa: FBT003 - Este é o padrão do Typer, sem alternativa
NAME_OPTION = typer.Option("world", "--name", help="Name to greet")


@app.command()
def hello(
    name: str = NAME_OPTION,
    verbose: bool = VERBOSE_OPTION,  # noqa: FBT001
) -> None:
    """Say hello."""
    if verbose:
        typer.echo(f"Running hello command with name: {name}")
    typer.echo(f"Hello, {name}!")


def test_app() -> None:
    """Test the Typer app."""
    runner = CliRunner()

    # Test the hello command with default parameters
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, world!" in result.stdout

    # Test the hello command with a name parameter
    result = runner.invoke(app, ["hello", "--name", "friend"])
    assert result.exit_code == 0
    assert "Hello, friend!" in result.stdout

    # Test the hello command with verbose flag
    result = runner.invoke(app, ["hello", "--verbose"])
    assert result.exit_code == 0
    assert "Running hello command with name" in result.stdout
    assert "Hello, world!" in result.stdout


if __name__ == "__main__":
    app()
