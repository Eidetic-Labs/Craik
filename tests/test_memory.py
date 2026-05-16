from pathlib import Path

import pytest

from craik.runtime.memory import (
    DirectMemoryWriteDeniedError,
    EphemeralMemoryStore,
    EvidenceRequiredError,
    LocalMemoryStore,
    create_proposal,
    evidence_reference,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_ephemeral_backend_proposal_lifecycle() -> None:
    backend = EphemeralMemoryStore()
    proposal = _proposal()

    backend.propose(proposal)
    approved = backend.approve(proposal.id, decided_by="user:reviewer", reason="Supported.")

    assert approved.status == "approved"
    assert approved.decided_by == "user:reviewer"
    assert backend.search("local proposals") == [approved.fact]


def test_local_backend_persists_proposals(store: LocalStore) -> None:
    backend = LocalMemoryStore(store)
    proposal = _proposal()

    backend.propose(proposal)

    assert backend.get_proposal(proposal.id) == proposal
    assert backend.list_proposals(task_id="task_docs", status="pending") == [proposal]


def test_approval_requires_evidence(store: LocalStore) -> None:
    proposal = create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:status",
        value="No evidence attached.",
        source="agent:codex",
        confidence=0.5,
        scope="local",
        trust_class="reported",
        evidence=[],
    )
    backend = LocalMemoryStore(store)
    backend.propose(proposal)

    with pytest.raises(EvidenceRequiredError, match="requires evidence"):
        backend.approve(proposal.id, decided_by="user:reviewer", reason="Unsupported.")


def test_reject_records_decision(store: LocalStore) -> None:
    backend = LocalMemoryStore(store)
    proposal = _proposal()
    backend.propose(proposal)

    rejected = backend.reject(proposal.id, decided_by="user:reviewer", reason="Too broad.")

    assert rejected.status == "rejected"
    assert rejected.decision_reason == "Too broad."
    assert backend.search("local proposals") == []


def test_direct_local_memory_write_requires_policy_grant(store: LocalStore) -> None:
    proposal = _proposal()

    with pytest.raises(DirectMemoryWriteDeniedError, match="memory.write grant"):
        LocalMemoryStore(store).write_fact(proposal.fact)


def _proposal():
    evidence = evidence_reference(
        task_id="task_docs",
        source="README.md",
        locator="README.md#memory",
        summary="README documents local proposals.",
    )
    return create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:memory",
        value="Local proposals require review before promotion.",
        source="README.md",
        confidence=0.9,
        scope="local",
        trust_class="observed",
        evidence=[evidence],
    )
