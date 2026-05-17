"""Command-line interface for Craik."""

from __future__ import annotations

import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from pydantic import ValidationError

from craik import __version__
from craik.contracts.models import (
    ContradictionStatus,
    MemoryScope,
    PolicyProfile,
    Priority,
    ProposalOperation,
    RunStatus,
    TaskMode,
    TaskRun,
    TrustClass,
)
from craik.contracts.registry import schema_model, schema_names
from craik.runtime.case_files import (
    CaseFileAssembler,
    DiscoveryOverrides,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from craik.runtime.contradictions import ContradictionManager, ContradictionNotFoundError
from craik.runtime.demos import StigmemDocsDemo
from craik.runtime.doctor import run_doctor
from craik.runtime.gateway import default_gateway_config
from craik.runtime.github import GitHubClient, GitHubConfig, GitHubReadAdapter
from craik.runtime.graph import WorkGraphExporter, WorkGraphTaskNotFoundError
from craik.runtime.handoffs import (
    HandoffContextError,
    HandoffNotFoundError,
    HandoffWriter,
    render_markdown,
)
from craik.runtime.intent_locks import IntentLockManager, IntentLockNotFoundError
from craik.runtime.memory import (
    EvidenceRequiredError,
    LocalMemoryStore,
    MemoryProposalNotFoundError,
    StigmemClient,
    StigmemConfig,
    StigmemMemoryStore,
    build_memory_diff,
    create_proposal,
    evidence_reference,
    preview_memory_impact,
)
from craik.runtime.model_providers import (
    ModelProviderNotFoundError,
    default_model_provider_registry,
    provider_selection_payload,
)
from craik.runtime.onboarding import AgentOnboardingBuilder, OnboardingProjectNotFoundError
from craik.runtime.paths import CraikPaths, ensure_craik_home, resolve_craik_paths
from craik.runtime.policy import (
    FailOpenNotAllowedError,
    fail_open_receipt,
    generate_policy_envelope,
)
from craik.runtime.policy_tests import PolicyTestHarness
from craik.runtime.project_registry import NotGitRepositoryError, ProjectRegistry
from craik.runtime.prompts import (
    PromptCaseFileNotFoundError,
    PromptCompiler,
    PromptTaskNotFoundError,
)
from craik.runtime.receipts import ReceiptNotFoundError, ReceiptStore
from craik.runtime.runners import default_runner_capability_matrices, get_runner_capability_matrix
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task
from craik.runtime.update_guidance import update_guidance_payload

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
intent_app = typer.Typer(help="Inspect task intent locks.")
app.add_typer(intent_app, name="intent")
case_app = typer.Typer(help="Build and inspect Craik case files.")
app.add_typer(case_app, name="case")
connect_app = typer.Typer(help="Connect to external services.")
app.add_typer(connect_app, name="connect")
demo_app = typer.Typer(help="Run built-in Craik demos.")
app.add_typer(demo_app, name="demo")
contradictions_app = typer.Typer(help="Manage local contradiction reports.")
app.add_typer(contradictions_app, name="contradictions")
graph_app = typer.Typer(help="Export Craik work graphs.")
app.add_typer(graph_app, name="graph")
handoff_app = typer.Typer(help="Create and inspect Craik handoffs.")
app.add_typer(handoff_app, name="handoff")
memory_app = typer.Typer(help="Create and review local memory proposals.")
app.add_typer(memory_app, name="memory")
policy_app = typer.Typer(help="Inspect Craik policy profiles.")
app.add_typer(policy_app, name="policy")
receipts_app = typer.Typer(help="Inspect persisted capability receipts.")
app.add_typer(receipts_app, name="receipts")
run_app = typer.Typer(help="Inspect and recover single-agent task runs.")
app.add_typer(run_app, name="run")
runners_app = typer.Typer(help="Inspect runner capabilities and trust profiles.")
app.add_typer(runners_app, name="runners")
prompt_app = typer.Typer(help="Compile runner-ready prompts from Craik runtime state.")
app.add_typer(prompt_app, name="prompt")
provider_app = typer.Typer(help="Inspect and select model providers.")
app.add_typer(provider_app, name="provider")


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


@app.command("setup")
def setup_command(
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Optional project id for gateway configuration."),
    ] = None,
    gateway_enabled: Annotated[
        bool,
        typer.Option(
            "--enable-gateway/--disable-gateway",
            help="Enable or disable the persisted gateway configuration.",
        ),
    ] = False,
    gateway_bind_host: Annotated[
        str,
        typer.Option("--gateway-bind-host", help="Gateway bind host. Defaults to local only."),
    ] = "127.0.0.1",
    gateway_port: Annotated[
        int,
        typer.Option("--gateway-port", help="Gateway port."),
    ] = 8765,
    policy_envelope_id: Annotated[
        str | None,
        typer.Option("--policy-envelope-id", help="Policy envelope for gateway authority."),
    ] = None,
) -> None:
    """Initialize local state and write non-secret gateway setup output."""
    paths = ensure_craik_home()
    store = LocalStore.from_paths(paths)
    try:
        store.initialize()
        config = default_gateway_config(
            project_id=project_id,
            policy_envelope_id=policy_envelope_id,
        ).model_copy(
            update={
                "bind_host": gateway_bind_host,
                "port": gateway_port,
                "enabled": gateway_enabled,
            }
        )
        try:
            config = type(config).model_validate(config.model_dump(mode="json", by_alias=True))
        except ValidationError as error:
            raise typer.BadParameter(str(error)) from None
        store.put_gateway_config(config)
        payload = {
            "home": _paths_payload(paths),
            "gateway_config": config.model_dump(mode="json", by_alias=True),
            "secrets_written": False,
            "next_steps": [
                "Review gateway_config before enabling external ingress.",
                "Store channel secrets outside Craik config files.",
                "Run gateway diagnostics before starting the daemon.",
            ],
        }
    finally:
        store.close()

    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("doctor")
