from craik.runtime.companions.desktop_companion import (
    DesktopCompanionSurface,
    desktop_companion_decision,
)


def test_desktop_companion_allows_supported_documented_surface() -> None:
    decision = desktop_companion_decision(
        DesktopCompanionSurface(
            id="desktop_status_panel",
            support_level="supported",
            docs_ref="docs/reference/desktop-companion.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == (
        "desktop companion surface preserves consent, storage, notification, policy, "
        "evidence, and receipt controls"
    )
    assert decision.required_controls == [
        "operator_consent",
        "encrypted_local_storage",
        "notification_controls",
        "background_action_controls",
        "policy_context",
        "evidence_links",
        "receipts",
        "documented_decision",
    ]


def test_desktop_companion_requires_review_for_experimental_surface() -> None:
    decision = desktop_companion_decision(
        DesktopCompanionSurface(
            id="desktop_live_actions",
            support_level="experimental",
            docs_ref="docs/reference/desktop-companion.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental desktop companion surfaces require explicit review"


def test_desktop_companion_defers_deferred_surface() -> None:
    decision = desktop_companion_decision(
        DesktopCompanionSurface(
            id="desktop_always_on_agent",
            support_level="deferred",
            docs_ref="docs/reference/desktop-companion.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "desktop companion surface is deferred by product posture"


def test_desktop_companion_blocks_secret_storage() -> None:
    decision = desktop_companion_decision(
        DesktopCompanionSurface(
            id="desktop_secret_cache",
            support_level="supported",
            stores_secrets=True,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "desktop companion surfaces must not store secrets"


def test_desktop_companion_blocks_missing_required_controls() -> None:
    cases = [
        (
            DesktopCompanionSurface(
                id="desktop_no_consent",
                support_level="supported",
                operator_consent_required=False,
            ),
            "desktop companion surfaces require operator consent",
        ),
        (
            DesktopCompanionSurface(
                id="desktop_plain_storage",
                support_level="supported",
                local_storage_encrypted=False,
            ),
            "desktop companion local storage must be encrypted",
        ),
        (
            DesktopCompanionSurface(
                id="desktop_no_notifications",
                support_level="supported",
                notification_controls=False,
            ),
            "desktop companion notifications require operator controls",
        ),
        (
            DesktopCompanionSurface(
                id="desktop_no_background_controls",
                support_level="supported",
                background_action_controls=False,
            ),
            "desktop companion background actions require controls",
        ),
        (
            DesktopCompanionSurface(
                id="desktop_no_policy",
                support_level="supported",
                preserves_policy_context=False,
            ),
            "desktop companion surfaces must preserve policy and evidence links",
        ),
        (
            DesktopCompanionSurface(
                id="desktop_no_receipts",
                support_level="supported",
                requires_receipts=False,
            ),
            "desktop companion surfaces require receipts",
        ),
    ]

    for surface, reason in cases:
        decision = desktop_companion_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
