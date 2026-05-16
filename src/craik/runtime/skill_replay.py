"""Skill eval/replay harness for learning-loop validation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

SkillReplayStatus = Literal["passed", "failed"]


class SkillReplayFixture(CraikModel):
    """Redacted replay fixture for one skill behavior check."""

    id: str
    skill_package_id: str
    name: str
    input_refs: list[str] = Field(min_length=1)
    expected_outcome: Literal["succeeded", "failed", "partial"]
    expected_output_refs: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(min_length=1)
    redacted: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_skill_replay_fixture(self) -> SkillReplayFixture:
        """Require reproducible, redacted replay fixtures."""
        if not self.redacted:
            raise ValueError("skill replay fixtures must be redacted")
        _reject_unredacted_metadata(self.metadata)
        return self


class SkillReplayObservation(CraikModel):
    """Current skill behavior observed during replay."""

    fixture_id: str
    outcome: Literal["succeeded", "failed", "partial"]
    output_refs: list[str] = Field(default_factory=list)
    validation_signal_ids: list[str] = Field(default_factory=list)
    telemetry_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_skill_replay_observation(self) -> SkillReplayObservation:
        """Keep replay observations auditable and redacted."""
        if not self.receipt_ids:
            raise ValueError("skill replay observations require receipt_ids")
        _reject_unredacted_metadata(self.metadata)
        return self


class SkillReplayResult(CraikModel):
    """Comparison result between replay fixture and current observation."""

    fixture_id: str
    skill_package_id: str
    status: SkillReplayStatus
    reason: str
    expected_outcome: str
    observed_outcome: str
    missing_output_refs: list[str] = Field(default_factory=list)
    unexpected_output_refs: list[str] = Field(default_factory=list)
    telemetry_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def replay_skill_fixture(
    *,
    fixture: SkillReplayFixture,
    observation: SkillReplayObservation,
    created_at: datetime | None = None,
) -> SkillReplayResult:
    """Compare a replay fixture with current skill behavior."""
    if observation.fixture_id != fixture.id:
        return SkillReplayResult(
            fixture_id=fixture.id,
            skill_package_id=fixture.skill_package_id,
            status="failed",
            reason=f"observation targets {observation.fixture_id}, not {fixture.id}",
            expected_outcome=fixture.expected_outcome,
            observed_outcome=observation.outcome,
            telemetry_id=observation.telemetry_id,
            receipt_ids=observation.receipt_ids,
            created_at=created_at or datetime.now(UTC),
        )
    missing = sorted(set(fixture.expected_output_refs) - set(observation.output_refs))
    unexpected = sorted(set(observation.output_refs) - set(fixture.expected_output_refs))
    if observation.outcome != fixture.expected_outcome:
        status: SkillReplayStatus = "failed"
        reason = (
            f"expected outcome {fixture.expected_outcome}, "
            f"observed {observation.outcome}"
        )
    elif missing or unexpected:
        status = "failed"
        reason = "observed output refs do not match replay fixture"
    else:
        status = "passed"
        reason = "replay observation matches fixture"
    return SkillReplayResult(
        fixture_id=fixture.id,
        skill_package_id=fixture.skill_package_id,
        status=status,
        reason=reason,
        expected_outcome=fixture.expected_outcome,
        observed_outcome=observation.outcome,
        missing_output_refs=missing,
        unexpected_output_refs=unexpected,
        telemetry_id=observation.telemetry_id,
        receipt_ids=observation.receipt_ids,
        created_at=created_at or datetime.now(UTC),
    )


def _reject_unredacted_metadata(metadata: dict[str, Any]) -> None:
    for key in metadata:
        normalized = key.lower().replace("-", "_")
        if normalized in _REDACTED_METADATA_KEYS or any(
            token in normalized for token in _SECRET_KEY_TOKENS
        ):
            raise ValueError("skill replay metadata must be redacted")


_REDACTED_METADATA_KEYS = {
    "input",
    "output",
    "payload",
    "prompt",
    "raw_error",
    "response",
    "stderr",
    "stdout",
    "trace",
}
_SECRET_KEY_TOKENS = ("secret", "token", "api_key", "apikey", "password", "credential")
