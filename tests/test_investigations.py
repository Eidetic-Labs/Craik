from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import (
    AgentRole,
    CaseFile,
    EvidenceReference,
    FactValue,
    PolicyEnvelope,
    ProjectProfile,
    RepoProfile,
    RunnerMetadata,
    TaskRequest,
)
from craik.runtime.investigations import (
    FixtureInvestigationSpecialist,
    InvestigationContextError,
    ReadOnlyInvestigationOrchestrator,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy import generate_policy_envelope
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


def test_orchestrator_runs_parallel_read_only_investigations(store: LocalStore) -> None:
    _seed_context(store)
    roles = [_role("role_verifier", "verifier"), _role("role_docs_reviewer", "docs_reviewer")]
    orchestrator = ReadOnlyInvestigationOrchestrator(
        store,
        FixtureInvestigationSpecialist(runner=_runner()),
    )

    batch = orchestrator.run(
        task_id="task_docs",
        case_file_id="case_docs",
        policy=generate_policy_envelope(task_id="task_docs", actor="role:orchestrator"),
        roles=roles,
        questions={
            "role_verifier": "Check test evidence.",
            "role_docs_reviewer": "Check docs evidence.",
        },
    )

    assert [request.role.id for request in batch.requests] == [
        "role_verifier",
        "role_docs_reviewer",
    ]
    assert [result.status for result in batch.results] == ["completed", "completed"]
    assert [receipt.result.status for receipt in batch.receipts] == ["passed", "passed"]
    assert {result.id for result in store.list_worker_results()} == {
        result.id for result in batch.results
    }
    assert {receipt.id for receipt in store.list_receipts()} == {
        receipt.id for receipt in batch.receipts
    }
    verifier = next(result for result in batch.results if result.role_id == "role_verifier")
    assert verifier.findings[0].evidence_ids == [
        "README.md",
        "evidence_readme",
    ]


def test_read_only_investigation_blocks_without_policy_access(store: LocalStore) -> None:
    _seed_context(store)
    policy = PolicyEnvelope(
        id="policy_no_read",
        task_id="task_docs",
        actor="role:orchestrator",
        profile="strict",
        allowed_capabilities=[],
        denied_capabilities=["repo.write", "memory.write"],
    )
    orchestrator = ReadOnlyInvestigationOrchestrator(
        store,
        FixtureInvestigationSpecialist(runner=_runner()),
    )

    batch = orchestrator.run(
        task_id="task_docs",
        case_file_id="case_docs",
        policy=policy,
        roles=[_role("role_verifier", "verifier")],
        questions={},
    )

    assert batch.receipts[0].result.status == "blocked"
    assert batch.results[0].status == "blocked"
    assert batch.results[0].diagnostics == [
        "Read-only investigation requires repo.read or memory.read policy access."
    ]


def test_read_only_investigation_requires_case_file(store: LocalStore) -> None:
    orchestrator = ReadOnlyInvestigationOrchestrator(
        store,
        FixtureInvestigationSpecialist(runner=_runner()),
    )

    with pytest.raises(InvestigationContextError, match="unknown case file"):
        orchestrator.run(
            task_id="task_docs",
            case_file_id="case_missing",
            policy=generate_policy_envelope(task_id="task_docs", actor="role:orchestrator"),
            roles=[_role("role_verifier", "verifier")],
            questions={},
        )


def _seed_context(store: LocalStore) -> None:
    store.put_project(
        ProjectProfile(
            id="project_docs",
            name="Docs",
            repo=RepoProfile(type="git", local_path="/workspace/docs"),
            memory={"backend": "local", "scope": "team"},
        )
    )
    store.put_task(
        TaskRequest(
            id="task_docs",
            title="Review docs",
            objective="Review docs safely.",
            project_id="project_docs",
            requested_by="user:maintainer",
            mode="review",
            created_at=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
        )
    )
    evidence = EvidenceReference(
        id="evidence_readme",
        source="README.md",
        kind="file",
        locator="README.md",
        summary="README evidence.",
    )
    store.put_case_file(
        CaseFile(
            id="case_docs",
            task_id="task_docs",
            objective="Review docs safely.",
            policy_envelope_id="policy_docs",
            facts=[
                FactValue(
                    entity="repo:docs",
                    relation="craik:source",
                    value="README exists.",
                    source="README.md",
                    confidence=0.9,
                    scope="team",
                    trust_class="observed",
                )
            ],
            evidence=[evidence],
            docs=["README.md"],
            verification_plan=["Review read-only evidence."],
        )
    )


def _role(role_id: str, kind: str) -> AgentRole:
    return AgentRole(
        id=role_id,
        kind=kind,
        name=kind.replace("_", " ").title(),
        description="Read-only specialist.",
        runner_id="runner_fixture",
        runner_mode="fixture",
        authority=["review"],
        allowed_capabilities=["repo.read", "memory.read", "receipt.write"],
        denied_capabilities=["repo.write", "memory.write"],
        expected_input_schemas=["craik.case_file"],
        expected_output_schemas=["craik.worker_result"],
    )


def _runner() -> RunnerMetadata:
    return RunnerMetadata(
        id="runner_fixture",
        name="Fixture Runner",
        adapter="fixture",
        adapter_version="0.1.0",
        mode="fixture",
        capabilities=["prompt.read", "result.structured"],
    )
