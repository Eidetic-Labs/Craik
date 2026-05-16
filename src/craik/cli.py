"""Command-line interface for Craik."""

from __future__ import annotations

import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated, cast

import typer

from craik import __version__
from craik.contracts.models import (
    MemoryScope,
    PolicyProfile,
    Priority,
    ProposalOperation,
    RunStatus,
    TaskMode,
    TrustClass,
)
from craik.contracts.registry import schema_model, schema_names
from craik.runtime.case_files import (
    CaseFileAssembler,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from craik.runtime.github import GitHubClient, GitHubConfig, GitHubReadAdapter
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
intent_app = typer.Typer(help="Inspect task intent locks.")
app.add_typer(intent_app, name="intent")
case_app = typer.Typer(help="Build and inspect Craik case files.")
app.add_typer(case_app, name="case")
connect_app = typer.Typer(help="Connect to external services.")
app.add_typer(connect_app, name="connect")
handoff_app = typer.Typer(help="Create and inspect Craik handoffs.")
app.add_typer(handoff_app, name="handoff")
memory_app = typer.Typer(help="Create and review local memory proposals.")
app.add_typer(memory_app, name="memory")
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
) -> None:
    """Build and persist a deterministic case file for a task."""
    store = LocalStore.from_env()
    try:
        store.initialize()
        github_adapter = _github_adapter() if github else None
        assembler = CaseFileAssembler(store, github_adapter=github_adapter)
        case_file = assembler.build(task_id, max_tokens=max_tokens)
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


def main() -> None:
    """Execute the Craik CLI."""
    app()
