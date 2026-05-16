"""Memory backend interfaces and local proposal flow."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Protocol

from craik.contracts.models import (
    EvidenceReference,
    FactValue,
    MemoryProposal,
    MemoryScope,
    ProposalOperation,
    TrustClass,
)
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore


class MemoryError(RuntimeError):
    """Base error for memory backend failures."""


class MemoryProposalNotFoundError(MemoryError):
    """Raised when a proposal cannot be found."""


class EvidenceRequiredError(MemoryError):
    """Raised when promotion is attempted without evidence."""


class DirectMemoryWriteDeniedError(MemoryError):
    """Raised when direct writes are attempted without a policy grant."""


class MemoryStore(Protocol):
    """Common memory backend behavior used by Craik."""

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        """Store a reviewable memory proposal."""

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        """Load one proposal."""

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        """List proposals with optional filters."""

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        """Approve a proposal for local memory use."""

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        """Reject a proposal."""

    def search(self, query: str) -> list[FactValue]:
        """Search approved local facts."""


class EphemeralMemoryStore:
    """In-memory backend for tests and demos."""

    def __init__(self) -> None:
        self._proposals: dict[str, MemoryProposal] = {}

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        self._proposals[proposal.id] = proposal
        return proposal

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        return self._proposals.get(proposal_id)

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        proposals = sorted(self._proposals.values(), key=lambda proposal: proposal.id)
        return _filter_proposals(proposals, task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = approve_proposal(proposal, decided_by=decided_by, reason=reason)
        self._proposals[proposal_id] = approved
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = reject_proposal(proposal, decided_by=decided_by, reason=reason)
        self._proposals[proposal_id] = rejected
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return _search_facts(self._proposals.values(), query)


class LocalMemoryStore:
    """SQLite-backed local memory proposal store."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        self._store.put_proposal(proposal)
        return proposal

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        return self._store.get_proposal(proposal_id)

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        return _filter_proposals(self._store.list_proposals(), task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = approve_proposal(proposal, decided_by=decided_by, reason=reason)
        self._store.put_proposal(approved)
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = reject_proposal(proposal, decided_by=decided_by, reason=reason)
        self._store.put_proposal(rejected)
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return _search_facts(self._store.list_proposals(), query)

    def write_fact(self, fact: FactValue) -> FactValue:
        """Reject direct durable writes until a policy-granted path exists."""
        message = "direct local memory writes require a memory.write grant"
        raise DirectMemoryWriteDeniedError(message)


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


def _filter_proposals(
    proposals: list[MemoryProposal],
    *,
    task_id: str | None,
    status: str | None,
) -> list[MemoryProposal]:
    filtered = proposals
    if task_id is not None:
        filtered = [proposal for proposal in filtered if proposal.task_id == task_id]
    if status is not None:
        filtered = [proposal for proposal in filtered if proposal.status == status]
    return sorted(filtered, key=lambda proposal: proposal.id)


def _search_facts(proposals: Iterable[MemoryProposal], query: str) -> list[FactValue]:
    needle = query.lower()
    facts: list[FactValue] = []
    for proposal in proposals:
        if proposal.status != "approved":
            continue
        haystack = " ".join(
            (
                proposal.fact.entity,
                proposal.fact.relation,
                proposal.fact.value,
                proposal.fact.source,
            )
        ).lower()
        if needle in haystack:
            facts.append(proposal.fact)
    return sorted(facts, key=lambda fact: (fact.entity, fact.relation, fact.source))


def _require_proposal(proposal: MemoryProposal | None, proposal_id: str) -> MemoryProposal:
    if proposal is None:
        raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
    return proposal


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "value"
