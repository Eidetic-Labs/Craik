import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from craik.contracts.models import (
    AdjudicationOutcome,
    Assumption,
    CapabilityReceipt,
    CaseFile,
    ContextDebtRecord,
    ContradictionReport,
    DebateSummary,
    DebateTurn,
    DistilledInstructionProposal,
    EvidenceCoverageScore,
    EvidenceReference,
    Handoff,
    HandoffQualityScore,
    HumanDelegationPoint,
    InstructionPromotionReview,
    InstructionProvenance,
    InstructionSource,
    InstructionSourceRegistry,
    InstructionSourceSnapshot,
    IntentLock,
    KnowledgeFreshnessProbe,
    KnownTrap,
    MemoryProposal,
    NegativeKnowledge,
    ProjectProfile,
    PromotedInstructionConstraint,
    RecoverySession,
    RedTeamFinding,
    ReviewRequest,
    ReviewResult,
    RunDelta,
    RunOutput,
    RuntimeCriticFinding,
    ScopeChangeRequest,
    ScopeChangeResult,
    TaskRequest,
    TaskRun,
    ToolResultAttestation,
    WorkerResult,
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
    task_run = TaskRun.model_validate(fixtures["craik.task_run"])
    run_output = RunOutput.model_validate(fixtures["craik.run_output"])
    receipt = CapabilityReceipt.model_validate(fixtures["craik.capability_receipt"])
    case_file = CaseFile.model_validate(fixtures["craik.case_file"])
    handoff = Handoff.model_validate(fixtures["craik.handoff"])
    intent_lock = IntentLock.model_validate(fixtures["craik.intent_lock"])
    attestation = ToolResultAttestation.model_validate(
        fixtures["craik.tool_result_attestation"]
    )
    freshness_probe = KnowledgeFreshnessProbe.model_validate(
        fixtures["craik.knowledge_freshness_probe"]
    )
    known_trap = KnownTrap.model_validate(fixtures["craik.known_trap"])
    negative_knowledge = NegativeKnowledge.model_validate(fixtures["craik.negative_knowledge"])
    proposal = MemoryProposal.model_validate(fixtures["craik.memory_proposal"])
    contradiction = ContradictionReport.model_validate(fixtures["craik.contradiction_report"])
    context_debt = ContextDebtRecord.model_validate(fixtures["craik.context_debt_record"])
    assumption = Assumption.model_validate(fixtures["craik.assumption"])
    evidence = EvidenceReference.model_validate(fixtures["craik.evidence_reference"])
    handoff_quality_score = HandoffQualityScore.model_validate(
        fixtures["craik.handoff_quality_score"]
    )
    evidence_coverage_score = EvidenceCoverageScore.model_validate(
        fixtures["craik.evidence_coverage_score"]
    )
    event = WorkGraphEvent.model_validate(fixtures["craik.work_graph_event"])
    export = WorkGraphExport.model_validate(fixtures["craik.work_graph_export"])
    worker_result = WorkerResult.model_validate(fixtures["craik.worker_result"])
    debate_turn = DebateTurn.model_validate(fixtures["craik.debate_turn"])
    debate_summary = DebateSummary.model_validate(fixtures["craik.debate_summary"])
    review_request = ReviewRequest.model_validate(fixtures["craik.review_request"])
    review_result = ReviewResult.model_validate(fixtures["craik.review_result"])
    adjudication = AdjudicationOutcome.model_validate(
        fixtures["craik.adjudication_outcome"]
    )
    delegation = HumanDelegationPoint.model_validate(
        fixtures["craik.human_delegation_point"]
    )
    scope_request = ScopeChangeRequest.model_validate(fixtures["craik.scope_change_request"])
    scope_result = ScopeChangeResult.model_validate(fixtures["craik.scope_change_result"])
    instruction_source = InstructionSource.model_validate(
        fixtures["craik.instruction_source"]
    )
    instruction_registry = InstructionSourceRegistry.model_validate(
        fixtures["craik.instruction_source_registry"]
    )
    instruction_snapshot = InstructionSourceSnapshot.model_validate(
        fixtures["craik.instruction_source_snapshot"]
    )
    instruction_provenance = InstructionProvenance.model_validate(
        fixtures["craik.instruction_provenance"]
    )
    distilled_instruction = DistilledInstructionProposal.model_validate(
        fixtures["craik.distilled_instruction_proposal"]
    )
    promotion_review = InstructionPromotionReview.model_validate(
        fixtures["craik.instruction_promotion_review"]
    )
    promoted_constraint = PromotedInstructionConstraint.model_validate(
        fixtures["craik.promoted_instruction_constraint"]
    )
    run_delta = RunDelta.model_validate(fixtures["craik.run_delta"])
    recovery_session = RecoverySession.model_validate(fixtures["craik.recovery_session"])
    critic_finding = RuntimeCriticFinding.model_validate(
        fixtures["craik.runtime_critic_finding"]
    )
    red_team_finding = RedTeamFinding.model_validate(fixtures["craik.red_team_finding"])

    store.put_task(task)
    store.put_task_run(task_run)
    store.put_run_output(run_output)
    store.put_receipt(receipt)
    store.put_case_file(case_file)
    store.put_handoff(handoff)
    store.put_intent_lock(intent_lock)
    store.put_tool_result_attestation(attestation)
    store.put_knowledge_freshness_probe(freshness_probe)
    store.put_known_trap(known_trap)
    store.put_negative_knowledge(negative_knowledge)
    store.put_proposal(proposal)
    store.put_contradiction(contradiction)
    store.put_context_debt_record(context_debt)
    store.put_assumption(assumption)
    store.put_evidence(evidence)
    store.put_handoff_quality_score(handoff_quality_score)
    store.put_evidence_coverage_score(evidence_coverage_score)
    store.put_graph_event(event)
    store.put_contract(export)
    store.put_worker_result(worker_result)
    store.put_debate_turn(debate_turn)
    store.put_debate_summary(debate_summary)
    store.put_review_request(review_request)
    store.put_review_result(review_result)
    store.put_adjudication_outcome(adjudication)
    store.put_human_delegation(delegation)
    store.put_scope_change_request(scope_request)
    store.put_scope_change_result(scope_result)
    store.put_instruction_source(instruction_source)
    store.put_instruction_source_registry(instruction_registry)
    store.put_instruction_source_snapshot(instruction_snapshot)
    store.put_instruction_provenance(instruction_provenance)
    store.put_distilled_instruction_proposal(distilled_instruction)
    store.put_instruction_promotion_review(promotion_review)
    store.put_promoted_instruction_constraint(promoted_constraint)
    store.put_run_delta(run_delta)
    store.put_recovery_session(recovery_session)
    store.put_runtime_critic_finding(critic_finding)
    store.put_red_team_finding(red_team_finding)

    assert store.get_task(task.id) == task
    assert store.get_task_run(task_run.id) == task_run
    assert store.get_run_output(run_output.id) == run_output
    assert store.list_tasks() == [task]
    assert store.list_task_runs() == [task_run]
    assert store.list_run_outputs() == [run_output]
    assert store.get_receipt(receipt.id) == receipt
    assert store.get_case_file(case_file.id) == case_file
    assert store.get_handoff(handoff.id) == handoff
    assert store.get_intent_lock(intent_lock.id) == intent_lock
    assert store.get_tool_result_attestation(attestation.id) == attestation
    assert store.get_knowledge_freshness_probe(freshness_probe.id) == freshness_probe
    assert store.get_known_trap(known_trap.id) == known_trap
    assert store.get_negative_knowledge(negative_knowledge.id) == negative_knowledge
    assert store.get_proposal(proposal.id) == proposal
    assert store.get_contradiction(contradiction.id) == contradiction
    assert store.get_context_debt_record(context_debt.id) == context_debt
    assert store.get_assumption(assumption.id) == assumption
    assert store.get_evidence(evidence.id) == evidence
    assert store.get_handoff_quality_score(handoff_quality_score.id) == handoff_quality_score
    assert (
        store.get_evidence_coverage_score(evidence_coverage_score.id)
        == evidence_coverage_score
    )
    assert store.get_graph_event(event.id) == event
    assert store.get_contract("craik.work_graph_export", export.id) == export
    assert store.get_worker_result(worker_result.id) == worker_result
    assert store.get_debate_turn(debate_turn.id) == debate_turn
    assert store.get_debate_summary(debate_summary.id) == debate_summary
    assert store.get_review_request(review_request.id) == review_request
    assert store.get_review_result(review_result.id) == review_result
    assert store.get_adjudication_outcome(adjudication.id) == adjudication
    assert store.get_human_delegation(delegation.id) == delegation
    assert store.get_scope_change_request(scope_request.id) == scope_request
    assert store.get_scope_change_result(scope_result.id) == scope_result
    assert store.get_instruction_source(instruction_source.id) == instruction_source
    assert store.get_instruction_source_registry(instruction_registry.id) == instruction_registry
    assert store.get_instruction_source_snapshot(instruction_snapshot.id) == instruction_snapshot
    assert store.get_instruction_provenance(instruction_provenance.id) == instruction_provenance
    assert (
        store.get_distilled_instruction_proposal(distilled_instruction.id)
        == distilled_instruction
    )
    assert store.get_instruction_promotion_review(promotion_review.id) == promotion_review
    assert (
        store.get_promoted_instruction_constraint(promoted_constraint.id)
        == promoted_constraint
    )
    assert store.get_run_delta(run_delta.id) == run_delta
    assert store.get_recovery_session(recovery_session.id) == recovery_session
    assert store.get_runtime_critic_finding(critic_finding.id) == critic_finding
    assert store.get_red_team_finding(red_team_finding.id) == red_team_finding
    assert store.list_receipts() == [receipt]
    assert store.list_case_files() == [case_file]
    assert store.list_handoffs() == [handoff]
    assert store.list_intent_locks() == [intent_lock]
    assert store.list_tool_result_attestations() == [attestation]
    assert store.list_knowledge_freshness_probes() == [freshness_probe]
    assert store.list_known_traps() == [known_trap]
    assert store.list_negative_knowledge() == [negative_knowledge]
    assert store.list_proposals() == [proposal]
    assert store.list_contradictions() == [contradiction]
    assert store.list_context_debt_records() == [context_debt]
    assert store.list_assumptions() == [assumption]
    assert store.list_evidence() == [evidence]
    assert store.list_handoff_quality_scores() == [handoff_quality_score]
    assert store.list_evidence_coverage_scores() == [evidence_coverage_score]
    assert store.list_graph_events() == [event]
    assert store.list_worker_results() == [worker_result]
    assert store.list_debate_turns() == [debate_turn]
    assert store.list_debate_summaries() == [debate_summary]
    assert store.list_review_requests() == [review_request]
    assert store.list_review_results() == [review_result]
    assert store.list_adjudication_outcomes() == [adjudication]
    assert store.list_human_delegations() == [delegation]
    assert store.list_scope_change_requests() == [scope_request]
    assert store.list_scope_change_results() == [scope_result]
    assert store.list_instruction_sources() == [instruction_source]
    assert store.list_instruction_source_registries() == [instruction_registry]
    assert store.list_instruction_source_snapshots() == [instruction_snapshot]
    assert store.list_instruction_provenance() == [instruction_provenance]
    assert store.list_distilled_instruction_proposals() == [distilled_instruction]
    assert store.list_instruction_promotion_reviews() == [promotion_review]
    assert store.list_promoted_instruction_constraints() == [promoted_constraint]
    assert store.list_run_deltas() == [run_delta]
    assert store.list_recovery_sessions() == [recovery_session]
    assert store.list_runtime_critic_findings() == [critic_finding]
    assert store.list_red_team_findings() == [red_team_finding]


def test_persists_supported_contract_types(
    store: LocalStore,
    fixtures: dict[str, dict[str, Any]],
) -> None:
    for schema_name in (
        "craik.project_profile",
        "craik.run_output",
        "craik.task_request",
        "craik.task_run",
        "craik.capability_receipt",
        "craik.case_file",
        "craik.contradiction_report",
        "craik.context_debt_record",
        "craik.debate_summary",
        "craik.debate_turn",
        "craik.distilled_instruction_proposal",
        "craik.evidence_coverage_score",
        "craik.instruction_promotion_review",
        "craik.handoff_quality_score",
        "craik.promoted_instruction_constraint",
        "craik.red_team_finding",
        "craik.recovery_session",
        "craik.review_request",
        "craik.review_result",
        "craik.run_delta",
        "craik.runtime_critic_finding",
        "craik.adjudication_outcome",
        "craik.human_delegation_point",
        "craik.instruction_source",
        "craik.instruction_provenance",
        "craik.instruction_source_registry",
        "craik.instruction_source_snapshot",
        "craik.scope_change_request",
        "craik.scope_change_result",
        "craik.handoff",
        "craik.intent_lock",
        "craik.knowledge_freshness_probe",
        "craik.known_trap",
        "craik.memory_proposal",
        "craik.negative_knowledge",
        "craik.assumption",
        "craik.evidence_reference",
        "craik.work_graph_export",
        "craik.work_graph_event",
        "craik.worker_result",
        "craik.tool_result_attestation",
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
