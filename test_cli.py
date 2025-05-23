#!/usr/bin/env python3

import typer

app = typer.Typer()


@app.command()
def hello(name: str = typer.Argument("World")) -> None:
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
