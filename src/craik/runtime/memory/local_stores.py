"""Local memory proposal store implementations."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from craik.contracts.models import FactValue, MemoryProposal
from craik.runtime.memory import memory_proposals as _memory_proposals
from craik.runtime.memory.memory_errors import (
    DirectMemoryWriteDeniedError,
    MemoryProposalNotFoundError,
)
from craik.runtime.store import LocalStore


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
        return filter_proposals(proposals, task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = _memory_proposals.approve_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._proposals[proposal_id] = approved
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = _memory_proposals.reject_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._proposals[proposal_id] = rejected
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return search_facts(self._proposals.values(), query)


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
        return filter_proposals(self._store.list_proposals(), task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = _memory_proposals.approve_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._store.put_proposal(approved)
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = _memory_proposals.reject_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._store.put_proposal(rejected)
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return search_facts(self._store.list_proposals(), query)

    def write_fact(self, fact: FactValue) -> FactValue:
        """Reject direct durable writes until a policy-granted path exists."""
        message = "direct local memory writes require a memory.write grant"
        raise DirectMemoryWriteDeniedError(message)


def filter_proposals(
    proposals: list[MemoryProposal],
    *,
    task_id: str | None,
    status: str | None,
) -> list[MemoryProposal]:
    """Filter and sort proposals by task and status."""
    filtered = proposals
    if task_id is not None:
        filtered = [proposal for proposal in filtered if proposal.task_id == task_id]
    if status is not None:
        filtered = [proposal for proposal in filtered if proposal.status == status]
    return sorted(filtered, key=lambda proposal: proposal.id)


def search_facts(proposals: Iterable[MemoryProposal], query: str) -> list[FactValue]:
    """Return approved proposal facts matching a simple case-insensitive query."""
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


def require_proposal(proposal: MemoryProposal | None, proposal_id: str) -> MemoryProposal:
    """Return a proposal or raise the stable not-found error."""
    if proposal is None:
        raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
    return proposal
