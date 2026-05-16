import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from craik.contracts.models import (
    Assumption,
    CapabilityReceipt,
    CaseFile,
    ContradictionReport,
    EvidenceReference,
    Handoff,
    IntentLock,
    MemoryProposal,
    ProjectProfile,
    TaskRequest,
    WorkGraphEvent,
    WorkGraphExport,
)
from craik.contracts.registry import CONTRACT_REGISTRY
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import (
    CURRENT_MIGRATION,
    DATABASE_NAME,
    LocalStore,
    LocalStoreCorruptError,
    UnredactedSecretError,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"
INSERT_RECORD_SQL = """
INSERT INTO records(kind, id, schema, version, payload_json, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text())


@pytest.fixture
def store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_initialize_creates_database_and_migration(tmp_path: Path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)

    local_store.initialize()

    assert (paths.state / DATABASE_NAME).is_file()
    assert local_store.migration_version() == CURRENT_MIGRATION
    local_store.close()


def test_persists_project_profile(store: LocalStore, fixtures: dict[str, dict[str, Any]]) -> None:
    project = ProjectProfile.model_validate(fixtures["craik.project_profile"])

    store.put_project(project)

    assert store.get_project(project.id) == project
    assert store.list_projects() == [project]


def test_typed_store_helpers_round_trip_all_supported_contracts(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    task = TaskRequest.model_validate(fixtures["craik.task_request"])
    receipt = CapabilityReceipt.model_validate(fixtures["craik.capability_receipt"])
    case_file = CaseFile.model_validate(fixtures["craik.case_file"])
    handoff = Handoff.model_validate(fixtures["craik.handoff"])
    intent_lock = IntentLock.model_validate(fixtures["craik.intent_lock"])
    proposal = MemoryProposal.model_validate(fixtures["craik.memory_proposal"])
    contradiction = ContradictionReport.model_validate(fixtures["craik.contradiction_report"])
    assumption = Assumption.model_validate(fixtures["craik.assumption"])
    evidence = EvidenceReference.model_validate(fixtures["craik.evidence_reference"])
    event = WorkGraphEvent.model_validate(fixtures["craik.work_graph_event"])
    export = WorkGraphExport.model_validate(fixtures["craik.work_graph_export"])

    store.put_task(task)
    store.put_receipt(receipt)
    store.put_case_file(case_file)
    store.put_handoff(handoff)
    store.put_intent_lock(intent_lock)
    store.put_proposal(proposal)
    store.put_contradiction(contradiction)
    store.put_assumption(assumption)
    store.put_evidence(evidence)
    store.put_graph_event(event)
    store.put_contract(export)

    assert store.get_task(task.id) == task
    assert store.list_tasks() == [task]
    assert store.get_receipt(receipt.id) == receipt
    assert store.get_case_file(case_file.id) == case_file
    assert store.get_handoff(handoff.id) == handoff
    assert store.get_intent_lock(intent_lock.id) == intent_lock
    assert store.get_proposal(proposal.id) == proposal
    assert store.get_contradiction(contradiction.id) == contradiction
    assert store.get_assumption(assumption.id) == assumption
    assert store.get_evidence(evidence.id) == evidence
    assert store.get_graph_event(event.id) == event
    assert store.get_contract("craik.work_graph_export", export.id) == export
    assert store.list_receipts() == [receipt]
    assert store.list_case_files() == [case_file]
    assert store.list_handoffs() == [handoff]
    assert store.list_intent_locks() == [intent_lock]
    assert store.list_proposals() == [proposal]
    assert store.list_contradictions() == [contradiction]
    assert store.list_assumptions() == [assumption]
    assert store.list_evidence() == [evidence]
    assert store.list_graph_events() == [event]


def test_persists_supported_contract_types(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    for schema_name in (
        "craik.project_profile",
        "craik.task_request",
        "craik.capability_receipt",
        "craik.case_file",
        "craik.contradiction_report",
        "craik.handoff",
        "craik.intent_lock",
        "craik.memory_proposal",
        "craik.assumption",
        "craik.evidence_reference",
        "craik.work_graph_export",
        "craik.work_graph_event",
    ):
        model = CONTRACT_REGISTRY[schema_name]
        contract = model.model_validate(fixtures[schema_name])
        store.put_contract(contract)

        assert store.get_contract(schema_name, contract.model_dump()["id"]) == contract


def test_upsert_replaces_existing_payload(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    task = TaskRequest.model_validate(fixtures["craik.task_request"])
    updated = task.model_copy(update={"title": "Updated title"})

    store.put_task(task)
    store.put_task(updated)

    assert store.get_task(task.id) == updated


def test_transaction_rolls_back_on_error(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    event = WorkGraphEvent.model_validate(fixtures["craik.work_graph_event"])
    params = (
        "graph_events",
        event.id,
        event.schema_,
        event.version,
        event.model_dump_json(by_alias=True),
        "now",
        "now",
    )

    with pytest.raises(LocalStoreCorruptError):
        with store.transaction() as connection:
            connection.execute(INSERT_RECORD_SQL, params)
            connection.execute(INSERT_RECORD_SQL, params)

    assert store.list_contracts("craik.work_graph_event") == []


def test_missing_contract_returns_none(store: LocalStore) -> None:
    assert store.get_project("project_missing") is None


def test_corrupt_database_raises_clear_error(tmp_path: Path) -> None:
    database_path = tmp_path / "bad.sqlite3"
    database_path.write_text("not sqlite")
    local_store = LocalStore(database_path)

    with pytest.raises(LocalStoreCorruptError):
        local_store.initialize()

    local_store.close()


def test_newer_migration_raises_clear_error(tmp_path: Path) -> None:
    database_path = tmp_path / "future.sqlite3"
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA user_version = 999")
    connection.close()
    local_store = LocalStore(database_path)

    with pytest.raises(LocalStoreCorruptError):
        local_store.initialize()

    local_store.close()


def test_unredacted_secret_payload_is_rejected(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    payload = dict(fixtures["craik.capability_receipt"])
    payload["result"] = {
        "status": "passed",
        "summary": "Secret scan fixture.",
        "metadata": {"api_token": "redaction-fixture-value"},
    }
    receipt = CapabilityReceipt.model_validate(payload)

    with pytest.raises(UnredactedSecretError, match="unredacted secret material"):
        store.put_receipt(receipt)


def test_redacted_secret_payload_is_allowed(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    payload = dict(fixtures["craik.capability_receipt"])
    payload["result"] = {
        "status": "passed",
        "summary": "Secret scan fixture.",
        "metadata": {"api_token": "[REDACTED]"},
    }
    receipt = CapabilityReceipt.model_validate(payload)

    store.put_receipt(receipt)

    assert store.get_contract("craik.capability_receipt", receipt.id) == receipt
