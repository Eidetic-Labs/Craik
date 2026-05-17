from datetime import UTC, datetime

from craik.contracts.models import (
    CapabilityReceipt,
    EvidenceReference,
    ReceiptResult,
    RunnerMetadata,
    RunnerStepResult,
    TaskRunPhase,
)
from craik.runtime.skills.trajectory_exports import (
    LOCAL_PATH_REDACTION,
    TRAJECTORY_EXPORT_FORMAT,
    build_training_trajectory_export,
    compress_training_trajectory,
)

NOW = datetime(2026, 5, 16, 16, 50, tzinfo=UTC)


def test_training_trajectory_export_records_stable_shape() -> None:
    export = build_training_trajectory_export(
        export_id="trajectory_export_docs_reconcile",
        task_id="task_docs_reconcile",
        steps=[_step()],
        receipts=[_receipt()],
        evidence=[_evidence()],
        outcome="completed",
        created_at=NOW,
    )

    payload = export.model_dump(by_alias=True, mode="json")

    assert payload["schema"] == "craik.training_trajectory_export"
    assert payload["format_version"] == TRAJECTORY_EXPORT_FORMAT
    assert payload["task_id"] == "task_docs_reconcile"
    assert payload["outcome"] == "completed"
    assert payload["receipt_ids"] == ["receipt_runner_fixture"]
    assert payload["evidence_ids"] == ["evidence_docs_reconcile"]
    assert payload["decisions"][0]["step_result_id"] == "runner_step_result_docs_reconcile_plan"
    assert payload["decisions"][0]["evidence_ids"] == ["evidence_docs_reconcile"]


def test_training_trajectory_export_redacts_secrets_private_payloads_and_paths() -> None:
    export = build_training_trajectory_export(
        export_id="trajectory_export_docs_reconcile",
        task_id="task_docs_reconcile",
        steps=[
            _step(
                summary="Used token=redactionfixture123 in local path /Users/bjones/project",
                observed_output={
                    "decision": "retry",
                    "evidence_ids": ["evidence_docs_reconcile"],
                    "private_payload": {"prompt": "do not export"},
                    "path": "/private/tmp/craik-secret/output.json",
                    "api_token": "redaction-fixture-value",
                },
                diagnostics=["wrote /var/folders/96/private.txt"],
                artifacts=["/Users/bjones/Desktop/Craik/private.log"],
            )
        ],
        receipts=[_receipt(metadata={"trace": "private", "status": "passed"})],
        evidence=[_evidence(locator="/Users/bjones/Desktop/Craik/tests/test_secret.py")],
        outcome="completed at /tmp/private-output with Bearer redactionfixture123",
        created_at=NOW,
    )

    payload = export.model_dump(by_alias=True, mode="json")
    decision = payload["decisions"][0]

    assert "redactionfixture123" not in str(payload)
    assert "/Users/bjones" not in str(payload)
    assert "/private/tmp" not in str(payload)
    assert decision["summary"] == f"Used token=[REDACTED] in local path {LOCAL_PATH_REDACTION}"
    assert decision["observed_output"]["private_payload"] == "[REDACTED]"
    assert decision["observed_output"]["api_token"] == "[REDACTED]"
    assert decision["observed_output"]["path"] == LOCAL_PATH_REDACTION
    assert decision["artifacts"] == [LOCAL_PATH_REDACTION]
    assert payload["receipts"][0]["result"]["metadata"]["trace"] == "[REDACTED]"
    assert payload["evidence"][0]["locator"] == LOCAL_PATH_REDACTION
    assert payload["redacted"] is True
    assert payload["redacted_paths"]


