"""Voice input/output posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

VoiceDirection = Literal["input", "output", "bidirectional"]
VoiceSupportLevel = Literal["supported", "experimental", "deferred"]
VoicePostureStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class VoiceSurface(CraikModel):
    """Candidate voice surface for Craik operator interaction."""

    id: str
    direction: VoiceDirection
    support_level: VoiceSupportLevel
    consent_required: bool = True
    preserves_policy_context: bool = True
    preserves_evidence_links: bool = True
    requires_receipts: bool = True
    transcript_redaction: bool = True
    media_metadata_redaction: bool = True
    stores_raw_audio_payloads: bool = False
    docs_ref: str | None = None


class VoicePostureDecision(CraikModel):
    """Decision describing whether a voice surface fits Craik's posture."""

    status: VoicePostureStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def voice_posture_decision(surface: VoiceSurface) -> VoicePostureDecision:
    """Evaluate voice input/output posture for a candidate surface."""
    if surface.stores_raw_audio_payloads:
        return _voice_blocked(surface, "voice surfaces must not persist raw audio payloads")
    if not surface.consent_required:
        return _voice_blocked(surface, "voice surfaces require explicit operator consent")
    if not surface.transcript_redaction or not surface.media_metadata_redaction:
        return _voice_blocked(surface, "voice surfaces require transcript and media redaction")
    if not surface.preserves_policy_context or not surface.preserves_evidence_links:
        return _voice_blocked(surface, "voice surfaces must preserve policy and evidence links")
    if not surface.requires_receipts:
        return _voice_blocked(surface, "voice surfaces require receipts")
    if surface.support_level == "deferred":
        return VoicePostureDecision(
            status="deferred",
            allowed=False,
            reason="voice surface is deferred by product posture",
            surface_id=surface.id,
            required_controls=_voice_controls(surface),
        )
    if surface.support_level == "experimental":
        return VoicePostureDecision(
            status="review_required",
            allowed=False,
            reason="experimental voice surfaces require explicit review before use",
            surface_id=surface.id,
            required_controls=_voice_controls(surface),
        )
    return VoicePostureDecision(
        status="allowed",
        allowed=True,
        reason=(
            "supported voice surface preserves consent, policy, evidence, receipts, and redaction"
        ),
        surface_id=surface.id,
        required_controls=_voice_controls(surface),
    )


def _voice_blocked(surface: VoiceSurface, reason: str) -> VoicePostureDecision:
    return VoicePostureDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_voice_controls(surface),
    )


def _voice_controls(surface: VoiceSurface) -> list[str]:
    controls = ["operator_consent", "transcript_redaction", "media_metadata_redaction"]
    if surface.preserves_policy_context:
        controls.append("policy_context")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.docs_ref:
        controls.append("documented_posture")
    return controls
