"""Capture run outputs and reviewable memory proposals."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from craik.contracts.models import (
    MemoryProposal,
    MemoryScope,
    ProposalOperation,
    RunnerStepResult,
    RunOutput,
    TrustClass,
)
from craik.runtime.memory import MemoryStore, create_proposal, evidence_reference
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore

PROPOSAL_STATUSES = frozenset({"completed", "partial"})


@dataclass(frozen=True)
class RunOutputProposalSpec:
    """Memory proposal fields derived from a captured run output."""

    entity: str
    relation: str
    value: str | None = None
    source: str | None = None
    confidence: float = 0.7
    scope: MemoryScope = "team"
    trust_class: TrustClass = "reported"
    operation: ProposalOperation = "add"
    handoff_id: str | None = None


@dataclass(frozen=True)
class RunOutputCapture:
    """Result of storing output and attempting proposal creation."""

    output: RunOutput
    proposals: list[MemoryProposal]
    skipped_reasons: list[str]


class RunOutputRecorder:
    """Persist observed step outputs and create reviewable proposals."""

    def __init__(self, store: LocalStore, memory: MemoryStore) -> None:
        self.store = store
        self.memory = memory

    def capture_step_result(
        self,
        step: RunnerStepResult,
        *,
        proposal_specs: list[RunOutputProposalSpec] | None = None,
        captured_at: datetime | None = None,
    ) -> RunOutputCapture:
        now = captured_at or datetime.now(UTC)
        output = RunOutput(
            id=run_output_id(step.run_id, step.id),
            run_id=step.run_id,
            step_result_id=step.id,
            task_id=step.task_id,
            phase=step.phase,
            summary=str(redact(step.summary).value),
            observed_output=_redacted_dict(step.observed_output),
            diagnostics=[str(redact(item).value) for item in step.diagnostics],
            receipt_ids=list(step.receipt_ids),
            memory_proposal_ids=[],
            artifacts=[str(redact(item).value) for item in step.artifacts],
            redacted=True,
            created_at=now,
        )

        specs = proposal_specs or []
        proposals: list[MemoryProposal] = []
        skipped_reasons: list[str] = []
        if step.status not in PROPOSAL_STATUSES:
            skipped_reasons.append(f"step status {step.status} does not create memory proposals")
        elif not specs:
            skipped_reasons.append("no memory proposal specs supplied")
        else:
            for spec in specs:
                proposal = self._proposal_from_output(output, spec)
                proposals.append(self.memory.propose(proposal))

        output = output.model_copy(update={"memory_proposal_ids": [item.id for item in proposals]})
        self.store.put_run_output(output)
        return RunOutputCapture(output=output, proposals=proposals, skipped_reasons=skipped_reasons)

    def _proposal_from_output(
        self,
        output: RunOutput,
        spec: RunOutputProposalSpec,
    ) -> MemoryProposal:
        source = spec.source or f"run:{output.run_id}"
        evidence = evidence_reference(
            task_id=output.task_id,
            source=source,
            locator=f"{output.id}#{output.step_result_id}",
            summary=output.summary,
        )
        proposal = create_proposal(
            task_id=output.task_id,
            entity=spec.entity,
            relation=spec.relation,
            value=spec.value or output.summary,
            source=source,
            confidence=spec.confidence,
            scope=spec.scope,
            trust_class=spec.trust_class,
            evidence=[evidence],
            operation=spec.operation,
        )
        return proposal.model_copy(
            update={
                "run_id": output.run_id,
                "step_id": output.step_result_id,
                "handoff_id": spec.handoff_id,
            }
        )


def run_output_id(run_id: str, step_result_id: str) -> str:
    """Return a stable output id for a run step result."""
    run_slug = run_id.removeprefix("run_")
    step_slug = step_result_id.removeprefix("runner_step_result_")
    return f"runout_{run_slug}_{step_slug}"


def _redacted_dict(value: dict[str, object]) -> dict[str, object]:
    redacted = redact(value).value
    if isinstance(redacted, dict):
        return redacted
    return {}
