from craik.runtime.companions.mobile_companion import (
    MobileCompanionSurface,
    mobile_companion_decision,
)


def test_mobile_companion_allows_supported_documented_surface() -> None:
    decision = mobile_companion_decision(
        MobileCompanionSurface(
            id="mobile_review_notifications",
            support_level="supported",
            docs_ref="docs/reference/mobile-companion.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.required_controls == [
        "operator_consent",
        "encrypted_device_storage",
        "push_notification_controls",
        "remote_action_controls",
        "offline_action_controls",
        "policy_context",
        "evidence_links",
        "receipts",
        "documented_decision",
    ]


def test_mobile_companion_requires_review_for_experimental_surface() -> None:
    decision = mobile_companion_decision(
        MobileCompanionSurface(
            id="mobile_live_actions",
            support_level="experimental",
            docs_ref="docs/reference/mobile-companion.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental mobile companion surfaces require explicit review"


def test_mobile_companion_defers_deferred_surface() -> None:
    decision = mobile_companion_decision(
        MobileCompanionSurface(
            id="mobile_always_on_agent",
            support_level="deferred",
            docs_ref="docs/reference/mobile-companion.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "mobile companion surface is deferred by product posture"


def test_mobile_companion_blocks_credential_storage() -> None:
    decision = mobile_companion_decision(
        MobileCompanionSurface(
            id="mobile_credential_cache",
            support_level="supported",
            stores_credentials=True,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "mobile companion surfaces must not store credentials"


def test_mobile_companion_blocks_missing_required_controls() -> None:
    cases = [
        (
            MobileCompanionSurface(
                id="mobile_no_consent",
                support_level="supported",
                operator_consent_required=False,
            ),
            "mobile companion surfaces require operator consent",
        ),
        (
            MobileCompanionSurface(
                id="mobile_plain_storage",
                support_level="supported",
                encrypted_device_storage=False,
            ),
            "mobile companion device storage must be encrypted",
        ),
        (
            MobileCompanionSurface(
                id="mobile_no_push_controls",
                support_level="supported",
                push_notification_controls=False,
            ),
            "mobile companion push notifications require controls",
        ),
        (
            MobileCompanionSurface(
                id="mobile_no_remote_controls",
                support_level="supported",
                remote_action_controls=False,
            ),
            "mobile companion remote actions require controls",
        ),
        (
            MobileCompanionSurface(
                id="mobile_no_offline_controls",
                support_level="supported",
                offline_action_controls=False,
            ),
            "mobile companion offline actions require controls",
        ),
        (
            MobileCompanionSurface(
                id="mobile_no_policy",
                support_level="supported",
                preserves_policy_context=False,
            ),
            "mobile companion surfaces must preserve policy and evidence links",
        ),
        (
            MobileCompanionSurface(
                id="mobile_no_receipts",
                support_level="supported",
                requires_receipts=False,
            ),
            "mobile companion surfaces require receipts",
        ),
    ]

    for surface, reason in cases:
        decision = mobile_companion_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
