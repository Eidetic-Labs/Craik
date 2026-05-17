"""Run command group for the Craik CLI."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from craik.contracts.models import CapabilityGrant, CapabilityTarget, TaskRun
from craik.runtime.case_files import ProjectNotFoundError, TaskNotFoundError
from craik.runtime.model_providers import ModelProviderNotFoundError
from craik.runtime.provider_runner import ProviderBackedRunExecutor, ProviderBackedRunResult
from craik.runtime.store import LocalStore

run_app = typer.Typer(help="Execute, inspect, and recover single-agent task runs.")


@run_app.command("execute")
def run_execute(
    task_id: Annotated[str, typer.Argument(help="Task id to execute.")],
    provider_id: Annotated[
        str,
        typer.Option(
            "--provider-id",
            help="Configured provider runner id. Use provider list to inspect options.",
        ),
    ] = "provider_openai",
    allow_fixture_action: Annotated[
        bool,
        typer.Option(
            "--allow-fixture-action/--no-allow-fixture-action",
            help=(
                "Grant the deterministic fixture shell action required by the MVP loop. "
                "This records a governed receipt; it does not execute arbitrary shell."
            ),
        ),
    ] = True,
    max_iterations: Annotated[
        int,
        typer.Option("--max-iterations", help="Maximum single-agent loop iterations."),
    ] = 5,
) -> None:
    """Execute a deterministic provider-backed MVP runner path for a task."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        grants = [_fixture_shell_grant(task_id)] if allow_fixture_action else []
        result = ProviderBackedRunExecutor(store).execute(
            task_id=task_id,
            provider_id=provider_id,
            grants=grants,
            max_iterations=max_iterations,
        )
        payload = _provider_run_payload(result)
    except (
        ModelProviderNotFoundError,
        ProjectNotFoundError,
        TaskNotFoundError,
        ValueError,
    ) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@run_app.command("list")
