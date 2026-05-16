"""Structured and Markdown handoff generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from craik.contracts.models import (
    CapabilityReceipt,
    CaseFile,
    Handoff,
    RunOutput,
    RunStatus,
    SelfAudit,
    TaskRun,
    TaskRunStatus,
)
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.context_debt import context_debt_summaries, records_from_case_file
from craik.runtime.intent_locks import IntentLockManager
from craik.runtime.receipts import ReceiptStore
from craik.runtime.redaction import redact
from craik.runtime.runner_metadata import (
    runner_metadata_from_receipt_metadata,
    unique_runner_metadata,
)
from craik.runtime.scratchpad import unknown_summaries
from craik.runtime.store import LocalStore


class HandoffError(RuntimeError):
    """Base error for handoff failures."""


class HandoffNotFoundError(HandoffError):
    """Raised when a requested handoff does not exist."""


class HandoffContextError(HandoffError):
    """Raised when required handoff context is missing."""


class RunHandoffContextError(HandoffContextError):
    """Raised when required run handoff context is missing."""


@dataclass(frozen=True)
class HandoffWriter:
    """Create structured handoff records and Markdown summaries."""

    store: LocalStore

    def create(
        self,
        *,
        task_id: str,
        agent: str,
        summary: str,
        status: RunStatus = "completed",
        completed_actions: list[str] | None = None,
        files_changed: list[str] | None = None,
        artifacts: list[str] | None = None,
        commands_run: list[str] | None = None,
        tests_run: list[str] | None = None,
        facts_learned: list[str] | None = None,
        facts_invalidated: list[str] | None = None,
        contradictions_opened: list[str] | None = None,
        risks: list[str] | None = None,
        next_steps: list[str] | None = None,
        memory_proposal_ids: list[str] | None = None,
        runner_metadata: list[dict[str, Any]] | None = None,
        policy_exceptions: list[str] | None = None,
        self_audit_notes: list[str] | None = None,
    ) -> Handoff:
        """Create, validate, persist, and return a structured handoff."""
        task = self.store.get_task(task_id)
        if task is None:
            raise HandoffContextError(f"unknown task: {task_id}")
        project = self.store.get_project(task.project_id)
        if project is None:
            raise HandoffContextError(f"unknown project for task {task_id}: {task.project_id}")

        case_file = CaseFileAssembler(self.store).latest_for_task(task_id)
        intent_lock = IntentLockManager(self.store).ensure_for_task(task)
        receipts = ReceiptStore(self.store).list_receipts(task_id=task_id)
        proposals = memory_proposal_ids or [
            proposal.id for proposal in self.store.list_proposals() if proposal.task_id == task_id
        ]
        assumptions = (
            [assumption.statement for assumption in case_file.assumptions] if case_file else []
        )
        debt_records = records_from_case_file(
            case_file,
            task_id=task_id,
            project_id=project.id,
            handoff_id=handoff_id(task_id),
        )
        context_debt = context_debt_summaries(debt_records)
        context_debt.extend(unknown_summaries(self.store, task_id))
        audit = _self_audit(
            receipts_reviewed=bool(receipts),
            assumptions_reviewed=bool(case_file),
            validation_recorded=bool(tests_run),
            policy_exceptions_disclosed=True,
            notes=self_audit_notes or [],
        )
        handoff = Handoff(
            id=handoff_id(task_id),
            task_id=task_id,
            project_id=project.id,
            intent_lock_id=intent_lock.id,
            agent=agent,
            status=status,
            summary=redact(summary).value,
            self_audit=audit,
            completed_actions=_redacted_strings(completed_actions),
            files_changed=files_changed or [],
            artifacts=artifacts or [],
            commands_run=_redacted_strings(commands_run),
            tests_run=tests_run or [],
            assumptions=assumptions,
            context_debt=context_debt,
            policy_exceptions=policy_exceptions or [],
            facts_learned=facts_learned or [],
            facts_invalidated=facts_invalidated or [],
            contradictions_opened=contradictions_opened or [],
            risks=_redacted_strings(risks),
            next_steps=_redacted_strings(next_steps),
            receipt_ids=[receipt.id for receipt in receipts],
            memory_proposal_ids=proposals,
            runner_metadata=_runner_metadata(receipts, runner_metadata),
            created_at=datetime.now(UTC),
        )
        self.store.put_handoff(handoff)
        for debt in debt_records:
            self.store.put_context_debt_record(debt)
        return handoff

    def create_from_run(
        self,
        run_id: str,
        *,
        agent: str | None = None,
        tests_run: list[str] | None = None,
        commands_run: list[str] | None = None,
    ) -> Handoff:
        """Create a handoff from a persisted task run and captured outputs."""
        run = self.store.get_task_run(run_id)
        if run is None:
            raise RunHandoffContextError(f"unknown task run: {run_id}")
        outputs = _outputs_for_run(self.store.list_run_outputs(), run.id)
        diagnostics = _run_diagnostics(outputs)
        output_receipt_ids = [receipt for output in outputs for receipt in output.receipt_ids]
        receipt_ids = _unique([*run.receipt_ids, *output_receipt_ids])
        proposals = _unique(
            [proposal for output in outputs for proposal in output.memory_proposal_ids]
        )
        runner_metadata = run.runner_metadata or [
            {
                "runner_id": run.runner_id,
                "execution_mode": run.runner_mode,
            }
        ]
        handoff = self.create(
            task_id=run.task_id,
            agent=agent or f"runner:{run.runner_id}",
            summary=_run_summary(run, outputs),
            status=_handoff_status(run.status),
            completed_actions=_run_completed_actions(run, outputs),
            artifacts=_unique([output.id for output in outputs]),
            commands_run=commands_run,
            tests_run=tests_run,
            memory_proposal_ids=proposals,
            runner_metadata=runner_metadata,
            risks=_run_risks(run, diagnostics),
            next_steps=_run_next_steps(run),
            self_audit_notes=diagnostics,
        )
        self.store.put_task_run(run.model_copy(update={"handoff_id": handoff.id}))
        for receipt_id in receipt_ids:
            if receipt_id not in handoff.receipt_ids:
                handoff = handoff.model_copy(
                    update={"receipt_ids": [*handoff.receipt_ids, receipt_id]}
                )
                self.store.put_handoff(handoff)
        return handoff

    def get(self, handoff_id_or_task_id: str) -> Handoff | None:
        """Load a handoff by handoff id or task id."""
        handoff = self.store.get_handoff(handoff_id_or_task_id)
        if handoff is not None:
            return handoff
        return self.store.get_handoff(handoff_id(handoff_id_or_task_id))

    def require(self, handoff_id_or_task_id: str) -> Handoff:
        """Load a handoff or raise a clear error."""
        handoff = self.get(handoff_id_or_task_id)
        if handoff is None:
            raise HandoffNotFoundError(f"unknown handoff or task: {handoff_id_or_task_id}")
        return handoff


def render_markdown(handoff: Handoff) -> str:
    """Render a deterministic Markdown handoff."""
    sections = [
        f"# Handoff: {handoff.task_id}",
        "",
        f"- Status: {handoff.status}",
        f"- Agent: {handoff.agent}",
        f"- Project: {handoff.project_id}",
        f"- Intent lock: {handoff.intent_lock_id or 'none'}",
        "",
        "## Summary",
        "",
        handoff.summary,
        "",
        "## Self-Audit",
        "",
        *_checklist(handoff.self_audit),
        "",
        "## Completed Actions",
        "",
        *_bullets(handoff.completed_actions),
        "",
        "## Validation",
        "",
        *_bullets(handoff.tests_run),
        "",
        "## Receipts",
        "",
        *_bullets(handoff.receipt_ids),
        "",
        "## Assumptions",
        "",
        *_bullets(handoff.assumptions),
        "",
        "## Context Debt",
        "",
        *_bullets(handoff.context_debt),
        "",
        "## Policy Exceptions",
        "",
        *_bullets(handoff.policy_exceptions),
        "",
        "## Memory Proposals",
        "",
        *_bullets(handoff.memory_proposal_ids),
        "",
        "## Runner Metadata",
        "",
        *_runner_metadata_bullets(handoff.runner_metadata),
        "",
        "## Next Steps",
        "",
        *_bullets(handoff.next_steps),
        "",
    ]
    return "\n".join(sections)


def handoff_id(task_id: str) -> str:
    """Return the stable handoff id for a task id."""
    return f"handoff_{task_id.removeprefix('task_')}"


def _handoff_status(status: TaskRunStatus) -> RunStatus:
    if status == "completed":
        return "completed"
    if status == "blocked":
        return "blocked"
    if status == "failed":
        return "failed"
    return "incomplete"


def _outputs_for_run(outputs: list[RunOutput], run_id: str) -> list[RunOutput]:
    return sorted(
        [output for output in outputs if output.run_id == run_id],
        key=lambda output: (output.created_at, output.id),
    )


def _run_summary(run: TaskRun, outputs: list[RunOutput]) -> str:
    reason = f" Stop reason: {run.stop_reason}" if run.stop_reason else ""
    return str(redact(
        f"Run {run.id} ended with status {run.status} at phase {run.phase} "
        f"after {run.iteration} iteration(s). Captured {len(outputs)} output(s).{reason}"
    ).value)


def _run_completed_actions(run: TaskRun, outputs: list[RunOutput]) -> list[str]:
    actions = [
        f"Recorded run {run.id} with status {run.status}.",
        f"Last phase: {run.phase}.",
    ]
    actions.extend(f"Captured output {output.id}: {output.summary}" for output in outputs)
    return _redacted_strings(actions)


def _run_diagnostics(outputs: list[RunOutput]) -> list[str]:
    return _redacted_strings(
        [diagnostic for output in outputs for diagnostic in output.diagnostics]
    )


def _run_risks(run: TaskRun, diagnostics: list[str]) -> list[str]:
    risks: list[str] = []
    if run.status in {"blocked", "failed", "interrupted"}:
        risks.append(run.stop_reason or f"Run ended as {run.status}.")
    risks.extend(diagnostics)
    return _redacted_strings(risks)


def _run_next_steps(run: TaskRun) -> list[str]:
    if run.status == "completed":
        return ["Review receipts, memory proposals, and merged handoff state."]
    if run.status == "blocked":
        return ["Resolve the blocking approval, context, or intent-lock condition."]
    if run.status == "failed":
        return ["Inspect diagnostics and decide whether recovery is appropriate."]
    if run.status == "interrupted":
        return ["Inspect run state and recover from the last safe boundary."]
    return ["Inspect run state before continuing."]


def _unique(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _self_audit(
    *,
    receipts_reviewed: bool,
    assumptions_reviewed: bool,
    validation_recorded: bool,
    policy_exceptions_disclosed: bool,
    notes: list[str],
) -> SelfAudit:
    return SelfAudit(
        schema_validated=True,
        redaction_reviewed=True,
        receipts_reviewed=receipts_reviewed,
        assumptions_reviewed=assumptions_reviewed,
        validation_recorded=validation_recorded,
        policy_exceptions_disclosed=policy_exceptions_disclosed,
        notes=notes,
    )


def _context_debt(case_file: CaseFile | None) -> list[str]:
    task_id = case_file.task_id if case_file is not None else "unknown"
    return context_debt_summaries(records_from_case_file(case_file, task_id=task_id))


def _runner_metadata(
    receipts: list[CapabilityReceipt],
    explicit: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    if explicit is not None:
        return unique_runner_metadata([redact(item).value for item in explicit])
    snapshots = [
        snapshot
        for receipt in receipts
        if (snapshot := runner_metadata_from_receipt_metadata(receipt.result.metadata)) is not None
    ]
    return unique_runner_metadata(snapshots)


def _runner_metadata_bullets(metadata: list[dict[str, Any]]) -> list[str]:
    if not metadata:
        return ["- none"]
    bullets: list[str] = []
    for item in metadata:
        runner_id = item.get("runner_id", "unknown")
        adapter = item.get("adapter", "unknown")
        version = item.get("adapter_version", "unknown")
        mode = item.get("execution_mode", "unknown")
        trust = item.get("trust_profile", {})
        trust_level = trust.get("level", "unknown") if isinstance(trust, dict) else "unknown"
        bullets.append(
            f"- {runner_id}: adapter={adapter}; version={version}; mode={mode}; trust={trust_level}"
        )
    return bullets


def _checklist(audit: SelfAudit) -> list[str]:
    return [
        f"- [{'x' if audit.schema_validated else ' '}] Schema validated",
        f"- [{'x' if audit.redaction_reviewed else ' '}] Redaction reviewed",
        f"- [{'x' if audit.receipts_reviewed else ' '}] Receipts reviewed",
        f"- [{'x' if audit.assumptions_reviewed else ' '}] Assumptions reviewed",
        f"- [{'x' if audit.validation_recorded else ' '}] Validation recorded",
        (
            f"- [{'x' if audit.policy_exceptions_disclosed else ' '}] "
            "Policy exceptions disclosed"
        ),
        *_bullets(audit.notes),
    ]


def _bullets(values: list[str]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _redacted_strings(values: list[str] | None) -> list[str]:
    return [str(redact(value).value) for value in values or []]
