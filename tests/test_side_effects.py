from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityTarget,
    DocsProfile,
    FactValue,
    MemoryProposal,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy import generate_policy_envelope
from craik.runtime.side_effects import (
    run_github_write,
    run_shell_command_ref,
    write_memory_fact,
    write_policy_file,
)
from craik.runtime.store import LocalStore


@pytest.fixture
def store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_shell_wrapper_requires_grant_and_persists_denial(store: LocalStore) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")

    result = run_shell_command_ref(
        store=store,
        policy=policy,
        grants=[],
        actor="agent:codex",
        command_ref="pytest",
    )

    assert result.allowed is False
    assert result.receipt.result.status == "denied"
    assert store.get_receipt(result.receipt.id) == result.receipt


def test_shell_wrapper_runs_command_reference_with_receipt(store: LocalStore) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")

    result = run_shell_command_ref(
        store=store,
        policy=policy,
        grants=[_grant("shell.execute", operations=["execute"])],
        actor="agent:codex",
        command_ref="pytest",
        executor=lambda command_ref: {"command_ref": command_ref, "stdout": "ok"},
    )

    assert result.allowed is True
    assert result.output == {"command_ref": "pytest", "stdout": "ok"}
    assert result.receipt.result.status == "passed"
    assert result.receipt.result.metadata["environment_action"] == "sandbox_action"
    assert "output" in result.receipt.result.metadata
    assert store.get_receipt(result.receipt.id) == result.receipt


def test_file_write_wrapper_enforces_immutable_paths_and_writes_allowed_file(
    store: LocalStore,
    tmp_path: Path,
) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")
    docs = DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"])

    denied = write_policy_file(
        store=store,
        policy=policy,
        grants=[_grant("repo.write.immutable", paths=["docs/adr/**"], operations=["write"])],
        actor="agent:codex",
        repo_root=tmp_path,
        relative_path="docs/adr/0001.md",
        content="secret=raw",
        docs=docs,
    )
    allowed = write_policy_file(
        store=store,
        policy=policy,
        grants=[_grant("repo.write.docs", paths=["docs/**"], operations=["write"])],
        actor="agent:codex",
        repo_root=tmp_path,
        relative_path="docs/index.md",
        content="api_key=raw",
        docs=docs,
    )

    assert denied.allowed is False
    assert denied.receipt.result.status == "denied"
    assert allowed.allowed is True
    assert (tmp_path / "docs" / "index.md").read_text() == "api_key=[REDACTED]"
    assert allowed.receipt.result.metadata["bytes_written"] > 0


def test_file_write_wrapper_rejects_path_escape(
    store: LocalStore,
    tmp_path: Path,
) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")

    with pytest.raises(ValueError, match="escapes repository root"):
        write_policy_file(
            store=store,
            policy=policy,
            grants=[_grant("repo.write.docs", paths=["../outside.md"], operations=["write"])],
            actor="agent:codex",
            repo_root=tmp_path,
            relative_path="../outside.md",
            content="outside",
            docs=DocsProfile(paths=["docs/"], immutable_paths=[]),
        )


def test_memory_write_wrapper_requires_policy_grant_and_records_receipt(
    store: LocalStore,
) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")
    memory = _WritableMemory()
    fact = FactValue(
        entity="repo:Eidetic-Labs/Craik",
        relation="craik:test",
        value="side effect completed",
        source="agent:codex",
        confidence=1.0,
        scope="local",
        trust_class="observed",
    )

    denied = write_memory_fact(
        store=store,
        memory=memory,
        policy=policy,
        grants=[],
        actor="agent:codex",
        fact=fact,
    )
    allowed = write_memory_fact(
        store=store,
        memory=memory,
        policy=policy,
        grants=[_grant("memory.write", operations=["write"])],
        actor="agent:codex",
        fact=fact,
    )

    assert denied.allowed is False
    assert allowed.allowed is True
    assert memory.facts == [fact]
    assert allowed.receipt.capability == "memory.write"
    assert allowed.receipt.result.metadata["entity"] == fact.entity


def test_github_write_wrapper_requires_grant_and_redacts_result(store: LocalStore) -> None:
    policy = generate_policy_envelope(task_id="task_side_effect", actor="agent:codex")

    denied = run_github_write(
        store=store,
        policy=policy,
        grants=[],
        actor="agent:codex",
        operation="create_pr",
        target="Eidetic-Labs/Craik",
    )
    allowed = run_github_write(
        store=store,
        policy=policy,
        grants=[_grant("github.write", operations=["create_pr"])],
        actor="agent:codex",
        operation="create_pr",
        target="Eidetic-Labs/Craik",
        writer=lambda operation, target: {
            "operation": operation,
            "target": target,
            "token": "ghp-secret-token",
        },
    )

    assert denied.allowed is False
    assert allowed.allowed is True
    assert allowed.receipt.result.metadata["github_result"]["token"] == "[REDACTED]"
    assert store.get_receipt(allowed.receipt.id) == allowed.receipt


class _WritableMemory:
    def __init__(self) -> None:
        self.facts: list[FactValue] = []

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        return proposal

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        return None

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        return []

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        raise NotImplementedError

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        raise NotImplementedError

    def search(self, query: str) -> list[FactValue]:
        return []

    def write_fact(self, fact: FactValue) -> FactValue:
        self.facts.append(fact)
        return fact


def _grant(
    capability: str,
    *,
    operations: list[str],
    paths: list[str] | None = None,
) -> CapabilityGrant:
    return CapabilityGrant(
        id=f"grant_{capability.replace('.', '_')}",
        task_id="task_side_effect",
        capability=capability,
        target=CapabilityTarget(paths=paths or []),
        operations=operations,
        reason="Allow side effect.",
        approved_by="user:maintainer",
        expires_at=datetime(2026, 5, 17, tzinfo=UTC),
    )
