"""Multimodal artifact reference contracts."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel
from craik.runtime.redaction import REDACTION, redact

MultimodalArtifactKind = Literal[
    "audio",
    "image",
    "video",
    "transcript",
    "canvas",
    "document",
    "other",
]
MultimodalArtifactLocatorKind = Literal[
    "artifact_id",
    "content_hash",
    "url",
    "relative_path",
    "external_ref",
]

_PRIVATE_ARTIFACT_KEYS = {
    "audio_payload",
    "bytes",
    "content",
    "credentials",
    "image_payload",
    "payload",
    "private_metadata",
    "raw_audio",
    "raw_image",
    "raw_media",
    "raw_video",
    "video_payload",
}
LOCAL_PATH_REDACTION = "[LOCAL_PATH]"
_LOCAL_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![\w.-])/(?:Users|private|tmp|var/folders)/[^\s'\"),\]}]+"),
    re.compile(r"(?i)\b[A-Z]:\\Users\\[^\s'\"),\]}]+"),
)


class MultimodalArtifactReference(CraikModel):
    """Portable reference to a multimodal artifact."""

    id: str
    task_id: str
    kind: MultimodalArtifactKind
    locator_kind: MultimodalArtifactLocatorKind
    locator: str
    media_mime_type: str | None = None
    media_metadata: dict[str, Any] = Field(default_factory=dict)
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    redacted_paths: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_multimodal_artifact_reference(self) -> MultimodalArtifactReference:
        """Keep artifact references policy-bound and portable."""
        if not self.policy_envelope_id:
            raise ValueError("multimodal artifact references require policy_envelope_id")
        if self.locator_kind == "relative_path" and self.locator.startswith("/"):
            raise ValueError("relative_path locators must not be absolute paths")
        return self


def multimodal_artifact_reference(
    *,
    artifact_id: str,
    task_id: str,
    kind: MultimodalArtifactKind,
    locator_kind: MultimodalArtifactLocatorKind,
    locator: str,
    policy_envelope_id: str,
    evidence_ids: list[str],
    receipt_ids: list[str],
    media_mime_type: str | None = None,
    media_metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> MultimodalArtifactReference:
    """Build a redacted multimodal artifact reference."""
    redacted_paths: list[str] = []
    safe_locator = str(_safe_value(locator, redacted_paths))
    safe_metadata = _safe_metadata(media_metadata or {}, redacted_paths)

    return MultimodalArtifactReference(
        id=artifact_id,
        task_id=task_id,
        kind=kind,
        locator_kind=locator_kind,
        locator=safe_locator,
        media_mime_type=media_mime_type,
        media_metadata=safe_metadata,
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
    return _drop_private_media_payloads(redacted.value, "$", redacted_paths)


def _drop_private_media_payloads(value: Any, path: str, redacted_paths: list[str]) -> Any:
    if isinstance(value, str):
        return _redact_local_paths(value, path, redacted_paths)
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PRIVATE_ARTIFACT_KEYS:
                safe[key] = REDACTION
                redacted_paths.append(child_path)
            else:
                safe[key] = _drop_private_media_payloads(item, child_path, redacted_paths)
        return safe
    if isinstance(value, list):
        return [
            _drop_private_media_payloads(item, f"{path}[{index}]", redacted_paths)
            for index, item in enumerate(value)
        ]
    return value


def _redact_local_paths(value: str, path: str, redacted_paths: list[str]) -> str:
    redacted = value
    for pattern in _LOCAL_PATH_PATTERNS:
        redacted = pattern.sub(LOCAL_PATH_REDACTION, redacted)
    if redacted != value:
        redacted_paths.append(path)
    return redacted