def doctor_command() -> None:
    """Run read-only diagnostics for local and gateway readiness."""
    paths = resolve_craik_paths()
    payload = run_doctor(paths, env=dict(os.environ))
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("update")
def update_command() -> None:
    """Print safe update guidance without modifying the installation."""
    payload = update_guidance_payload(installed_version=package_version())
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


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


@runners_app.command("matrix")
def runners_matrix(
    runner_id: Annotated[
        str | None,
        typer.Option("--runner", help="Runner id to inspect. Prints all runners when omitted."),
    ] = None,
) -> None:
    """Print runner capability matrix entries as JSON."""
    payload: Any
    if runner_id is None:
        payload = [
            matrix.model_dump(mode="json", by_alias=True)
            for matrix in default_runner_capability_matrices().values()
        ]
    else:
        try:
            payload = get_runner_capability_matrix(runner_id).model_dump(
                mode="json",
                by_alias=True,
            )
        except KeyError as error:
            raise typer.BadParameter(str(error)) from None

    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@provider_app.command("list")
def provider_list() -> None:
    """Print registered model providers as JSON."""
    registry = default_model_provider_registry()
    payload = [
        provider.model_dump(mode="json", by_alias=True)
        for provider in registry.list()
    ]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@provider_app.command("show")
def provider_show(provider_id: str) -> None:
    """Print one model provider as JSON."""
    registry = default_model_provider_registry()
    try:
        provider = registry.require(provider_id)
    except ModelProviderNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    payload = provider.model_dump(mode="json", by_alias=True)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@provider_app.command("select")
