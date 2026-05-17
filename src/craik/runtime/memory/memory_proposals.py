"""Memory proposal lifecycle helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from craik.contracts.models import (
    EvidenceReference,
    FactValue,
    MemoryProposal,
    MemoryScope,
    ProposalOperation,
    TrustClass,
)
from craik.runtime.memory.memory_errors import EvidenceRequiredError
from craik.runtime.policy.redaction import redact


def create_proposal(
    *,
    task_id: str,
    entity: str,
    relation: str,
    value: str,
    source: str,
    confidence: float,
    scope: MemoryScope,
    trust_class: TrustClass,
    evidence: list[EvidenceReference],
    operation: ProposalOperation = "add",
) -> MemoryProposal:
    """Create a redacted reviewable memory proposal."""
    fact = FactValue(
        entity=str(redact(entity).value),
        relation=str(redact(relation).value),
        value=str(redact(value).value),
        source=str(redact(source).value),
        confidence=confidence,
        scope=scope,
        trust_class=trust_class,
    )
    return MemoryProposal(
        id=proposal_id(task_id, entity, relation),
        task_id=task_id,
        operation=operation,
        fact=fact,
        evidence=evidence,
        requires_approval=True,
        status="pending",
    )


def approve_proposal(
    proposal: MemoryProposal,
    *,
    decided_by: str,
    reason: str,
) -> MemoryProposal:
    """Approve a proposal after enforcing evidence requirements."""
    if not proposal.evidence:
        raise EvidenceRequiredError(f"proposal {proposal.id} requires evidence before approval")
    return proposal.model_copy(
        update={
            "status": "approved",
            "decision_reason": reason,
            "decided_by": decided_by,
            "decided_at": datetime.now(UTC),
        }
    )


def reject_proposal(
    proposal: MemoryProposal,
    *,
    decided_by: str,
    reason: str,
) -> MemoryProposal:
    """Reject a proposal with reviewer context."""
    return proposal.model_copy(
        update={
            "status": "rejected",
            "decision_reason": reason,
            "decided_by": decided_by,
            "decided_at": datetime.now(UTC),
        }
    )


def proposal_id(task_id: str, entity: str, relation: str) -> str:
    """Create a stable proposal id."""
    return f"memprop_{task_id.removeprefix('task_')}_{_slug(entity)}_{_slug(relation)}"


def evidence_reference(
    *,
    task_id: str,
    source: str,
    locator: str,
    summary: str,
) -> EvidenceReference:
    """Create an evidence reference for a memory proposal."""
    return EvidenceReference(
        id=f"evidence_{task_id}_{_slug(source)}_{_slug(locator)}",
        source=str(redact(source).value),
        kind="other",
        locator=str(redact(locator).value),
        summary=str(redact(summary).value),
        captured_at=datetime.now(UTC),
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "value"
