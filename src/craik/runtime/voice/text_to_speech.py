"""Text-to-speech adapter contract."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel
from craik.runtime.policy.redaction import REDACTION, redact

TextToSpeechStatus = Literal["completed", "partial", "failed"]

_PRIVATE_TTS_KEYS = {
    "payload",
    "private_payload",
    "prompt",
    "raw_audio",
    "raw_payload",
    "request",
    "response",
    "speech_payload",
    "text_prompt",
}


class TextToSpeechRequestMetadata(CraikModel):
    """Redacted request metadata for generated speech."""

    text_summary: str
    voice_id: str | None = None
    language: str | None = None
    speaking_rate: float | None = Field(default=None, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextToSpeechArtifact(CraikModel):
    """Reference to generated speech output."""

    media_artifact_id: str
    media_mime_type: str
    duration_ms: int | None = Field(default=None, ge=0)
    byte_count: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    redacted: bool = True


class TextToSpeechResult(CraikModel):
    """Policy-, evidence-, and receipt-linked text-to-speech result."""

    id: str
    task_id: str
    adapter_id: str
    status: TextToSpeechStatus
    request: TextToSpeechRequestMetadata
    artifact: TextToSpeechArtifact | None = None
    errors: list[str] = Field(default_factory=list)
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    redacted_paths: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_text_to_speech_result(self) -> TextToSpeechResult:
        """Keep TTS results policy-bound and internally consistent."""
        if not self.policy_envelope_id:
            raise ValueError("text-to-speech results require policy_envelope_id")
        if self.status in {"completed", "partial"} and self.artifact is None:
            raise ValueError("completed or partial text-to-speech results require artifact")
        if self.status == "failed" and not self.errors:
            raise ValueError("failed text-to-speech results require errors")
        return self


def text_to_speech_result(
    *,
    result_id: str,
    task_id: str,
    adapter_id: str,
    status: TextToSpeechStatus,
    request: TextToSpeechRequestMetadata,
    policy_envelope_id: str,
    evidence_ids: list[str],
    receipt_ids: list[str],
    artifact: TextToSpeechArtifact | None = None,
    errors: list[str] | None = None,
    created_at: datetime | None = None,
) -> TextToSpeechResult:
    """Build a redacted text-to-speech result."""
    redacted_paths: list[str] = []
    safe_request = request.model_copy(
        update={
            "text_summary": str(_safe_value(request.text_summary, redacted_paths)),
            "metadata": _safe_metadata(request.metadata, redacted_paths),
        }
    )
    safe_artifact = None
    if artifact is not None:
        safe_artifact = artifact.model_copy(
            update={"metadata": _safe_metadata(artifact.metadata, redacted_paths)}
        )
    safe_errors = [str(_safe_value(error, redacted_paths)) for error in errors or []]

    return TextToSpeechResult(
        id=result_id,
        task_id=task_id,
        adapter_id=adapter_id,
        status=status,
        request=safe_request,
        artifact=safe_artifact,
        errors=safe_errors,
        policy_envelope_id=policy_envelope_id,
        evidence_ids=evidence_ids,
        receipt_ids=receipt_ids,
        redacted_paths=sorted(set(redacted_paths)),
        created_at=created_at or datetime.now(UTC),
    )


def _safe_metadata(metadata: dict[str, Any], redacted_paths: list[str]) -> dict[str, Any]:
    safe = _safe_value(metadata, redacted_paths)
    if isinstance(safe, dict):
        return safe
    return {}


def _safe_value(value: Any, redacted_paths: list[str]) -> Any:
    redacted = redact(value)
    redacted_paths.extend(redacted.redacted_paths)
    return _drop_private_tts_payloads(redacted.value, "$", redacted_paths)


def _drop_private_tts_payloads(value: Any, path: str, redacted_paths: list[str]) -> Any:
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PRIVATE_TTS_KEYS:
                safe[key] = REDACTION
                redacted_paths.append(child_path)
            else:
                safe[key] = _drop_private_tts_payloads(item, child_path, redacted_paths)
        return safe
    if isinstance(value, list):
        return [
            _drop_private_tts_payloads(item, f"{path}[{index}]", redacted_paths)
            for index, item in enumerate(value)
        ]
    return value
