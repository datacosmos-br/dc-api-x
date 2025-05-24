"""Minimal Typer example script."""

import typer

app = typer.Typer()

# Define option constants
NAME_OPTION = typer.Option("World", "--name", "-n", help="Name to greet")
VERBOSE_OPTION = typer.Option(
    False,  # First parameter should be the default value
    "--verbose",
    "-v",
    help="Enable verbose output",
    is_flag=True,  # Specify this is a flag
)  # noqa: FBT003 - Este é o padrão do Typer, sem alternativa


@app.command()
def hello(
    name: str = NAME_OPTION,
    verbose: bool = VERBOSE_OPTION,  # noqa: FBT001
) -> None:
    """Say hello to someone."""
    if verbose:
        typer.echo(f"Running hello with name={name}")
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