def test_compress_training_trajectory_preserves_review_and_replay_links() -> None:
    export = build_training_trajectory_export(
        export_id="trajectory_export_docs_reconcile",
        task_id="task_docs_reconcile",
        steps=[
            _step(
                observed_output={
                    "decision": "plan",
                    "evidence_ids": ["evidence_docs_reconcile"],
                    "policy_envelope_id": "policy_learning",
                    "replay_fixture_ids": ["skill_replay_docs_fixture"],
                    "replay_result_ids": ["skill_replay_docs_fixture_result"],
                    "unresolved_risk_ids": ["risk_docs_regression"],
                },
            ),
            _step(step_id="runner_step_result_docs_reconcile_evaluate", phase="evaluate"),
        ],
        receipts=[_receipt(metadata={"policy_envelope_id": "policy_learning"})],
        evidence=[_evidence()],
        outcome="completed",
        created_at=NOW,
    )

    summary = compress_training_trajectory(
        summary_id="trajectory_summary_docs_reconcile",
        export=export,
        max_summary_lines=1,
        created_at=NOW,
    )
    payload = summary.model_dump(by_alias=True, mode="json")

    assert payload["schema"] == "craik.training_trajectory_summary"
    assert payload["source_export_id"] == "trajectory_export_docs_reconcile"
    assert payload["decision_count"] == 2
    assert payload["phase_counts"] == {"plan": 1, "evaluate": 1}
    assert payload["status_counts"] == {"completed": 2}
    assert payload["summary_lines"] == ["plan:completed: Step completed."]
    assert payload["omitted_decision_ids"] == [
        "trajectory_decision_runner_step_result_docs_reconcile_evaluate"
    ]
    assert payload["receipt_ids"] == ["receipt_runner_fixture"]
    assert payload["evidence_ids"] == ["evidence_docs_reconcile"]
    assert payload["policy_envelope_ids"] == ["policy_learning"]
    assert payload["replay_fixture_ids"] == ["skill_replay_docs_fixture"]
    assert payload["replay_result_ids"] == ["skill_replay_docs_fixture_result"]
    assert payload["unresolved_risk_ids"] == ["risk_docs_regression"]


def test_compress_training_trajectory_keeps_summary_redacted() -> None:
    export = build_training_trajectory_export(
        export_id="trajectory_export_docs_reconcile",
        task_id="task_docs_reconcile",
        steps=[
            _step(
                summary="Used token=redactionfixture123 from /Users/bjones/private",
                observed_output={"evidence_ids": ["evidence_docs_reconcile"]},
            )
        ],
        evidence=[_evidence()],
        outcome="failed at /private/tmp/run with Bearer redactionfixture123",
        created_at=NOW,
    )

    summary = compress_training_trajectory(
        summary_id="trajectory_summary_docs_reconcile",
        export=export,
        created_at=NOW,
    )
    payload = summary.model_dump(by_alias=True, mode="json")

    assert "redactionfixture123" not in str(payload)
    assert "/Users/bjones" not in str(payload)
    assert "/private/tmp" not in str(payload)
    assert payload["summary_lines"] == [
        f"plan:completed: Used token=[REDACTED] from {LOCAL_PATH_REDACTION}"
    ]
    assert payload["outcome"] == f"failed at {LOCAL_PATH_REDACTION} with Bearer [REDACTED]"
    assert payload["redacted_paths"]


def _step(
    *,
    step_id: str = "runner_step_result_docs_reconcile_plan",
    phase: TaskRunPhase = "plan",
    summary: str = "Step completed.",
    observed_output: dict[str, object] | None = None,
    diagnostics: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> RunnerStepResult:
    return RunnerStepResult(
        id=step_id,
        request_id=f"request_{step_id}",
        run_id="run_docs_reconcile",
        task_id="task_docs_reconcile",
        phase=phase,
        runner=RunnerMetadata(
            id="runner_fixture",
            name="Fixture Runner",
            adapter="fixture",
            adapter_version="0.1.0",
            mode="fixture",
            capabilities=["prompt.read", "result.structured"],
            metadata={"contract_test": True},
        ),
        status="completed",
        summary=summary,
        observed_output=observed_output or {
            "decision": "replay fixture",
            "evidence_ids": ["evidence_docs_reconcile"],
        },
        diagnostics=diagnostics or [],
        receipt_ids=["receipt_runner_fixture"],
        artifacts=artifacts or ["case_docs_reconcile"],
        created_at=NOW,
    )


def _receipt(metadata: dict[str, object] | None = None) -> CapabilityReceipt:
    return CapabilityReceipt(
        id="receipt_runner_fixture",
        task_id="task_docs_reconcile",
        actor="agent:codex",
        capability="runner.step",
        target="run_docs_reconcile",
        policy_profile="strict",
        reason="Record trajectory step.",
        result=ReceiptResult(
            status="passed",
            summary="Step completed.",
            metadata=metadata or {},
        ),
        redacted=True,
        created_at=NOW,
    )


def _evidence(locator: str = "tests/test_docs.py") -> EvidenceReference:
    return EvidenceReference(
        id="evidence_docs_reconcile",
        source="repo",
        kind="file",
        locator=locator,
        summary="Docs test coverage.",
        captured_at=NOW,
    )