def run_list(
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Only include runs for this task id."),
    ] = None,
) -> None:
    """List persisted task runs."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        runs = store.list_task_runs()
    finally:
        store.close()
    if task_id is not None:
        runs = [run for run in runs if run.task_id == task_id]
    payload = [run.model_dump(mode="json", by_alias=True) for run in runs]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@run_app.command("inspect")
def run_inspect(
    run_id_or_task_id: str,
    include_outputs: Annotated[
        bool,
        typer.Option(
            "--include-outputs/--no-include-outputs",
            help="Include full captured output payloads.",
        ),
    ] = False,
) -> None:
    """Inspect one persisted task run and linked local state."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        run = _find_run(store, run_id_or_task_id)
        if run is None:
            raise typer.BadParameter(f"unknown run or task: {run_id_or_task_id}")
        payload = _run_inspection_payload(store, run, include_outputs=include_outputs)
    finally:
        store.close()
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@run_app.command("recover")
def run_recover(
    run_id_or_task_id: str,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print recovery plan without writing new state."),
    ] = False,
    reason: Annotated[
        str | None,
        typer.Option("--reason", help="Reason for recovery."),
    ] = None,
) -> None:
    """Print a deterministic recovery plan for an interrupted run."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        run = _find_run(store, run_id_or_task_id)
        if run is None:
            raise typer.BadParameter(f"unknown run or task: {run_id_or_task_id}")
        if run.status != "interrupted":
            typer.echo(
                f"run {run.id} is {run.status}; only interrupted runs can be recovered",
                err=True,
            )
            raise typer.Exit(1)
        payload = _run_recovery_payload(store, run, dry_run=dry_run, reason=reason)
    finally:
        store.close()
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def _fixture_shell_grant(task_id: str) -> CapabilityGrant:
    return CapabilityGrant(
        id=f"grant_{task_id.removeprefix('task_')}_fixture_shell",
        task_id=task_id,
        capability="shell.execute",
        target=CapabilityTarget(paths=["fixture-action"]),
        operations=["execute"],
        reason="Allow the deterministic MVP fixture action.",
        approved_by="user:local-operator",
    )


def _provider_run_payload(result: ProviderBackedRunResult) -> dict[str, Any]:
    provider_results = [
        provider_result.model_dump(mode="json", by_alias=True)
        for provider_result in result.provider_results
    ]
    receipt_ids = sorted(
        {
            receipt_id
            for output in (result.loop.output_captures if result.loop else [])
            for receipt_id in output.output.receipt_ids
        }
        | set(result.run.receipt_ids)
    )
    return {
        "schema": "craik.provider_backed_run_execution",
        "version": "0.1.0",
        "status": result.run.status,
        "run": result.run.model_dump(mode="json", by_alias=True),
        "handoff": result.handoff.model_dump(mode="json", by_alias=True),
        "compiled_prompt": result.compiled_prompt.model_dump(mode="json", by_alias=True),
        "provider_results": provider_results,
        "provider_ids": sorted(
            {provider_result["provider_id"] for provider_result in provider_results}
        ),
        "provider_families": sorted(
            {provider_result["provider_family"] for provider_result in provider_results}
        ),
        "receipt_ids": receipt_ids,
        "interrupted_error": result.interrupted_error,
        "next_commands": [
            f"craik run inspect {result.run.id} --include-outputs",
            f"craik handoff show {result.handoff.id}",
            f"craik receipts list --task-id {result.run.task_id}",
        ],
    }


def _find_run(store: LocalStore, run_id_or_task_id: str) -> TaskRun | None:
    run = store.get_task_run(run_id_or_task_id)
    if run is not None:
        return run
    matches = [
        candidate for candidate in store.list_task_runs() if candidate.task_id == run_id_or_task_id
    ]
    return matches[-1] if matches else None


def _run_inspection_payload(
    store: LocalStore,
    run: TaskRun,
    *,
    include_outputs: bool,
) -> dict[str, Any]:
    outputs = [output for output in store.list_run_outputs() if output.run_id == run.id]
    receipts = [
        receipt for receipt in store.list_receipts() if receipt.id in _run_receipt_ids(run, outputs)
    ]
    proposals = [
        proposal
        for proposal in store.list_proposals()
        if proposal.id in {item for output in outputs for item in output.memory_proposal_ids}
    ]
    handoff = store.get_handoff(run.handoff_id) if run.handoff_id else None
    return {
        "run": run.model_dump(mode="json", by_alias=True),
        "status": run.status,
        "phase": run.phase,
        "stop_reason": run.stop_reason,
        "next_allowed_action": _next_allowed_action(run),
        "receipts": [receipt.model_dump(mode="json", by_alias=True) for receipt in receipts],
        "outputs": [
            _run_output_payload(output, include_outputs=include_outputs) for output in outputs
        ],
        "memory_proposals": [
            proposal.model_dump(mode="json", by_alias=True) for proposal in proposals
        ],
        "handoff": handoff.model_dump(mode="json", by_alias=True) if handoff else None,
        "runner_metadata": run.runner_metadata,
    }


def _run_recovery_payload(
    store: LocalStore,
    run: TaskRun,
    *,
    dry_run: bool,
    reason: str | None,
) -> dict[str, Any]:
    outputs = [output for output in store.list_run_outputs() if output.run_id == run.id]
    return {
        "run_id": run.id,
        "task_id": run.task_id,
        "recoverable": True,
        "dry_run": dry_run,
        "reason": reason,
        "resume_phase": "continue" if run.iteration < run.max_iterations else "stop",
        "last_phase": run.phase,
        "last_iteration": run.iteration,
        "next_allowed_action": _next_allowed_action(run),
        "required_checks": [
            "reload task run state",
            "re-check policy grants",
            "re-check intent-lock stop conditions",
            "verify max-iteration budget",
        ],
        "output_ids": [output.id for output in outputs],
    }


def _run_output_payload(output: Any, *, include_outputs: bool) -> dict[str, Any]:
    payload = output.model_dump(mode="json", by_alias=True)
    if include_outputs:
        return dict(payload)
    return {
        "id": payload["id"],
        "run_id": payload["run_id"],
        "step_result_id": payload["step_result_id"],
        "phase": payload["phase"],
        "summary": payload["summary"],
        "diagnostics": payload["diagnostics"],
        "receipt_ids": payload["receipt_ids"],
        "memory_proposal_ids": payload["memory_proposal_ids"],
        "artifacts": payload["artifacts"],
        "redacted": payload["redacted"],
    }


def _run_receipt_ids(run: TaskRun, outputs: list[Any]) -> set[str]:
    output_receipt_ids = [receipt for output in outputs for receipt in output.receipt_ids]
    return {*run.receipt_ids, *output_receipt_ids}


def _next_allowed_action(run: TaskRun) -> str:
    if run.status == "interrupted":
        return "recover from the last safe boundary"
    if run.status == "blocked":
        return "resolve the blocking condition before recovery"
    if run.status == "failed":
        return "inspect diagnostics before deciding whether to retry"
    if run.status == "completed":
        return "review handoff, receipts, and memory proposals"
    return "continue within policy and iteration limits"
