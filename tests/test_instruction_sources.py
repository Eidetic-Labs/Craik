from pathlib import Path

import pytest
from pydantic import ValidationError

from craik.contracts.models import (
    INSTRUCTION_SOURCE_DEFAULT_PATHS,
    InstructionSource,
    InstructionSourceRegistry,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _source(kind: str, path: str | None = None, active: bool = True) -> InstructionSource:
    return InstructionSource(
        id=f"instruction_source_{kind}",
        project_id="project_docs",
        kind=kind,
        path=path if path is not None else INSTRUCTION_SOURCE_DEFAULT_PATHS[kind],
        owner="team:runtime",
        trust_boundary="project",
        active=active,
        declared_by="agent:orchestrator",
        created_at="2026-05-15T22:30:00Z",
    )


@pytest.mark.parametrize(
    "kind",
    [
        "agents_md",
        "claude_md",
        "gemini_md",
        "hermes_md",
        "skills_md",
        "cursor_rules",
        "github_copilot_instructions",
        "codex_instructions",
    ],
)
def test_standard_instruction_source_paths_are_supported(kind: str) -> None:
    source = _source(kind)

    assert source.path == INSTRUCTION_SOURCE_DEFAULT_PATHS[kind]
    assert source.active is True


def test_policy_doc_sources_require_declared_path() -> None:
    source = _source("policy_doc", path="docs/policies/runtime.md")

    assert source.path == "docs/policies/runtime.md"


def test_instruction_source_registry_round_trips(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        agents = _source("agents_md")
        policy = _source("policy_doc", path="docs/policies/runtime.md")
        registry = InstructionSourceRegistry(
            id="instruction_registry_project_docs",
            project_id="project_docs",
            sources=[policy, agents],
            active_source_ids=[agents.id, policy.id],
            declared_policy_doc_paths=[policy.path],
            created_at="2026-05-15T22:31:00Z",
        )

        store.put_instruction_source(agents)
        store.put_instruction_source(policy)
        store.put_instruction_source_registry(registry)

        assert store.get_instruction_source(agents.id) == agents
        assert store.get_instruction_source_registry(registry.id) == registry
        assert store.list_instruction_sources() == [agents, policy]
        assert store.list_instruction_source_registries() == [registry]
    finally:
        store.close()


def test_standard_source_rejects_noncanonical_path() -> None:
    with pytest.raises(ValidationError, match="agents_md instruction source path"):
        _source("agents_md", path="docs/AGENTS.md")


def test_registry_rejects_inactive_active_source() -> None:
    inactive = _source("skills_md", active=False)

    with pytest.raises(ValidationError, match="inactive instruction source ids"):
        InstructionSourceRegistry(
            id="instruction_registry_project_docs",
            project_id="project_docs",
            sources=[inactive],
            active_source_ids=[inactive.id],
            created_at="2026-05-15T22:31:00Z",
        )


def test_registry_requires_policy_doc_paths_to_match_sources() -> None:
    policy = _source("policy_doc", path="docs/policies/runtime.md")

    with pytest.raises(ValidationError, match="declared policy doc paths"):
        InstructionSourceRegistry(
            id="instruction_registry_project_docs",
            project_id="project_docs",
            sources=[policy],
            active_source_ids=[policy.id],
            declared_policy_doc_paths=["docs/policies/other.md"],
            created_at="2026-05-15T22:31:00Z",
        )
