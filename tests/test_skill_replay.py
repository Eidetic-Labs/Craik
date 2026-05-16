from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skill_replay import (
    SkillReplayFixture,
    SkillReplayObservation,
    replay_skill_fixture,
)

NOW = datetime(2026, 5, 16, 21, 10, tzinfo=UTC)


def _fixture(**overrides: object) -> SkillReplayFixture:
    payload = {
        "id": "skill_replay_docs_fixture",
        "skill_package_id": "skill_docs_reconcile",
        "name": "Docs reconciliation emits worker result",
        "input_refs": ["case_docs_reconcile"],
        "expected_outcome": "succeeded",
        "expected_output_refs": ["worker_result_docs_reconcile"],
        "evidence_ids": ["evidence_replay_fixture"],
        "metadata": {"fixture_version": "1"},
    }
    payload.update(overrides)
    return SkillReplayFixture.model_validate(payload)


def _observation(**overrides: object) -> SkillReplayObservation:
    payload = {
        "fixture_id": "skill_replay_docs_fixture",
        "outcome": "succeeded",
        "output_refs": ["worker_result_docs_reconcile"],
        "validation_signal_ids": ["signal_pytest"],
        "telemetry_id": "skill_telemetry_docs_success",
        "receipt_ids": ["receipt_replay_docs"],
        "metadata": {"attempt": 1},
    }
    payload.update(overrides)
    return SkillReplayObservation.model_validate(payload)


def test_replay_skill_fixture_passes_matching_observation() -> None:
    result = replay_skill_fixture(
        fixture=_fixture(),
        observation=_observation(),
        created_at=NOW,
    )

    assert result.status == "passed"
    assert result.reason == "replay observation matches fixture"
    assert result.missing_output_refs == []
    assert result.unexpected_output_refs == []
    assert result.telemetry_id == "skill_telemetry_docs_success"
    assert result.created_at == NOW


def test_replay_skill_fixture_fails_outcome_mismatch() -> None:
    result = replay_skill_fixture(
        fixture=_fixture(),
        observation=_observation(outcome="failed", output_refs=[]),
        created_at=NOW,
    )

    assert result.status == "failed"
    assert result.reason == "expected outcome succeeded, observed failed"
    assert result.missing_output_refs == ["worker_result_docs_reconcile"]


def test_replay_skill_fixture_fails_output_mismatch() -> None:
    result = replay_skill_fixture(
        fixture=_fixture(expected_output_refs=["worker_result_docs_reconcile"]),
        observation=_observation(output_refs=["worker_result_other"]),
        created_at=NOW,
    )

    assert result.status == "failed"
    assert result.reason == "observed output refs do not match replay fixture"
    assert result.missing_output_refs == ["worker_result_docs_reconcile"]
    assert result.unexpected_output_refs == ["worker_result_other"]


def test_replay_skill_fixture_fails_fixture_mismatch() -> None:
    result = replay_skill_fixture(
        fixture=_fixture(),
        observation=_observation(fixture_id="other_fixture"),
        created_at=NOW,
    )

    assert result.status == "failed"
    assert result.reason == "observation targets other_fixture, not skill_replay_docs_fixture"


def test_skill_replay_fixtures_and_observations_require_redaction_and_receipts() -> None:
    with pytest.raises(ValidationError, match="must be redacted"):
        _fixture(redacted=False)

    with pytest.raises(ValidationError, match="metadata must be redacted"):
        _fixture(metadata={"stdout": "raw"})

    with pytest.raises(ValidationError, match="receipt_ids"):
        _observation(receipt_ids=[])

    with pytest.raises(ValidationError, match="metadata must be redacted"):
        _observation(metadata={"api_token": "raw"})
