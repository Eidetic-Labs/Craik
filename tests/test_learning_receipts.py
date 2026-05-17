from datetime import UTC, datetime

from craik.runtime.skills.learning_receipts import LearningReceiptContext, learning_receipt

NOW = datetime(2026, 5, 16, 21, 25, tzinfo=UTC)


def _context() -> LearningReceiptContext:
    return LearningReceiptContext(
        task_id="task_learning",
        policy_envelope_id="policy_learning",
        skill_package_id="skill_docs_reconcile",
        proposal_id="skill_proposal_docs_reconcile",
        telemetry_id="skill_telemetry_docs_failed",
        replay_fixture_id="skill_replay_docs_fixture",
        preference_id="preference_user_pr_titles",
        memory_fact_ref="fact_memory_policy",
        evidence_ids=["evidence_learning"],
        receipt_ids=["receipt_prior"],
    )


def test_learning_receipt_records_passed_proposal_context() -> None:
    receipt = learning_receipt(
        receipt_id="receipt_learning_proposal",
        action="proposal",
        context=_context(),
        actor="agent:codex",
        capability="learning.proposal.create",
        policy_profile="strict",
        status="passed",
        reason="Proposal created for review.",
        summary="Learning proposal recorded.",
        metadata={"risk": "medium"},
        created_at=NOW,
    )

    assert receipt.result.status == "passed"
    assert receipt.target == "proposal:skill_proposal_docs_reconcile"
    assert receipt.result.metadata["learning_action"] == "proposal"
    assert receipt.result.metadata["skill_package_id"] == "skill_docs_reconcile"
    assert receipt.result.metadata["proposal_id"] == "skill_proposal_docs_reconcile"
    assert receipt.result.metadata["telemetry_id"] == "skill_telemetry_docs_failed"
    assert receipt.result.metadata["risk"] == "medium"


def test_learning_receipt_records_denied_promotion_context() -> None:
    receipt = learning_receipt(
        receipt_id="receipt_learning_promotion_denied",
        action="promotion",
        context=_context(),
        actor="agent:codex",
        capability="learning.skill.promote",
        policy_profile="strict",
        status="denied",
        reason="Promotion requires approval gate.",
        summary="Skill promotion denied.",
        created_at=NOW,
    )

    assert receipt.result.status == "denied"
    assert receipt.reason == "Promotion requires approval gate."
    assert receipt.result.metadata["policy_envelope_id"] == "policy_learning"


def test_learning_receipt_redacts_trajectory_and_preference_payloads() -> None:
    receipt = learning_receipt(
        receipt_id="receipt_learning_export",
        action="export",
        context=_context(),
        actor="agent:codex",
        capability="learning.trajectory.export",
        policy_profile="strict",
        status="passed",
        reason="Export generated.",
        summary="Trajectory export prepared.",
        metadata={
            "trajectory": {"prompt": "secret"},
            "raw_trajectory": "raw",
            "preference_evidence": "private",
            "export_payload": {"token": "secret"},
            "api_token": "raw",
            "format": "jsonl",
        },
        created_at=NOW,
    )

    assert receipt.redacted is True
    assert receipt.result.metadata["format"] == "jsonl"
    assert "trajectory" not in receipt.result.metadata
    assert "raw_trajectory" not in receipt.result.metadata
    assert "preference_evidence" not in receipt.result.metadata
    assert "export_payload" not in receipt.result.metadata
    assert "api_token" not in receipt.result.metadata
    assert "trajectory" in receipt.result.metadata["redacted_fields"]
