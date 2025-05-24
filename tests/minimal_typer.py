"""Minimal Typer example script."""

import typer

from tests.constants import (
    DEFAULT_GREETING,
    DEFAULT_NAME_OPTION,
    DEFAULT_NAME_OPTION_SHORT,
    DEFAULT_VERBOSE_OPTION,
    DEFAULT_VERBOSE_OPTION_SHORT,
    TEST_GREETING_FORMAT,
    TEST_VERBOSE_MESSAGE,
)

app = typer.Typer()

# Define option constants
NAME_OPTION = typer.Option(
    DEFAULT_GREETING,
    DEFAULT_NAME_OPTION,
    DEFAULT_NAME_OPTION_SHORT,
    help="Name to greet",
)
VERBOSE_OPTION = typer.Option(
    False,  # noqa: FBT003 - Required by Typer API
    DEFAULT_VERBOSE_OPTION,
    DEFAULT_VERBOSE_OPTION_SHORT,
    help="Enable verbose output",
    is_flag=True,
)


@app.command()
def hello(
    name: str = NAME_OPTION,
    verbose: bool = VERBOSE_OPTION,  # noqa: FBT001
) -> None:
    """Say hello to someone."""
    if verbose:
        typer.echo(TEST_VERBOSE_MESSAGE.format(name))
    typer.echo(TEST_GREETING_FORMAT.format(name))


if __name__ == "__main__":
    app()
