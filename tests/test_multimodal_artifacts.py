from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.voice.multimodal_artifacts import (
    LOCAL_PATH_REDACTION,
    MultimodalArtifactReference,
    multimodal_artifact_reference,
)

NOW = datetime(2026, 5, 16, 18, 45, tzinfo=UTC)


def test_multimodal_artifact_reference_records_portable_context() -> None:
    reference = multimodal_artifact_reference(
        artifact_id="artifact_voice_note",
        task_id="task_voice_note",
        kind="audio",
        locator_kind="artifact_id",
        locator="media_voice_note",
        media_mime_type="audio/wav",
        media_metadata={"duration_ms": 2400, "language": "en-US"},
        policy_envelope_id="policy_voice",
        evidence_ids=["evidence_voice_note"],
        receipt_ids=["receipt_artifact_capture"],
        created_at=NOW,
    )

    assert reference.kind == "audio"
    assert reference.locator == "media_voice_note"
    assert reference.media_mime_type == "audio/wav"
    assert reference.media_metadata == {"duration_ms": 2400, "language": "en-US"}
    assert reference.policy_envelope_id == "policy_voice"
    assert reference.evidence_ids == ["evidence_voice_note"]
    assert reference.receipt_ids == ["receipt_artifact_capture"]
    assert reference.created_at == NOW


def test_multimodal_artifact_reference_redacts_private_media_metadata() -> None:
    reference = multimodal_artifact_reference(
        artifact_id="artifact_voice_note",
        task_id="task_voice_note",
        kind="audio",
        locator_kind="artifact_id",
        locator="media_voice_note?token=redactionfixture123",
        media_mime_type="audio/wav",
        media_metadata={
            "raw_audio": "raw bytes",
            "api_token": "redaction-fixture-value",
            "duration_ms": 2400,
            "nested": {"image_payload": "private"},
        },
        policy_envelope_id="policy_voice",
        evidence_ids=["evidence_voice_note"],
        receipt_ids=["receipt_artifact_capture"],
        created_at=NOW,
    )

    assert reference.locator == "media_voice_note?token=[REDACTED]"
    assert reference.media_metadata["raw_audio"] == "[REDACTED]"
    assert reference.media_metadata["api_token"] == "[REDACTED]"
    assert reference.media_metadata["duration_ms"] == 2400
    assert reference.media_metadata["nested"]["image_payload"] == "[REDACTED]"
    assert reference.redacted_paths


def test_multimodal_artifact_reference_redacts_local_only_paths() -> None:
    reference = multimodal_artifact_reference(
        artifact_id="artifact_local_media",
        task_id="task_voice_note",
        kind="image",
        locator_kind="external_ref",
        locator="/Users/example/private/image.png",
        media_mime_type="image/png",
        media_metadata={"preview_path": "/private/tmp/preview.png"},
        policy_envelope_id="policy_voice",
        evidence_ids=["evidence_voice_note"],
        receipt_ids=["receipt_artifact_capture"],
        created_at=NOW,
    )

    assert reference.locator == LOCAL_PATH_REDACTION
    assert reference.media_metadata["preview_path"] == LOCAL_PATH_REDACTION
    assert reference.redacted_paths


def test_multimodal_artifact_reference_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        multimodal_artifact_reference(
            artifact_id="artifact_voice_note",
            task_id="task_voice_note",
            kind="audio",
            locator_kind="artifact_id",
            locator="media_voice_note",
            policy_envelope_id="",
            evidence_ids=["evidence_voice_note"],
            receipt_ids=["receipt_artifact_capture"],
        )

    with pytest.raises(ValidationError):
        multimodal_artifact_reference(
            artifact_id="artifact_voice_note",
            task_id="task_voice_note",
            kind="audio",
            locator_kind="artifact_id",
            locator="media_voice_note",
            policy_envelope_id="policy_voice",
            evidence_ids=[],
            receipt_ids=["receipt_artifact_capture"],
        )

    with pytest.raises(ValidationError):
        multimodal_artifact_reference(
            artifact_id="artifact_voice_note",
            task_id="task_voice_note",
            kind="audio",
            locator_kind="artifact_id",
            locator="media_voice_note",
            policy_envelope_id="policy_voice",
            evidence_ids=["evidence_voice_note"],
            receipt_ids=[],
        )


def test_multimodal_artifact_relative_path_locators_must_be_portable() -> None:
    with pytest.raises(ValidationError, match="relative_path"):
        MultimodalArtifactReference(
            id="artifact_local_absolute",
            task_id="task_voice_note",
            kind="image",
            locator_kind="relative_path",
            locator="/tmp/private-image.png",
            policy_envelope_id="policy_voice",
            evidence_ids=["evidence_voice_note"],
            receipt_ids=["receipt_artifact_capture"],
            created_at=NOW,
        )