def provider_select(
    provider_id: str,
    mode: Annotated[
        str,
        typer.Option("--mode", help="Provider mode to select."),
    ] = "chat",
    policy_envelope_id: Annotated[
        str | None,
        typer.Option("--policy-envelope-id", help="Policy envelope linked to this selection."),
    ] = None,
    receipt_id: Annotated[
        list[str] | None,
        typer.Option("--receipt-id", help="Receipt id linked to this selection."),
    ] = None,
) -> None:
    """Print a redacted provider selection payload."""
    registry = default_model_provider_registry()
    try:
        provider = registry.require(provider_id)
        payload = provider_selection_payload(
            provider,
            mode=mode,
            policy_envelope_id=policy_envelope_id,
            receipt_ids=receipt_id,
        )
    except (ModelProviderNotFoundError, ValueError) as error:
        raise typer.BadParameter(str(error)) from None
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@prompt_app.command("compile")
def prompt_compile(
    task_id: str,
    runner_id: Annotated[
        str,
        typer.Option("--runner", help="Runner id from `craik runners matrix`."),
    ],
    expected_output_schema: Annotated[
        list[str] | None,
        typer.Option("--expected-output-schema", help="Expected output schema. May repeat."),
    ] = None,
) -> None:
    """Compile a deterministic policy-aware prompt for a task and runner."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        try:
            compiled = PromptCompiler(store).compile(
                task_id,
                runner_id=runner_id,
                expected_output_schemas=expected_output_schema,
            )
        except PromptTaskNotFoundError as error:
            raise typer.BadParameter(str(error)) from None
        except PromptCaseFileNotFoundError as error:
            raise typer.BadParameter(str(error)) from None
        except KeyError as error:
            raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(compiled.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


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
    discovery_include: Annotated[
        list[str] | None,
        typer.Option(
            "--discovery-include",
            help="Context discovery include override. May be repeated.",
        ),
    ] = None,
    discovery_exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--discovery-exclude",
            help="Context discovery exclude override. May be repeated.",
        ),
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
            discovery_include=tuple(discovery_include or ()),
            discovery_exclude=tuple(discovery_exclude or ()),
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
    accepted_interpretation: Annotated[
        str | None,
        typer.Option("--accepted-interpretation", help="Accepted interpretation of the request."),
    ] = None,
    in_scope: Annotated[
        list[str] | None,
        typer.Option("--in-scope", help="In-scope work. May be repeated."),
    ] = None,
    out_of_scope: Annotated[
        list[str] | None,
        typer.Option("--out-of-scope", help="Out-of-scope work. May be repeated."),
    ] = None,
    allowed_autonomy: Annotated[
        list[str] | None,
        typer.Option("--allowed-autonomy", help="Autonomous action allowed. May be repeated."),
    ] = None,
    stop_condition: Annotated[
        list[str] | None,
        typer.Option("--stop-condition", help="Condition that should stop execution."),
    ] = None,
    scope_change_rule: Annotated[
        list[str] | None,
        typer.Option("--scope-change-rule", help="Rule for handling scope changes."),
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
        intent_lock = IntentLockManager(store).create_for_task(
            task,
            accepted_interpretation=accepted_interpretation,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            allowed_autonomy=allowed_autonomy,
            stop_conditions=stop_condition,
            scope_change_rules=scope_change_rule,
        )
    finally:
        store.close()

    payload = {
        "task": task.model_dump(mode="json", by_alias=True),
        "intent_lock": intent_lock.model_dump(mode="json", by_alias=True),
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@intent_app.command("show")
def intent_show(intent_or_task_id: str) -> None:
    """Show one persisted intent lock by intent lock id or task id."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        intent_lock = IntentLockManager(store).require(intent_or_task_id)
    except IntentLockNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(intent_lock.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@case_app.command("build")
def case_build(
    task_id: Annotated[str, typer.Argument(help="Task id to build a case file for.")],
    max_tokens: Annotated[
        int,
        typer.Option("--max-tokens", min=1, help="Approximate context budget."),
    ] = 24000,
    github: Annotated[
        bool,
        typer.Option("--github/--no-github", help="Load read-only GitHub context."),
    ] = True,
    discovery_include: Annotated[
        list[str] | None,
        typer.Option(
            "--discovery-include",
            help="One-off context discovery include override. May be repeated.",
        ),
    ] = None,
    discovery_exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--discovery-exclude",
            help="One-off context discovery exclude override. May be repeated.",
        ),
    ] = None,
) -> None:
    """Build and persist a deterministic case file for a task."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        github_adapter = _github_adapter() if github else None
        assembler = CaseFileAssembler(store, github_adapter=github_adapter)
        case_file = assembler.build(
            task_id,
            max_tokens=max_tokens,
            discovery_overrides=DiscoveryOverrides(
                include=tuple(discovery_include or ()),
                exclude=tuple(discovery_exclude or ()),
            ),
        )
    except (TaskNotFoundError, ProjectNotFoundError) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(case_file.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


def _github_adapter() -> GitHubReadAdapter:
    config = GitHubConfig.from_env(dict(os.environ))
    return GitHubReadAdapter(GitHubClient(config))


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


@demo_app.command("stigmem-docs")
def demo_stigmem_docs(
    repo_path: Annotated[
        Path,
        typer.Option("--repo-path", help="Path inside the Stigmem Git repository."),
    ] = Path("."),
    project_name: Annotated[
        str,
        typer.Option("--project-name", help="Project name to register for the demo."),
    ] = "Stigmem",
    stigmem_url: Annotated[
        str | None,
        typer.Option("--stigmem-url", envvar="CRAIK_STIGMEM_URL", help="Stigmem node URL."),
    ] = None,
    stigmem_api_key: Annotated[
        str | None,
        typer.Option(
            "--stigmem-api-key",
            envvar="CRAIK_STIGMEM_API_KEY",
            help="Bearer API key. Prefer CRAIK_STIGMEM_API_KEY.",
        ),
    ] = None,
    github: Annotated[
        bool,
        typer.Option("--github/--no-github", help="Load read-only GitHub context."),
    ] = True,
    provider_id: Annotated[
        list[str] | None,
        typer.Option(
            "--provider-id",
            help=(
                "Provider id to exercise through the deterministic demo runner. "
                "Repeat to override the default OpenAI and Anthropic run."
            ),
        ),
    ] = None,
    max_tokens: Annotated[
        int,
        typer.Option("--max-tokens", min=1, help="Approximate case-file context budget."),
    ] = 24000,
) -> None:
    """Run the Stigmem documentation reconciliation demo."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        result = StigmemDocsDemo(
            store,
            github_adapter=_github_adapter() if github else None,
        ).run(
            repo_path=repo_path,
            project_name=project_name,
            stigmem_url=stigmem_url,
            stigmem_api_key=stigmem_api_key,
            github=github,
            provider_ids=tuple(provider_id) if provider_id else None,
            max_tokens=max_tokens,
        )
    except (
        NotGitRepositoryError,
        TaskNotFoundError,
        ProjectNotFoundError,
        HandoffContextError,
    ) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(json.dumps(result, indent=2, sort_keys=True))


