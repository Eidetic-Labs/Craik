"""Command-line interface for Craik."""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version
from typing import Annotated

import typer

from craik import __version__
from craik.contracts.registry import schema_model, schema_names

PACKAGE_NAME = "craik"

app = typer.Typer(
    add_completion=False,
    help="Durable agent runtime for shared project models and governed multi-agent work.",
    no_args_is_help=True,
)
schema_app = typer.Typer(help="Inspect Craik runtime contract schemas.")
app.add_typer(schema_app, name="schema")


def package_version() -> str:
    """Return the installed package version, with a source-tree fallback."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return __version__


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version_requested: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Print the installed Craik version and exit.",
        ),
    ] = False,
) -> None:
    """Run Craik."""
    if version_requested:
        typer.echo(package_version())
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("version")
def version_command() -> None:
    """Print the installed Craik version."""
    typer.echo(package_version())


@schema_app.command("list")
def schema_list() -> None:
    """List known Craik contract schemas."""
    for name in schema_names():
        typer.echo(name)


@schema_app.command("show")
def schema_show(name: str) -> None:
    """Print a contract JSON Schema by name."""
    try:
        model = schema_model(name)
    except KeyError:
        known = ", ".join(schema_names())
        raise typer.BadParameter(f"unknown schema {name!r}; known schemas: {known}") from None

    typer.echo(json.dumps(model.model_json_schema(), indent=2, sort_keys=True))


def main() -> None:
    """Execute the Craik CLI."""
    app()
