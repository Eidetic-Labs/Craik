from pathlib import Path

import pytest

from craik.contracts.models import EvidenceReference, TaskRequest
from craik.runtime.memory.contradictions import ContradictionManager, ContradictionNotFoundError
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore
from craik.runtime.work.graph import WorkGraphExporter


@pytest.fixture
def store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_contradiction_lifecycle_and_filters(store: LocalStore) -> None:
    manager = ContradictionManager(store)

    report = manager.open_report(
        task_id="task_docs",
        facts=["fact_old", "fact_new"],
        summary="Docs conflict with implementation.",
        affected_artifacts=["README.md"],
        evidence_ids=["evidence_docs"],
        owner="user:maintainer",
        proposed_resolution="Update docs.",
    )

    assert report.status == "open"
    assert report.task_id == "task_docs"
    assert report.affected_artifacts == ["README.md"]
    assert manager.get_report(report.id) == report
    assert manager.list_reports(task_id="task_docs", status="open") == [report]
    assert manager.list_reports(task_id="task_other") == []


def test_contradiction_links_stored_evidence(store: LocalStore) -> None:
    evidence = EvidenceReference(
        id="evidence_docs",
        source="README.md",
        kind="file",
        locator="README.md#status",
        summary="README status section.",
    )
    store.put_evidence(evidence)
    report = ContradictionManager(store).open_report(
        task_id="task_docs",
        facts=["fact_old", "fact_new"],
        summary="Docs conflict with implementation.",
        affected_artifacts=["README.md"],
        evidence_ids=[evidence.id, "evidence_missing"],
    )

    linked = ContradictionManager(store).evidence_for(report.id)

    assert linked == [evidence]


def test_contradiction_reports_link_into_work_graph(store: LocalStore) -> None:
    task = TaskRequest(
        id="task_docs",
        title="Review docs",
        objective="Find contradictions.",
        project_id="project_docs",
        requested_by="user:maintainer",
        mode="review",
        created_at="2026-05-15T22:30:00Z",
    )
    evidence = EvidenceReference(
        id="evidence_docs",
        source="README.md",
        kind="file",
        locator="README.md#status",
        summary="README status section.",
    )
    store.put_task(task)
    store.put_evidence(evidence)
    report = ContradictionManager(store).open_report(
        task_id=task.id,
        facts=["fact_old", "fact_new"],
        summary="Docs conflict with implementation.",
        affected_artifacts=["README.md"],
        evidence_ids=[evidence.id],
    )

    export = WorkGraphExporter(store).export(task_id=task.id)
    edges = {(edge.type, edge.from_node, edge.to_node) for edge in export.edges}

    assert f"contradiction:{report.id}" in {node.id for node in export.nodes}
    assert ("has_contradiction", f"task:{task.id}", f"contradiction:{report.id}") in edges
    assert ("supported_by", f"contradiction:{report.id}", f"evidence:{evidence.id}") in edges


def test_contradiction_reports_redact_secret_like_values(store: LocalStore) -> None:
    report = ContradictionManager(store).open_report(
        task_id="task_docs",
        facts=["token=redactionfixture123", "fact_new"],
        summary="Authorization: Bearer redactionfixture123",
        affected_artifacts=["README.md"],
        evidence_ids=[],
    )

    assert "redactionfixture" not in report.model_dump_json()


def test_missing_contradiction_raises(store: LocalStore) -> None:
    with pytest.raises(ContradictionNotFoundError, match="unknown contradiction"):
        ContradictionManager(store).get_report("contradiction_missing")
