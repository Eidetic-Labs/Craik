import subprocess
from pathlib import Path

import pytest

from craik.runtime.demos import DEMO_TASK_ID, StigmemDocsDemo
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


def test_stigmem_docs_demo_produces_runnable_artifacts(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)

    result = StigmemDocsDemo(store).run(repo_path=repo, github=False)

    assert result["schema"] == "craik.demo.stigmem_docs_reconciliation"
    assert result["status"] == "runnable"
    assert result["task"]["id"] == DEMO_TASK_ID
    assert result["project"]["memory"]["backend"] == "stigmem"
    assert result["stigmem_backend_status"]["status"] == "not_configured"
    assert result["case_file_id"] == "case_stigmem_documentation_reconciliation"
    assert result["receipt_ids"] == ["receipt_demo_stigmem_documentation_reconciliation"]
    assert result["handoff_id"] == "handoff_stigmem_documentation_reconciliation"
    assert result["memory_write"] == {
        "status": "proposal_created",
        "proposal_id": (
            "memprop_stigmem_documentation_reconciliation_repo_stigmem_"
            "craik_docs_reconciliation_demo"
        ),
        "direct_write": "not_requested",
    }
    assert result["memory_proposal_ids"] == [
        "memprop_stigmem_documentation_reconciliation_repo_stigmem_craik_docs_reconciliation_demo"
    ]
    assert [item["provider_id"] for item in result["provider_executions"]] == [
        "provider_openai",
        "provider_anthropic",
    ]
    assert {item["run_status"] for item in result["provider_executions"]} == {"completed"}
    assert {tuple(item["provider_families"]) for item in result["provider_executions"]} == {
        ("openai",),
        ("anthropic",),
    }
    assert result["work_graph_id"] == "graph_task_stigmem_documentation_reconciliation"
    assert store.get_task(DEMO_TASK_ID) is not None
    assert store.get_case_file("case_stigmem_documentation_reconciliation") is not None
    assert store.get_handoff("handoff_stigmem_documentation_reconciliation") is not None
    assert store.list_contradictions()[0].task_id == DEMO_TASK_ID
    assert len(store.list_run_outputs()) == 8
    assert any(
        receipt.result.metadata.get("policy_envelope_id")
        == "policy_task_stigmem_documentation_reconciliation"
        for receipt in store.list_receipts()
    )


def test_stigmem_docs_demo_surfaces_boundaries_and_evidence(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)

    result = StigmemDocsDemo(store).run(repo_path=repo, github=False)

    assert "ADRs are present and must remain immutable evidence." in result["findings"]["risks"]
    assert result["findings"]["evidence_ids"]
    assert any(
        "internal-only labels" in item
        for item in result["findings"]["public_internal_boundary"]
    )
    assert result["proposed_doc_updates"][0]["path"] == "README.md"


def test_stigmem_docs_demo_can_limit_provider_execution(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)

    result = StigmemDocsDemo(store).run(
        repo_path=repo,
        github=False,
        provider_ids=("provider_openai",),
    )

    assert [item["provider_id"] for item in result["provider_executions"]] == [
        "provider_openai"
    ]


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "stigmem"
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Stigmem\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "docs" / "adr" / "0001-record.md").write_text("# ADR\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        env={
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_AUTHOR_NAME": "Craik Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Craik Test",
        },
    )
