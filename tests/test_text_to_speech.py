from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.voice.text_to_speech import (
    TextToSpeechArtifact,
    TextToSpeechRequestMetadata,
    TextToSpeechResult,
    text_to_speech_result,
)

NOW = datetime(2026, 5, 16, 18, 25, tzinfo=UTC)


def test_text_to_speech_result_records_generated_artifact_context() -> None:
    result = text_to_speech_result(
        result_id="tts_result_status_update",
        task_id="task_status_update",
        adapter_id="tts_adapter_fixture",
        status="completed",
        request=_request(),
        artifact=_artifact(),
        policy_envelope_id="policy_voice",
        evidence_ids=["evidence_tts_request"],
        receipt_ids=["receipt_tts"],
        created_at=NOW,
    )

    assert result.status == "completed"
    assert result.request.text_summary == "Read the status update."
    assert result.artifact is not None
    assert result.artifact.media_artifact_id == "media_status_update_speech"
    assert result.policy_envelope_id == "policy_voice"
    assert result.evidence_ids == ["evidence_tts_request"]
    assert result.receipt_ids == ["receipt_tts"]
    assert result.created_at == NOW


def test_text_to_speech_result_redacts_prompts_private_payloads_and_media_metadata() -> None:
    result = text_to_speech_result(
        result_id="tts_result_status_update",
        task_id="task_status_update",
        adapter_id="tts_adapter_fixture",
        status="completed",
        request=_request(
            text_summary="token=redactionfixture123",
            metadata={
                "prompt": "private prompt",
                "api_token": "redaction-fixture-value",
                "voice_style": "neutral",
            },
        ),
        artifact=_artifact(metadata={"speech_payload": "raw audio", "codec": "wav"}),
        policy_envelope_id="policy_voice",
        evidence_ids=["evidence_tts_request"],
        receipt_ids=["receipt_tts"],
        created_at=NOW,
    )

    assert result.request.text_summary == "token=[REDACTED]"
    assert result.request.metadata["prompt"] == "[REDACTED]"
    assert result.request.metadata["api_token"] == "[REDACTED]"
    assert result.request.metadata["voice_style"] == "neutral"
    assert result.artifact is not None
    assert result.artifact.metadata["speech_payload"] == "[REDACTED]"
    assert result.artifact.metadata["codec"] == "wav"
    assert result.redacted_paths


def test_failed_text_to_speech_result_requires_errors() -> None:
    with pytest.raises(ValidationError, match="errors"):
        TextToSpeechResult(
            id="tts_result_failed",
            task_id="task_status_update",
            adapter_id="tts_adapter_fixture",
            status="failed",
            request=_request(),
            policy_envelope_id="policy_voice",
            evidence_ids=["evidence_tts_request"],
            receipt_ids=["receipt_tts"],
            created_at=NOW,
        )


def test_completed_text_to_speech_result_requires_artifact() -> None:
    with pytest.raises(ValidationError, match="artifact"):
        TextToSpeechResult(
            id="tts_result_missing_artifact",
            task_id="task_status_update",
            adapter_id="tts_adapter_fixture",
            status="completed",
            request=_request(),
            policy_envelope_id="policy_voice",
            evidence_ids=["evidence_tts_request"],
            receipt_ids=["receipt_tts"],
            created_at=NOW,
        )


def test_text_to_speech_result_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        text_to_speech_result(
            result_id="tts_result_status_update",
            task_id="task_status_update",
            adapter_id="tts_adapter_fixture",
            status="completed",
            request=_request(),
            artifact=_artifact(),
            policy_envelope_id="",
            evidence_ids=["evidence_tts_request"],
            receipt_ids=["receipt_tts"],
        )

    with pytest.raises(ValidationError):
        text_to_speech_result(
            result_id="tts_result_status_update",
            task_id="task_status_update",
            adapter_id="tts_adapter_fixture",
            status="completed",
            request=_request(),
            artifact=_artifact(),
            policy_envelope_id="policy_voice",
            evidence_ids=[],
            receipt_ids=["receipt_tts"],
        )

    with pytest.raises(ValidationError):
        text_to_speech_result(
            result_id="tts_result_status_update",
            task_id="task_status_update",
            adapter_id="tts_adapter_fixture",
            status="completed",
            request=_request(),
            artifact=_artifact(),
            policy_envelope_id="policy_voice",
            evidence_ids=["evidence_tts_request"],
            receipt_ids=[],
        )


def _request(**overrides: object) -> TextToSpeechRequestMetadata:
    payload = {
        "text_summary": "Read the status update.",
        "voice_id": "voice_neutral",
        "language": "en-US",
        "speaking_rate": 1.0,
        "metadata": {"request_source": "operator"},
    }
    payload.update(overrides)
    return TextToSpeechRequestMetadata.model_validate(payload)


def _artifact(**overrides: object) -> TextToSpeechArtifact:
    payload = {
        "media_artifact_id": "media_status_update_speech",
        "media_mime_type": "audio/wav",
        "duration_ms": 1800,
        "byte_count": 48000,
        "metadata": {"codec": "wav"},
    }
    payload.update(overrides)
    return TextToSpeechArtifact.model_validate(payload)
