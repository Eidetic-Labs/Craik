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
    AdjudicationOutcome,
    Assumption,
    CapabilityGrant,
    CapabilityReceipt,
    CaseFile,
    CompiledPrompt,
    ContradictionReport,
    DebateSummary,
    DebateTurn,
    DistilledInstructionProposal,
    EvidenceReference,
    Handoff,
    HumanDelegationPoint,
    InstructionPromotionReview,
    InstructionProvenance,
    InstructionSource,
    InstructionSourceRegistry,
    InstructionSourceSnapshot,
    IntentLock,
    MemoryDiff,
    MemoryImpactPreview,
    MemoryProposal,
    PolicyEnvelope,
    ProjectProfile,
    PromotedInstructionConstraint,
    ReviewRequest,
    ReviewResult,
    RunOutput,
    ScopeChangeRequest,
    ScopeChangeResult,
    TaskRequest,
    TaskRun,
    WorkerResult,
    WorkGraphEvent,
)
from craik.contracts.registry import CONTRACT_REGISTRY, ContractModel
from craik.runtime.paths import CraikPaths, ensure_craik_home
from craik.runtime.redaction import contains_unredacted_secret

CURRENT_MIGRATION = 1
DATABASE_NAME = "craik.sqlite3"

CONTRACT_KINDS: dict[str, str] = {
    "craik.adjudication_outcome": "adjudication_outcomes",
    "craik.project_profile": "projects",
    "craik.run_output": "run_outputs",
    "craik.task_request": "tasks",
    "craik.task_run": "task_runs",
    "craik.policy_envelope": "policies",
    "craik.capability_grant": "grants",
    "craik.capability_receipt": "receipts",
    "craik.compiled_prompt": "compiled_prompts",
    "craik.case_file": "case_files",
    "craik.contradiction_report": "contradictions",
    "craik.debate_summary": "debate_summaries",
    "craik.debate_turn": "debate_turns",
    "craik.distilled_instruction_proposal": "distilled_instruction_proposals",
    "craik.handoff": "handoffs",
    "craik.human_delegation_point": "human_delegations",
    "craik.instruction_source": "instruction_sources",
    "craik.instruction_promotion_review": "instruction_promotion_reviews",
    "craik.instruction_provenance": "instruction_provenance",
    "craik.instruction_source_registry": "instruction_source_registries",
    "craik.instruction_source_snapshot": "instruction_source_snapshots",
    "craik.intent_lock": "intent_locks",
    "craik.memory_proposal": "proposals",
    "craik.memory_diff": "memory_diffs",
    "craik.memory_impact_preview": "memory_previews",
    "craik.assumption": "assumptions",
    "craik.evidence_reference": "evidence",
    "craik.work_graph_export": "graph_exports",
    "craik.work_graph_event": "graph_events",
    "craik.worker_result": "worker_results",
    "craik.review_request": "review_requests",
    "craik.review_result": "review_results",
    "craik.promoted_instruction_constraint": "promoted_instruction_constraints",
    "craik.scope_change_request": "scope_change_requests",
    "craik.scope_change_result": "scope_change_results",
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

    def put_run_output(self, output: RunOutput) -> None:
        self.put_contract(output)

    def get_run_output(self, output_id: str) -> RunOutput | None:
        contract = self.get_contract("craik.run_output", output_id)
        return _cast_optional(RunOutput, contract)

    def list_run_outputs(self) -> list[RunOutput]:
        return _cast_list(RunOutput, self.list_contracts("craik.run_output"))

    def put_worker_result(self, result: WorkerResult) -> None:
        self.put_contract(result)

    def get_worker_result(self, result_id: str) -> WorkerResult | None:
        contract = self.get_contract("craik.worker_result", result_id)
        return _cast_optional(WorkerResult, contract)

    def list_worker_results(self) -> list[WorkerResult]:
        return _cast_list(WorkerResult, self.list_contracts("craik.worker_result"))

    def put_debate_turn(self, turn: DebateTurn) -> None:
        self.put_contract(turn)

    def get_debate_turn(self, turn_id: str) -> DebateTurn | None:
        contract = self.get_contract("craik.debate_turn", turn_id)
        return _cast_optional(DebateTurn, contract)

    def list_debate_turns(self) -> list[DebateTurn]:
        return _cast_list(DebateTurn, self.list_contracts("craik.debate_turn"))

    def put_debate_summary(self, summary: DebateSummary) -> None:
        self.put_contract(summary)

    def get_debate_summary(self, summary_id: str) -> DebateSummary | None:
        contract = self.get_contract("craik.debate_summary", summary_id)
        return _cast_optional(DebateSummary, contract)

    def list_debate_summaries(self) -> list[DebateSummary]:
        return _cast_list(DebateSummary, self.list_contracts("craik.debate_summary"))

    def put_review_request(self, request: ReviewRequest) -> None:
        self.put_contract(request)

    def get_review_request(self, request_id: str) -> ReviewRequest | None:
        contract = self.get_contract("craik.review_request", request_id)
        return _cast_optional(ReviewRequest, contract)

    def list_review_requests(self) -> list[ReviewRequest]:
        return _cast_list(ReviewRequest, self.list_contracts("craik.review_request"))

    def put_review_result(self, result: ReviewResult) -> None:
        self.put_contract(result)

    def get_review_result(self, result_id: str) -> ReviewResult | None:
        contract = self.get_contract("craik.review_result", result_id)
        return _cast_optional(ReviewResult, contract)

    def list_review_results(self) -> list[ReviewResult]:
        return _cast_list(ReviewResult, self.list_contracts("craik.review_result"))

    def put_adjudication_outcome(self, outcome: AdjudicationOutcome) -> None:
        self.put_contract(outcome)

    def get_adjudication_outcome(self, outcome_id: str) -> AdjudicationOutcome | None:
        contract = self.get_contract("craik.adjudication_outcome", outcome_id)
        return _cast_optional(AdjudicationOutcome, contract)

    def list_adjudication_outcomes(self) -> list[AdjudicationOutcome]:
        return _cast_list(
            AdjudicationOutcome,
            self.list_contracts("craik.adjudication_outcome"),
        )

    def put_human_delegation(self, delegation: HumanDelegationPoint) -> None:
        self.put_contract(delegation)

    def get_human_delegation(self, delegation_id: str) -> HumanDelegationPoint | None:
        contract = self.get_contract("craik.human_delegation_point", delegation_id)
        return _cast_optional(HumanDelegationPoint, contract)

    def list_human_delegations(self) -> list[HumanDelegationPoint]:
        return _cast_list(
            HumanDelegationPoint,
            self.list_contracts("craik.human_delegation_point"),
        )

    def put_scope_change_request(self, request: ScopeChangeRequest) -> None:
        self.put_contract(request)

    def get_scope_change_request(self, request_id: str) -> ScopeChangeRequest | None:
        contract = self.get_contract("craik.scope_change_request", request_id)
        return _cast_optional(ScopeChangeRequest, contract)

    def list_scope_change_requests(self) -> list[ScopeChangeRequest]:
        return _cast_list(
            ScopeChangeRequest,
            self.list_contracts("craik.scope_change_request"),
        )

    def put_scope_change_result(self, result: ScopeChangeResult) -> None:
        self.put_contract(result)

    def get_scope_change_result(self, result_id: str) -> ScopeChangeResult | None:
        contract = self.get_contract("craik.scope_change_result", result_id)
        return _cast_optional(ScopeChangeResult, contract)

    def list_scope_change_results(self) -> list[ScopeChangeResult]:
        return _cast_list(
            ScopeChangeResult,
            self.list_contracts("craik.scope_change_result"),
        )

    def put_instruction_source(self, source: InstructionSource) -> None:
        self.put_contract(source)

    def get_instruction_source(self, source_id: str) -> InstructionSource | None:
        contract = self.get_contract("craik.instruction_source", source_id)
        return _cast_optional(InstructionSource, contract)

    def list_instruction_sources(self) -> list[InstructionSource]:
        return _cast_list(
            InstructionSource,
            self.list_contracts("craik.instruction_source"),
        )

    def put_instruction_source_registry(self, registry: InstructionSourceRegistry) -> None:
        self.put_contract(registry)

    def get_instruction_source_registry(
        self,
        registry_id: str,
    ) -> InstructionSourceRegistry | None:
        contract = self.get_contract("craik.instruction_source_registry", registry_id)
        return _cast_optional(InstructionSourceRegistry, contract)

    def list_instruction_source_registries(self) -> list[InstructionSourceRegistry]:
        return _cast_list(
            InstructionSourceRegistry,
            self.list_contracts("craik.instruction_source_registry"),
        )

    def put_instruction_source_snapshot(self, snapshot: InstructionSourceSnapshot) -> None:
        self.put_contract(snapshot)

    def get_instruction_source_snapshot(
        self,
        snapshot_id: str,
    ) -> InstructionSourceSnapshot | None:
        contract = self.get_contract("craik.instruction_source_snapshot", snapshot_id)
        return _cast_optional(InstructionSourceSnapshot, contract)

    def list_instruction_source_snapshots(self) -> list[InstructionSourceSnapshot]:
        return _cast_list(
            InstructionSourceSnapshot,
            self.list_contracts("craik.instruction_source_snapshot"),
        )

    def put_instruction_provenance(self, provenance: InstructionProvenance) -> None:
        self.put_contract(provenance)

    def get_instruction_provenance(self, provenance_id: str) -> InstructionProvenance | None:
        contract = self.get_contract("craik.instruction_provenance", provenance_id)
        return _cast_optional(InstructionProvenance, contract)

    def list_instruction_provenance(self) -> list[InstructionProvenance]:
        return _cast_list(
            InstructionProvenance,
            self.list_contracts("craik.instruction_provenance"),
        )

    def put_distilled_instruction_proposal(
        self,
        proposal: DistilledInstructionProposal,
    ) -> None:
        self.put_contract(proposal)

    def get_distilled_instruction_proposal(
        self,
        proposal_id: str,
    ) -> DistilledInstructionProposal | None:
        contract = self.get_contract("craik.distilled_instruction_proposal", proposal_id)
        return _cast_optional(DistilledInstructionProposal, contract)

    def list_distilled_instruction_proposals(self) -> list[DistilledInstructionProposal]:
        return _cast_list(
            DistilledInstructionProposal,
            self.list_contracts("craik.distilled_instruction_proposal"),
        )

    def put_instruction_promotion_review(self, review: InstructionPromotionReview) -> None:
        self.put_contract(review)

    def get_instruction_promotion_review(
        self,
        review_id: str,
    ) -> InstructionPromotionReview | None:
        contract = self.get_contract("craik.instruction_promotion_review", review_id)
        return _cast_optional(InstructionPromotionReview, contract)

    def list_instruction_promotion_reviews(self) -> list[InstructionPromotionReview]:
        return _cast_list(
            InstructionPromotionReview,
            self.list_contracts("craik.instruction_promotion_review"),
        )

    def put_promoted_instruction_constraint(
        self,
        constraint: PromotedInstructionConstraint,
    ) -> None:
        self.put_contract(constraint)

    def get_promoted_instruction_constraint(
        self,
        constraint_id: str,
    ) -> PromotedInstructionConstraint | None:
        contract = self.get_contract("craik.promoted_instruction_constraint", constraint_id)
        return _cast_optional(PromotedInstructionConstraint, contract)

    def list_promoted_instruction_constraints(self) -> list[PromotedInstructionConstraint]:
        return _cast_list(
            PromotedInstructionConstraint,
            self.list_contracts("craik.promoted_instruction_constraint"),
        )

    def put_task(self, task: TaskRequest) -> None:
        self.put_contract(task)

    def get_task(self, task_id: str) -> TaskRequest | None:
        return _cast_optional(TaskRequest, self.get_contract("craik.task_request", task_id))

    def list_tasks(self) -> list[TaskRequest]:
        return _cast_list(TaskRequest, self.list_contracts("craik.task_request"))

    def put_task_run(self, run: TaskRun) -> None:
        self.put_contract(run)

    def get_task_run(self, run_id: str) -> TaskRun | None:
        contract = self.get_contract("craik.task_run", run_id)
        return _cast_optional(TaskRun, contract)

    def list_task_runs(self) -> list[TaskRun]:
        return _cast_list(TaskRun, self.list_contracts("craik.task_run"))

    def put_receipt(self, receipt: CapabilityReceipt) -> None:
        self.put_contract(receipt)

    def get_receipt(self, receipt_id: str) -> CapabilityReceipt | None:
        contract = self.get_contract("craik.capability_receipt", receipt_id)
        return _cast_optional(CapabilityReceipt, contract)

    def list_receipts(self) -> list[CapabilityReceipt]:
        return _cast_list(CapabilityReceipt, self.list_contracts("craik.capability_receipt"))

    def put_policy_envelope(self, policy: PolicyEnvelope) -> None:
        self.put_contract(policy)

    def get_policy_envelope(self, policy_id: str) -> PolicyEnvelope | None:
        contract = self.get_contract("craik.policy_envelope", policy_id)
        return _cast_optional(PolicyEnvelope, contract)

    def list_policy_envelopes(self) -> list[PolicyEnvelope]:
        return _cast_list(PolicyEnvelope, self.list_contracts("craik.policy_envelope"))

    def put_capability_grant(self, grant: CapabilityGrant) -> None:
        self.put_contract(grant)

    def get_capability_grant(self, grant_id: str) -> CapabilityGrant | None:
        contract = self.get_contract("craik.capability_grant", grant_id)
        return _cast_optional(CapabilityGrant, contract)

    def list_capability_grants(self) -> list[CapabilityGrant]:
        return _cast_list(CapabilityGrant, self.list_contracts("craik.capability_grant"))

    def put_case_file(self, case_file: CaseFile) -> None:
        self.put_contract(case_file)

    def get_case_file(self, case_file_id: str) -> CaseFile | None:
        contract = self.get_contract("craik.case_file", case_file_id)
        return _cast_optional(CaseFile, contract)

    def list_case_files(self) -> list[CaseFile]:
        return _cast_list(CaseFile, self.list_contracts("craik.case_file"))

    def put_compiled_prompt(self, prompt: CompiledPrompt) -> None:
        self.put_contract(prompt)

    def get_compiled_prompt(self, prompt_id: str) -> CompiledPrompt | None:
        contract = self.get_contract("craik.compiled_prompt", prompt_id)
        return _cast_optional(CompiledPrompt, contract)

    def list_compiled_prompts(self) -> list[CompiledPrompt]:
        return _cast_list(CompiledPrompt, self.list_contracts("craik.compiled_prompt"))

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

    def put_memory_diff(self, diff: MemoryDiff) -> None:
        self.put_contract(diff)

    def get_memory_diff(self, diff_id: str) -> MemoryDiff | None:
        contract = self.get_contract("craik.memory_diff", diff_id)
        return _cast_optional(MemoryDiff, contract)

    def list_memory_diffs(self) -> list[MemoryDiff]:
        return _cast_list(MemoryDiff, self.list_contracts("craik.memory_diff"))

    def put_memory_impact_preview(self, preview: MemoryImpactPreview) -> None:
        self.put_contract(preview)

    def get_memory_impact_preview(self, preview_id: str) -> MemoryImpactPreview | None:
        contract = self.get_contract("craik.memory_impact_preview", preview_id)
        return _cast_optional(MemoryImpactPreview, contract)

    def list_memory_impact_previews(self) -> list[MemoryImpactPreview]:
        return _cast_list(
            MemoryImpactPreview,
            self.list_contracts("craik.memory_impact_preview"),
        )

    def put_contradiction(self, contradiction: ContradictionReport) -> None:
        self.put_contract(contradiction)

    def get_contradiction(self, contradiction_id: str) -> ContradictionReport | None:
        contract = self.get_contract("craik.contradiction_report", contradiction_id)
        return _cast_optional(ContradictionReport, contract)

    def list_contradictions(self) -> list[ContradictionReport]:
        return _cast_list(ContradictionReport, self.list_contracts("craik.contradiction_report"))

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
