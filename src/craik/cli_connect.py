"""Connection detection CLI commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from craik.cli import connect_app
from craik.runtime.memory.memory import StigmemClient, StigmemConfig, StigmemMemoryStore


@connect_app.command("stigmem")
def connect_stigmem(
    url: Annotated[
        str,
        typer.Option(
            "--url",
            envvar="CRAIK_STIGMEM_URL",
            help="Stigmem node URL.",
        ),
    ],
    api_key: Annotated[
        str | None,
        typer.Option(
            "--api-key",
            envvar="CRAIK_STIGMEM_API_KEY",
            help="Bearer API key. Prefer CRAIK_STIGMEM_API_KEY.",
        ),
    ] = None,
    timeout: Annotated[
        float,
        typer.Option(
            "--timeout",
            envvar="CRAIK_STIGMEM_TIMEOUT",
            help="Request timeout in seconds.",
        ),
    ] = 5.0,
) -> None:
    """Detect Stigmem backend compatibility."""
    config = StigmemConfig(node_url=url, api_key=api_key, timeout_seconds=timeout)
    capabilities = StigmemMemoryStore(StigmemClient(config)).discover()
    typer.echo(
        json.dumps(capabilities.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )
