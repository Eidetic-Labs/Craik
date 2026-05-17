import pytest
from pydantic import ValidationError

from craik.runtime.accessibility import AccessibilityRequirements, accessibility_check


def test_accessibility_check_passes_when_all_requirements_are_present() -> None:
    check = accessibility_check(_requirements())

    assert check.status == "passed"
    assert check.surface_kind == "visual_workspace"
    assert check.missing_requirements == []
    assert check.policy_envelope_id == "policy_accessibility"
    assert check.evidence_ids == ["evidence_accessibility"]
    assert check.receipt_ids == ["receipt_accessibility"]


def test_accessibility_check_reports_missing_requirements() -> None:
    check = accessibility_check(
        _requirements(
            keyboard_navigation=False,
            screen_reader_labels=False,
            captions_available=False,
        )
    )

    assert check.status == "failed"
    assert check.missing_requirements == [
        "keyboard_navigation",
        "screen_reader_labels",
        "captions_available",
    ]


def test_accessibility_requirements_preserve_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError):
        _requirements(evidence_ids=[])

    with pytest.raises(ValidationError):
        _requirements(receipt_ids=[])


def _requirements(**overrides: object) -> AccessibilityRequirements:
    payload = {
        "surface_kind": "visual_workspace",
        "keyboard_navigation": True,
        "screen_reader_labels": True,
        "reduced_motion_support": True,
        "contrast_checked": True,
        "transcripts_available": True,
        "captions_available": True,
        "notification_controls": True,
        "policy_envelope_id": "policy_accessibility",
        "evidence_ids": ["evidence_accessibility"],
        "receipt_ids": ["receipt_accessibility"],
    }
    payload.update(overrides)
    return AccessibilityRequirements.model_validate(payload)
