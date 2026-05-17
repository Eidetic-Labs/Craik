"""Accessibility requirements for multimodal and companion surfaces."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

AccessibilitySurfaceKind = Literal[
    "desktop_companion",
    "mobile_companion",
    "visual_workspace",
    "voice",
]
AccessibilityCheckStatus = Literal["passed", "failed"]


class AccessibilityRequirements(CraikModel):
    """Accessibility controls expected for multimodal surfaces."""

    surface_kind: AccessibilitySurfaceKind
    keyboard_navigation: bool = True
    screen_reader_labels: bool = True
    reduced_motion_support: bool = True
    contrast_checked: bool = True
    transcripts_available: bool = True
    captions_available: bool = True
    notification_controls: bool = True
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)


class AccessibilityCheck(CraikModel):
    """Reviewable result for accessibility requirements."""

    status: AccessibilityCheckStatus
    surface_kind: AccessibilitySurfaceKind
    missing_requirements: list[str] = Field(default_factory=list)
    policy_envelope_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)


def accessibility_check(requirements: AccessibilityRequirements) -> AccessibilityCheck:
    """Evaluate whether required accessibility controls are present."""
    missing = [
        name
        for name, present in [
            ("keyboard_navigation", requirements.keyboard_navigation),
            ("screen_reader_labels", requirements.screen_reader_labels),
            ("reduced_motion_support", requirements.reduced_motion_support),
            ("contrast_checked", requirements.contrast_checked),
            ("transcripts_available", requirements.transcripts_available),
            ("captions_available", requirements.captions_available),
            ("notification_controls", requirements.notification_controls),
        ]
        if not present
    ]
    return AccessibilityCheck(
        status="failed" if missing else "passed",
        surface_kind=requirements.surface_kind,
        missing_requirements=missing,
        policy_envelope_id=requirements.policy_envelope_id,
        evidence_ids=list(requirements.evidence_ids),
        receipt_ids=list(requirements.receipt_ids),
    )
