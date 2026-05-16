"""Structured and Markdown handoff generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from craik.contracts.models import CaseFile, Handoff, RunStatus, SelfAudit
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.intent_locks import IntentLockManager
from craik.runtime.receipts import ReceiptStore
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore


class HandoffError(RuntimeError):
    """Base error for handoff failures."""


class HandoffNotFoundError(HandoffError):
    """Raised when a requested handoff does not exist."""


class HandoffContextError(HandoffError):
    """Raised when required handoff context is missing."""


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
        context_debt = _context_debt(case_file)
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
            created_at=datetime.now(UTC),
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
        "## Next Steps",
        "",
        *_bullets(handoff.next_steps),
        "",
    ]
    return "\n".join(sections)


def handoff_id(task_id: str) -> str:
    """Return the stable handoff id for a task id."""
    return f"handoff_{task_id.removeprefix('task_')}"


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
    if case_file is None:
        return ["No case file was available for this handoff."]
    debt: list[str] = []
    omitted = case_file.context_budget.get("docs_omitted", [])
    if isinstance(omitted, list) and omitted:
        omitted_list = ", ".join(str(item) for item in omitted)
        debt.append(f"Documentation omitted by context budget: {omitted_list}")
    if case_file.github_state.get("status") == "not_loaded":
        debt.append("GitHub state was not loaded into the case file.")
    if not case_file.facts:
        debt.append("No memory facts were loaded into the case file.")
    return debt


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
