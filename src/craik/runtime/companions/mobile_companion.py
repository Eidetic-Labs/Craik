"""Mobile companion app posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

MobileCompanionSupportLevel = Literal["supported", "experimental", "deferred"]
MobileCompanionStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class MobileCompanionSurface(CraikModel):
    """Candidate mobile companion surface."""

    id: str
    support_level: MobileCompanionSupportLevel
    operator_consent_required: bool = True
    preserves_policy_context: bool = True
    preserves_evidence_links: bool = True
    requires_receipts: bool = True
    stores_credentials: bool = False
    encrypted_device_storage: bool = True
    push_notification_controls: bool = True
    remote_action_controls: bool = True
    offline_action_controls: bool = True
    docs_ref: str | None = None


class MobileCompanionDecision(CraikModel):
    """Decision describing whether a mobile companion surface can be used."""

    status: MobileCompanionStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def mobile_companion_decision(surface: MobileCompanionSurface) -> MobileCompanionDecision:
    """Evaluate mobile companion app posture."""
    if surface.stores_credentials:
        return _blocked(surface, "mobile companion surfaces must not store credentials")
    if not surface.operator_consent_required:
        return _blocked(surface, "mobile companion surfaces require operator consent")
    if not surface.encrypted_device_storage:
        return _blocked(surface, "mobile companion device storage must be encrypted")
    if not surface.push_notification_controls:
        return _blocked(surface, "mobile companion push notifications require controls")
    if not surface.remote_action_controls:
        return _blocked(surface, "mobile companion remote actions require controls")
    if not surface.offline_action_controls:
        return _blocked(surface, "mobile companion offline actions require controls")
    if not surface.preserves_policy_context or not surface.preserves_evidence_links:
        return _blocked(
            surface,
            "mobile companion surfaces must preserve policy and evidence links",
        )
    if not surface.requires_receipts:
        return _blocked(surface, "mobile companion surfaces require receipts")
    if surface.support_level == "deferred":
        return MobileCompanionDecision(
            status="deferred",
            allowed=False,
            reason="mobile companion surface is deferred by product posture",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    if surface.support_level == "experimental":
        return MobileCompanionDecision(
            status="review_required",
            allowed=False,
            reason="experimental mobile companion surfaces require explicit review",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    return MobileCompanionDecision(
        status="allowed",
        allowed=True,
        reason=(
            "mobile companion surface preserves consent, storage, notification, action, "
            "policy, evidence, and receipt controls"
        ),
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _blocked(surface: MobileCompanionSurface, reason: str) -> MobileCompanionDecision:
    return MobileCompanionDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _controls(surface: MobileCompanionSurface) -> list[str]:
    controls = ["operator_consent", "encrypted_device_storage", "push_notification_controls"]
    if surface.remote_action_controls:
        controls.append("remote_action_controls")
    if surface.offline_action_controls:
        controls.append("offline_action_controls")
    if surface.preserves_policy_context:
        controls.append("policy_context")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.docs_ref:
        controls.append("documented_decision")
    return controls
