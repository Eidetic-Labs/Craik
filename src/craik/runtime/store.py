"""SQLite-backed local runtime store."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from craik.contracts.models import (
    Assumption,
    CapabilityReceipt,
    CaseFile,
    EvidenceReference,
    Handoff,
    IntentLock,
    MemoryProposal,
    ProjectProfile,
    TaskRequest,
    WorkGraphEvent,
)
from craik.contracts.registry import CONTRACT_REGISTRY, ContractModel
from craik.runtime.paths import CraikPaths, ensure_craik_home
from craik.runtime.redaction import contains_unredacted_secret

CURRENT_MIGRATION = 1
DATABASE_NAME = "craik.sqlite3"

CONTRACT_KINDS: dict[str, str] = {
    "craik.project_profile": "projects",
    "craik.task_request": "tasks",
    "craik.capability_receipt": "receipts",
    "craik.case_file": "case_files",
    "craik.handoff": "handoffs",
    "craik.intent_lock": "intent_locks",
    "craik.memory_proposal": "proposals",
    "craik.assumption": "assumptions",
    "craik.evidence_reference": "evidence",
    "craik.work_graph_event": "graph_events",
}

class LocalStoreError(RuntimeError):
    """Base error for local store failures."""


class LocalStoreCorruptError(LocalStoreError):
    """Raised when the SQLite database cannot be read as a Craik store."""


class UnredactedSecretError(LocalStoreError):
    """Raised when a payload appears to contain unredacted secret material."""


class UnknownContractError(LocalStoreError):
    """Raised when a contract is not part of the local store schema."""


class LocalStore:
    """SQLite persistence for v0.1 runtime state."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def from_paths(cls, paths: CraikPaths) -> LocalStore:
        """Open the default local store under a resolved Craik home."""
        return cls(paths.state / DATABASE_NAME)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> LocalStore:
        """Ensure Craik home exists and open its default local store."""
        return cls.from_paths(ensure_craik_home(env))

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self._connection.close()

    def initialize(self) -> None:
        """Apply local store migrations."""
        try:
            with self.transaction() as connection:
                _apply_migrations(connection)
        except sqlite3.DatabaseError as error:
            raise LocalStoreCorruptError(f"cannot initialize local store: {error}") from error

    def migration_version(self) -> int:
        """Return the current local store migration version."""
        try:
            row = self._connection.execute("PRAGMA user_version").fetchone()
            return int(row[0])
        except sqlite3.DatabaseError as error:
            message = f"cannot read local store migration version: {error}"
            raise LocalStoreCorruptError(message) from error

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Run statements in a commit-or-rollback transaction."""
        try:
            with self._connection:
                yield self._connection
        except sqlite3.DatabaseError as error:
            raise LocalStoreCorruptError(f"local store transaction failed: {error}") from error

    def put_contract(self, contract: BaseModel) -> None:
        """Persist a supported contract payload after validation."""
        payload = contract.model_dump(mode="json", by_alias=True)
        schema_name = str(payload.get("schema"))
        kind = _kind_for_schema(schema_name)
        model = CONTRACT_REGISTRY[schema_name]
        validated = model.model_validate(payload)
        payload = validated.model_dump(mode="json", by_alias=True)
        _reject_unredacted_secrets(payload)
        now = _utc_now()

        try:
            with self.transaction() as connection:
                connection.execute(
                    """
                    INSERT INTO records (
                      kind, id, schema, version, payload_json, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(kind, id) DO UPDATE SET
                      schema = excluded.schema,
                      version = excluded.version,
                      payload_json = excluded.payload_json,
                      updated_at = excluded.updated_at
                    """,
                    (
                        kind,
                        payload["id"],
                        payload["schema"],
                        payload["version"],
                        json.dumps(payload, sort_keys=True, separators=(",", ":")),
                        now,
                        now,
                    ),
                )
        except sqlite3.DatabaseError as error:
            message = f"cannot persist contract {schema_name}: {error}"
            raise LocalStoreCorruptError(message) from error

    def get_contract(self, schema_name: str, contract_id: str) -> BaseModel | None:
        """Load and validate a contract by schema and id."""
        kind = _kind_for_schema(schema_name)
        model = CONTRACT_REGISTRY[schema_name]
        try:
            row = self._connection.execute(
                "SELECT payload_json FROM records WHERE kind = ? AND id = ?",
                (kind, contract_id),
            ).fetchone()
        except sqlite3.DatabaseError as error:
            raise LocalStoreCorruptError(f"cannot read contract {schema_name}: {error}") from error
        if row is None:
            return None
        return _parse_payload(model, str(row["payload_json"]))

    def list_contracts(self, schema_name: str) -> list[BaseModel]:
        """Load all contracts for a schema in stable id order."""
        kind = _kind_for_schema(schema_name)
        model = CONTRACT_REGISTRY[schema_name]
        try:
            rows = self._connection.execute(
                "SELECT payload_json FROM records WHERE kind = ? ORDER BY id",
                (kind,),
            ).fetchall()
        except sqlite3.DatabaseError as error:
            raise LocalStoreCorruptError(f"cannot list contracts {schema_name}: {error}") from error
        return [_parse_payload(model, str(row["payload_json"])) for row in rows]

    def put_project(self, project: ProjectProfile) -> None:
        self.put_contract(project)

    def get_project(self, project_id: str) -> ProjectProfile | None:
        contract = self.get_contract("craik.project_profile", project_id)
        return _cast_optional(ProjectProfile, contract)

    def list_projects(self) -> list[ProjectProfile]:
        return _cast_list(ProjectProfile, self.list_contracts("craik.project_profile"))

    def put_task(self, task: TaskRequest) -> None:
        self.put_contract(task)

    def get_task(self, task_id: str) -> TaskRequest | None:
        return _cast_optional(TaskRequest, self.get_contract("craik.task_request", task_id))

    def put_receipt(self, receipt: CapabilityReceipt) -> None:
        self.put_contract(receipt)

    def get_receipt(self, receipt_id: str) -> CapabilityReceipt | None:
        contract = self.get_contract("craik.capability_receipt", receipt_id)
        return _cast_optional(CapabilityReceipt, contract)

    def list_receipts(self) -> list[CapabilityReceipt]:
        return _cast_list(CapabilityReceipt, self.list_contracts("craik.capability_receipt"))

    def put_case_file(self, case_file: CaseFile) -> None:
        self.put_contract(case_file)

    def get_case_file(self, case_file_id: str) -> CaseFile | None:
        contract = self.get_contract("craik.case_file", case_file_id)
        return _cast_optional(CaseFile, contract)

    def list_case_files(self) -> list[CaseFile]:
        return _cast_list(CaseFile, self.list_contracts("craik.case_file"))

    def put_intent_lock(self, intent_lock: IntentLock) -> None:
        self.put_contract(intent_lock)

    def get_intent_lock(self, intent_lock_id: str) -> IntentLock | None:
        contract = self.get_contract("craik.intent_lock", intent_lock_id)
        return _cast_optional(IntentLock, contract)

    def list_intent_locks(self) -> list[IntentLock]:
        return _cast_list(IntentLock, self.list_contracts("craik.intent_lock"))

    def put_handoff(self, handoff: Handoff) -> None:
        self.put_contract(handoff)

    def get_handoff(self, handoff_id: str) -> Handoff | None:
        contract = self.get_contract("craik.handoff", handoff_id)
        return _cast_optional(Handoff, contract)

    def list_handoffs(self) -> list[Handoff]:
        return _cast_list(Handoff, self.list_contracts("craik.handoff"))

    def put_proposal(self, proposal: MemoryProposal) -> None:
        self.put_contract(proposal)

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        contract = self.get_contract("craik.memory_proposal", proposal_id)
        return _cast_optional(MemoryProposal, contract)

    def list_proposals(self) -> list[MemoryProposal]:
        return _cast_list(MemoryProposal, self.list_contracts("craik.memory_proposal"))

    def put_assumption(self, assumption: Assumption) -> None:
        self.put_contract(assumption)

    def get_assumption(self, assumption_id: str) -> Assumption | None:
        contract = self.get_contract("craik.assumption", assumption_id)
        return _cast_optional(Assumption, contract)

    def list_assumptions(self) -> list[Assumption]:
        return _cast_list(Assumption, self.list_contracts("craik.assumption"))

    def put_evidence(self, evidence: EvidenceReference) -> None:
        self.put_contract(evidence)

    def get_evidence(self, evidence_id: str) -> EvidenceReference | None:
        contract = self.get_contract("craik.evidence_reference", evidence_id)
        return _cast_optional(EvidenceReference, contract)

    def list_evidence(self) -> list[EvidenceReference]:
        return _cast_list(EvidenceReference, self.list_contracts("craik.evidence_reference"))

    def put_graph_event(self, event: WorkGraphEvent) -> None:
        self.put_contract(event)

    def get_graph_event(self, event_id: str) -> WorkGraphEvent | None:
        contract = self.get_contract("craik.work_graph_event", event_id)
        return _cast_optional(WorkGraphEvent, contract)

    def list_graph_events(self) -> list[WorkGraphEvent]:
        return _cast_list(WorkGraphEvent, self.list_contracts("craik.work_graph_event"))


def _apply_migrations(connection: sqlite3.Connection) -> None:
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current > CURRENT_MIGRATION:
        raise LocalStoreCorruptError(
            f"local store migration {current} is newer than supported {CURRENT_MIGRATION}"
        )
    if current < 1:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS records (
              kind TEXT NOT NULL,
              id TEXT NOT NULL,
              schema TEXT NOT NULL,
              version TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (kind, id)
            );
            CREATE INDEX IF NOT EXISTS idx_records_schema ON records(schema);
            CREATE TABLE IF NOT EXISTS migrations (
              version INTEGER PRIMARY KEY,
              applied_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO migrations(version, applied_at) VALUES (?, ?)",
            (1, _utc_now()),
        )
        connection.execute("PRAGMA user_version = 1")


def _parse_payload(model: ContractModel, payload_json: str) -> BaseModel:
    try:
        return model.model_validate_json(payload_json)
    except ValidationError as error:
        raise LocalStoreCorruptError(f"stored payload failed validation: {error}") from error


def _kind_for_schema(schema_name: str) -> str:
    try:
        return CONTRACT_KINDS[schema_name]
    except KeyError:
        message = f"unsupported local store contract schema: {schema_name}"
        raise UnknownContractError(message) from None


def _reject_unredacted_secrets(value: Any) -> None:
    if contains_unredacted_secret(value):
        raise UnredactedSecretError("refusing to persist unredacted secret material")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _cast_optional[T: BaseModel](model: type[T], value: BaseModel | None) -> T | None:
    if value is None:
        return None
    if not isinstance(value, model):
        raise TypeError(f"expected {model.__name__}, got {type(value).__name__}")
    return value


def _cast_list[T: BaseModel](model: type[T], values: list[BaseModel]) -> list[T]:
    return [_cast_required(model, value) for value in values]


def _cast_required[T: BaseModel](model: type[T], value: BaseModel) -> T:
    if not isinstance(value, model):
        raise TypeError(f"expected {model.__name__}, got {type(value).__name__}")
    return value
