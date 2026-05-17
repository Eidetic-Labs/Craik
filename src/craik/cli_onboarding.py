"""Project onboarding CLI commands."""

from __future__ import annotations

import json
from typing import Annotated, cast

import typer

from craik.cli import app
from craik.contracts.models import PolicyProfile
from craik.runtime.policy.policy import FailOpenNotAllowedError
from craik.runtime.projects.onboarding import AgentOnboardingBuilder, OnboardingProjectNotFoundError
from craik.runtime.store import LocalStore


@app.command("onboard")
def onboard(
    project: Annotated[
        str,
        typer.Option("--project", help="Registered project id or name to onboard."),
    ],
    policy_profile: Annotated[
        str,
        typer.Option(
            "--policy-profile",
            help="Policy profile: strict, trusted-local, or automation.",
        ),
    ] = "strict",
    trusted_local_fail_open: Annotated[
        bool,
        typer.Option(
            "--trusted-local-fail-open",
            help="Explicitly opt in to trusted-local fail-open semantics.",
        ),
    ] = False,
    max_recent_handoffs: Annotated[
        int,
        typer.Option("--max-recent-handoffs", min=0, help="Recent handoffs to include."),
    ] = 5,
) -> None:
    """Print runner-readable onboarding context for a project."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        report = AgentOnboardingBuilder(store).build(
            project,
            policy_profile=_policy_profile(policy_profile),
            trusted_local_fail_open=trusted_local_fail_open,
            max_recent_handoffs=max_recent_handoffs,
        )
    except (OnboardingProjectNotFoundError, FailOpenNotAllowedError) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(json.dumps(report.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


def _policy_profile(value: str) -> PolicyProfile:
    if value not in {"strict", "trusted-local", "automation", "custom"}:
        raise typer.BadParameter(f"unsupported policy profile: {value}")
    return cast(PolicyProfile, value)
