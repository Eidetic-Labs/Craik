"""Command-line interface for Craik."""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated, cast

import typer

from craik import __version__
from craik.contracts.models import PolicyProfile, Priority, TaskMode
from craik.contracts.registry import schema_model, schema_names
from craik.runtime.case_files import (
    CaseFileAssembler,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from craik.runtime.paths import CraikPaths, ensure_craik_home, resolve_craik_paths
from craik.runtime.policy import (
    FailOpenNotAllowedError,
    fail_open_receipt,
    generate_policy_envelope,
)
from craik.runtime.project_registry import NotGitRepositoryError, ProjectRegistry
from craik.runtime.receipts import ReceiptNotFoundError, ReceiptStore
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task

PACKAGE_NAME = "craik"

app = typer.Typer(
    add_completion=False,
    help="Durable agent runtime for shared project models and governed multi-agent work.",
    no_args_is_help=True,
)
schema_app = typer.Typer(help="Inspect Craik runtime contract schemas.")
app.add_typer(schema_app, name="schema")
home_app = typer.Typer(help="Inspect and initialize Craik local state paths.")
app.add_typer(home_app, name="home")
project_app = typer.Typer(help="Register and inspect Craik projects.")
app.add_typer(project_app, name="project")
task_app = typer.Typer(help="Create and inspect Craik tasks.")
app.add_typer(task_app, name="task")
case_app = typer.Typer(help="Build and inspect Craik case files.")
app.add_typer(case_app, name="case")
policy_app = typer.Typer(help="Inspect Craik policy profiles.")
app.add_typer(policy_app, name="policy")
receipts_app = typer.Typer(help="Inspect persisted capability receipts.")
app.add_typer(receipts_app, name="receipts")


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


@home_app.command("show")
def home_show() -> None:
    """Print resolved Craik local state paths without creating directories."""
    paths = resolve_craik_paths()
    typer.echo(json.dumps(_paths_payload(paths), indent=2, sort_keys=True))


@home_app.command("init")
def home_init() -> None:
    """Create Craik local state directories."""
    paths = ensure_craik_home()
    typer.echo(json.dumps(_paths_payload(paths), indent=2, sort_keys=True))


def _paths_payload(paths: CraikPaths) -> dict[str, str]:
    return {
        "cache": str(paths.cache),
        "case_files": str(paths.case_files),
        "config": str(paths.config),
        "handoffs": str(paths.handoffs),
        "home": str(paths.home),
        "logs": str(paths.logs),
        "projects": str(paths.projects),
        "receipts": str(paths.receipts),
        "secrets": str(paths.secrets),
        "state": str(paths.state),
    }


@project_app.command("add")
def project_add(
    path: Annotated[
        Path,
        typer.Argument(help="Path inside the Git repository to register."),
    ],
    name: Annotated[
        str | None,
        typer.Option("--name", help="Project name. Defaults to the repository directory name."),
    ] = None,
    docs_path: Annotated[
        list[str] | None,
        typer.Option("--docs-path", help="Documentation path to include. May be repeated."),
    ] = None,
    immutable_path: Annotated[
        list[str] | None,
        typer.Option("--immutable-path", help="Immutable path to include. May be repeated."),
    ] = None,
) -> None:
    """Register a Git project."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        registry = ProjectRegistry(store)
        project = registry.add_project(
            path,
            name=name,
            docs_paths=tuple(docs_path or ()),
            immutable_paths=tuple(immutable_path or ()),
        )
    except NotGitRepositoryError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(json.dumps(project.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@project_app.command("list")
def project_list() -> None:
    """List registered projects."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        registry = ProjectRegistry(store)
        projects = registry.list_projects()
    finally:
        store.close()

    payload = [project.model_dump(mode="json", by_alias=True) for project in projects]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@project_app.command("show")
def project_show(project: str) -> None:
    """Show one registered project by id or name."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        registry = ProjectRegistry(store)
        profile = registry.get_project(project)
    finally:
        store.close()

    if profile is None:
        raise typer.BadParameter(f"unknown project: {project}")
    typer.echo(json.dumps(profile.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@task_app.command("create")
def task_create(
    title: Annotated[str, typer.Option("--title", help="Task title.")],
    objective: Annotated[str, typer.Option("--objective", help="Task objective.")],
    project: Annotated[str, typer.Option("--project", help="Registered project id or name.")],
    requested_by: Annotated[
        str,
        typer.Option("--requested-by", help="Requester identity to store on the task."),
    ] = "user:local",
    priority: Annotated[
        str,
        typer.Option("--priority", help="Priority: low, normal, high, or urgent."),
    ] = "normal",
    mode: Annotated[
        str,
        typer.Option("--mode", help="Mode: plan, review, implement, or verify."),
    ] = "implement",
    constraint: Annotated[
        list[str] | None,
        typer.Option("--constraint", help="Task constraint. May be repeated."),
    ] = None,
    expected_output: Annotated[
        list[str] | None,
        typer.Option("--expected-output", help="Expected output. May be repeated."),
    ] = None,
) -> None:
    """Create a task request for a registered project."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        registry = ProjectRegistry(store)
        profile = registry.get_project(project)
        if profile is None:
            raise typer.BadParameter(f"unknown project: {project}")
        task = create_task(
            store,
            title=title,
            objective=objective,
            project_id=profile.id,
            requested_by=requested_by,
            priority=_priority(priority),
            mode=_task_mode(mode),
            constraints=constraint,
            expected_outputs=expected_output,
        )
    finally:
        store.close()

    typer.echo(json.dumps(task.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@case_app.command("build")
def case_build(
    task_id: Annotated[str, typer.Argument(help="Task id to build a case file for.")],
    max_tokens: Annotated[
        int,
        typer.Option("--max-tokens", min=1, help="Approximate context budget."),
    ] = 24000,
) -> None:
    """Build and persist a deterministic case file for a task."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        assembler = CaseFileAssembler(store)
        case_file = assembler.build(task_id, max_tokens=max_tokens)
    except (TaskNotFoundError, ProjectNotFoundError) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(case_file.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@case_app.command("show")
def case_show(case_or_task_id: str) -> None:
    """Show one persisted case file by case id or task id."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        assembler = CaseFileAssembler(store)
        case_file = assembler.get(case_or_task_id) or assembler.latest_for_task(case_or_task_id)
    finally:
        store.close()

    if case_file is None:
        raise typer.BadParameter(f"unknown case file or task: {case_or_task_id}")
    typer.echo(
        json.dumps(case_file.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@policy_app.command("show")
def policy_show(
    task_id: Annotated[
        str,
        typer.Option("--task-id", help="Task id for the envelope."),
    ] = "task_preview",
    actor: Annotated[
        str,
        typer.Option("--actor", help="Actor for the envelope."),
    ] = "agent:preview",
    profile: Annotated[
        str,
        typer.Option("--profile", help="Policy profile: strict, trusted-local, or automation."),
    ] = "strict",
    trusted_local_fail_open: Annotated[
        bool,
        typer.Option(
            "--trusted-local-fail-open",
            help="Explicitly opt in to trusted-local fail-open semantics.",
        ),
    ] = False,
    include_receipt: Annotated[
        bool,
        typer.Option("--include-receipt", help="Include the fail-open receipt when applicable."),
    ] = False,
) -> None:
    """Print a generated policy envelope."""
    policy_profile = _policy_profile(profile)
    try:
        envelope = generate_policy_envelope(
            task_id=task_id,
            actor=actor,
            profile=policy_profile,
            trusted_local_fail_open=trusted_local_fail_open,
        )
    except FailOpenNotAllowedError as error:
        raise typer.BadParameter(str(error)) from None

    payload: dict[str, object] = {
        "policy_envelope": envelope.model_dump(mode="json", by_alias=True),
    }
    if include_receipt and envelope.fail_open:
        receipt = fail_open_receipt(
            task_id=task_id,
            actor=actor,
            target=profile,
            reason="Policy preview requested fail-open receipt.",
        )
        payload["receipt"] = receipt.model_dump(mode="json", by_alias=True)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@receipts_app.command("list")
def receipts_list(
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Only include receipts for this task id."),
    ] = None,
    policy_id: Annotated[
        str | None,
        typer.Option("--policy-id", help="Only include receipts linked to this policy envelope."),
    ] = None,
    handoff_id: Annotated[
        str | None,
        typer.Option("--handoff-id", help="Only include receipts linked to this handoff."),
    ] = None,
) -> None:
    """Print persisted capability receipts as JSON."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        receipt_store = ReceiptStore(store)
        receipts = receipt_store.list_receipts(
            task_id=task_id,
            policy_id=policy_id,
            handoff_id=handoff_id,
        )
    finally:
        store.close()

    payload = [receipt.model_dump(mode="json", by_alias=True) for receipt in receipts]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@receipts_app.command("show")
def receipts_show(receipt_id: str) -> None:
    """Print one capability receipt by id as JSON."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        receipt_store = ReceiptStore(store)
        receipt = receipt_store.require_receipt(receipt_id)
    except ReceiptNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(receipt.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


def _policy_profile(value: str) -> PolicyProfile:
    if value in {"strict", "trusted-local", "automation"}:
        return cast(PolicyProfile, value)
    raise typer.BadParameter(f"unknown policy profile: {value}")


def _priority(value: str) -> Priority:
    if value in {"low", "normal", "high", "urgent"}:
        return cast(Priority, value)
    raise typer.BadParameter(f"unknown priority: {value}")


def _task_mode(value: str) -> TaskMode:
    if value in {"plan", "review", "implement", "verify"}:
        return cast(TaskMode, value)
    raise typer.BadParameter(f"unknown task mode: {value}")


def main() -> None:
    """Execute the Craik CLI."""
    app()