@contradictions_app.command("open")
def contradiction_open(
    summary: Annotated[str, typer.Option("--summary", help="Contradiction summary.")],
    fact: Annotated[
        list[str],
        typer.Option("--fact", help="Conflicting fact id or statement. Repeat at least twice."),
    ],
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Task associated with this contradiction."),
    ] = None,
    affected_artifact: Annotated[
        list[str] | None,
        typer.Option("--affected-artifact", help="Affected artifact path or id."),
    ] = None,
    evidence_id: Annotated[
        list[str] | None,
        typer.Option("--evidence-id", help="Supporting evidence id."),
    ] = None,
    owner: Annotated[
        str | None,
        typer.Option("--owner", help="Owner responsible for resolution."),
    ] = None,
    proposed_resolution: Annotated[
        str | None,
        typer.Option("--proposed-resolution", help="Proposed resolution."),
    ] = None,
    stigmem_conflict_id: Annotated[
        str | None,
        typer.Option("--stigmem-conflict-id", help="Optional future Stigmem conflict id."),
    ] = None,
) -> None:
    """Open and persist a local contradiction report."""
    if len(fact) < 2:
        raise typer.BadParameter("at least two --fact values are required")
    store = LocalStore.from_env()
    try:
        store.initialize()
        report = ContradictionManager(store).open_report(
            task_id=task_id,
            facts=fact,
            summary=summary,
            affected_artifacts=affected_artifact or [],
            evidence_ids=evidence_id or [],
            owner=owner,
            proposed_resolution=proposed_resolution,
            stigmem_conflict_id=stigmem_conflict_id,
        )
    finally:
        store.close()

    typer.echo(json.dumps(report.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@contradictions_app.command("list")
def contradiction_list(
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Only include reports for this task."),
    ] = None,
    status: Annotated[
        str | None,
        typer.Option("--status", help="Only include reports with this status."),
    ] = None,
) -> None:
    """List local contradiction reports."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        reports = ContradictionManager(store).list_reports(
            task_id=task_id,
            status=_contradiction_status(status) if status else None,
        )
    finally:
        store.close()

    payload = [report.model_dump(mode="json", by_alias=True) for report in reports]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@contradictions_app.command("show")
def contradiction_show(report_id: str) -> None:
    """Show one local contradiction report and linked evidence."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        manager = ContradictionManager(store)
        report = manager.get_report(report_id)
        evidence = manager.evidence_for(report_id)
    except ContradictionNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    payload = {
        "contradiction": report.model_dump(mode="json", by_alias=True),
        "evidence": [item.model_dump(mode="json", by_alias=True) for item in evidence],
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@graph_app.command("export")
def graph_export(
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Only export graph objects for this task."),
    ] = None,
) -> None:
    """Export the local work graph as deterministic JSON."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        export = WorkGraphExporter(store).export(task_id=task_id)
    except WorkGraphTaskNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(json.dumps(export.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@handoff_app.command("create")
def handoff_create(
    task_id: Annotated[str, typer.Argument(help="Task id to create a handoff for.")],
    summary: Annotated[str, typer.Option("--summary", help="Handoff summary.")],
    agent: Annotated[str, typer.Option("--agent", help="Agent identity.")] = "agent:local",
    status: Annotated[
        str,
        typer.Option("--status", help="Status: completed, incomplete, blocked, or failed."),
    ] = "completed",
    completed_action: Annotated[
        list[str] | None,
        typer.Option("--completed-action", help="Completed action. May be repeated."),
    ] = None,
    file_changed: Annotated[
        list[str] | None,
        typer.Option("--file-changed", help="Changed file. May be repeated."),
    ] = None,
    artifact: Annotated[
        list[str] | None,
        typer.Option("--artifact", help="Artifact path or id. May be repeated."),
    ] = None,
    command_run: Annotated[
        list[str] | None,
        typer.Option("--command-run", help="Command run. May be repeated."),
    ] = None,
    test_run: Annotated[
        list[str] | None,
        typer.Option("--test-run", help="Validation run. May be repeated."),
    ] = None,
    risk: Annotated[
        list[str] | None,
        typer.Option("--risk", help="Residual risk. May be repeated."),
    ] = None,
    next_step: Annotated[
        list[str] | None,
        typer.Option("--next-step", help="Next step. May be repeated."),
    ] = None,
    policy_exception: Annotated[
        list[str] | None,
        typer.Option("--policy-exception", help="Policy exception or fail-open note."),
    ] = None,
    self_audit_note: Annotated[
        list[str] | None,
        typer.Option("--self-audit-note", help="Self-audit note. May be repeated."),
    ] = None,
    markdown: Annotated[
        bool,
        typer.Option("--markdown", help="Print Markdown instead of JSON."),
    ] = False,
) -> None:
    """Create a structured handoff for a task."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        writer = HandoffWriter(store)
        handoff = writer.create(
            task_id=task_id,
            agent=agent,
            summary=summary,
            status=_run_status(status),
            completed_actions=completed_action,
            files_changed=file_changed,
            artifacts=artifact,
            commands_run=command_run,
            tests_run=test_run,
            risks=risk,
            next_steps=next_step,
            policy_exceptions=policy_exception,
            self_audit_notes=self_audit_note,
        )
    except HandoffContextError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    if markdown:
        typer.echo(render_markdown(handoff))
    else:
        typer.echo(
            json.dumps(handoff.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
        )


@handoff_app.command("show")
def handoff_show(
    handoff_or_task_id: str,
    markdown: Annotated[
        bool,
        typer.Option("--markdown", help="Print Markdown instead of JSON."),
    ] = False,
) -> None:
    """Show one persisted handoff by handoff id or task id."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        handoff = HandoffWriter(store).require(handoff_or_task_id)
    except HandoffNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    if markdown:
        typer.echo(render_markdown(handoff))
    else:
        typer.echo(
            json.dumps(handoff.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
        )


@memory_app.command("propose")
def memory_propose(
    task_id: Annotated[str, typer.Argument(help="Task id for the proposal.")],
    entity: Annotated[str, typer.Option("--entity", help="Fact entity.")],
    relation: Annotated[str, typer.Option("--relation", help="Fact relation.")],
    value: Annotated[str, typer.Option("--value", help="Fact value.")],
    source: Annotated[str, typer.Option("--source", help="Fact source.")],
    evidence_source: Annotated[
        str,
        typer.Option("--evidence-source", help="Evidence source supporting the proposal."),
    ],
    evidence_locator: Annotated[
        str,
        typer.Option("--evidence-locator", help="Evidence locator supporting the proposal."),
    ],
    evidence_summary: Annotated[
        str,
        typer.Option("--evidence-summary", help="Evidence summary supporting the proposal."),
    ],
    confidence: Annotated[
        float,
        typer.Option("--confidence", min=0.0, max=1.0, help="Fact confidence."),
    ] = 0.8,
    scope: Annotated[
        str,
        typer.Option("--scope", help="Memory scope: local, team, company, or public."),
    ] = "local",
    trust_class: Annotated[
        str,
        typer.Option(
            "--trust-class",
            help="Trust class: observed, reported, inferred, policy, external, or stale-risk.",
        ),
    ] = "observed",
    operation: Annotated[
        str,
        typer.Option("--operation", help="Operation: add, update, or invalidate."),
    ] = "add",
) -> None:
    """Create a reviewable local memory proposal."""
    evidence = evidence_reference(
        task_id=task_id,
        source=evidence_source,
        locator=evidence_locator,
        summary=evidence_summary,
    )
    proposal = create_proposal(
        task_id=task_id,
        entity=entity,
        relation=relation,
        value=value,
        source=source,
        confidence=confidence,
        scope=_memory_scope(scope),
        trust_class=_trust_class(trust_class),
        operation=_proposal_operation(operation),
        evidence=[evidence],
    )
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposal = LocalMemoryStore(store).propose(proposal)
    finally:
        store.close()

    typer.echo(
        json.dumps(proposal.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@memory_app.command("list")
def memory_list(
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Only include proposals for this task id."),
    ] = None,
    status: Annotated[
        str | None,
        typer.Option("--status", help="Only include proposals with this status."),
    ] = None,
) -> None:
    """List local memory proposals."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposals = LocalMemoryStore(store).list_proposals(task_id=task_id, status=status)
    finally:
        store.close()

    payload = [proposal.model_dump(mode="json", by_alias=True) for proposal in proposals]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@memory_app.command("show")
def memory_show(proposal_id: str) -> None:
    """Show one local memory proposal."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposal = LocalMemoryStore(store).get_proposal(proposal_id)
    finally:
        store.close()

    if proposal is None:
        raise typer.BadParameter(f"unknown memory proposal: {proposal_id}")
    typer.echo(
        json.dumps(proposal.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@memory_app.command("approve")
def memory_approve(
    proposal_id: str,
    decided_by: Annotated[
        str,
        typer.Option("--decided-by", help="Reviewer identity."),
    ] = "user:local",
    reason: Annotated[
        str,
        typer.Option("--reason", help="Decision reason."),
    ] = "Evidence reviewed.",
) -> None:
    """Approve a local memory proposal for local search."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposal = LocalMemoryStore(store).approve(
            proposal_id,
            decided_by=decided_by,
            reason=reason,
        )
    except (MemoryProposalNotFoundError, EvidenceRequiredError) as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(proposal.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@memory_app.command("reject")
def memory_reject(
    proposal_id: str,
    decided_by: Annotated[
        str,
        typer.Option("--decided-by", help="Reviewer identity."),
    ] = "user:local",
    reason: Annotated[
        str,
        typer.Option("--reason", help="Decision reason."),
    ] = "Rejected during review.",
) -> None:
    """Reject a local memory proposal."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposal = LocalMemoryStore(store).reject(
            proposal_id,
            decided_by=decided_by,
            reason=reason,
        )
    except MemoryProposalNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    finally:
        store.close()

    typer.echo(
        json.dumps(proposal.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
    )


@memory_app.command("search")
def memory_search(query: str) -> None:
    """Search approved local memory facts."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        facts = LocalMemoryStore(store).search(query)
    finally:
        store.close()

    payload = [fact.model_dump(mode="json", by_alias=True) for fact in facts]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@memory_app.command("diff")
def memory_diff(task_id: str) -> None:
    """Print a run-scoped memory diff for local proposal activity."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposals = store.list_proposals()
        diff = build_memory_diff(task_id=task_id, proposals=proposals)
        store.put_memory_diff(diff)
    finally:
        store.close()

    typer.echo(json.dumps(diff.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True))


@memory_app.command("preview")
def memory_preview(task_id: str) -> None:
    """Preview local memory impact before promotion or direct writes."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        proposals = store.list_proposals()
        existing_facts = LocalMemoryStore(store).search("")
        preview = preview_memory_impact(
            task_id=task_id,
            proposals=proposals,
            existing_facts=existing_facts,
        )
        store.put_memory_impact_preview(preview)
    finally:
        store.close()

    typer.echo(
        json.dumps(preview.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True)
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


@policy_app.command("test")
def policy_test() -> None:
    """Run policy regression checks required for release gates."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        report = PolicyTestHarness(store).run()
    finally:
        store.close()

    payload = report.to_payload()
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    if report.status != "passed":
        raise typer.Exit(code=1)


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


def _run_status(value: str) -> RunStatus:
    if value in {"completed", "incomplete", "blocked", "failed"}:
        return cast(RunStatus, value)
    raise typer.BadParameter(f"unknown run status: {value}")


def _memory_scope(value: str) -> MemoryScope:
    if value in {"local", "team", "company", "public"}:
        return cast(MemoryScope, value)
    raise typer.BadParameter(f"unknown memory scope: {value}")


def _trust_class(value: str) -> TrustClass:
    if value in {"observed", "reported", "inferred", "policy", "external", "stale-risk"}:
        return cast(TrustClass, value)
    raise typer.BadParameter(f"unknown trust class: {value}")


def _proposal_operation(value: str) -> ProposalOperation:
    if value in {"add", "update", "invalidate"}:
        return cast(ProposalOperation, value)
    raise typer.BadParameter(f"unknown proposal operation: {value}")


def _contradiction_status(value: str) -> ContradictionStatus:
    if value in {"open", "resolved", "ignored"}:
        return cast(ContradictionStatus, value)
    raise typer.BadParameter(f"unknown contradiction status: {value}")


def main() -> None:
    """Execute the Craik CLI."""
    app()
