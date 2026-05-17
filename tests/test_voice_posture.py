from craik.runtime.voice.voice_posture import VoiceSurface, voice_posture_decision


def test_voice_posture_allows_supported_documented_surface() -> None:
    decision = voice_posture_decision(
        VoiceSurface(
            id="voice_operator_transcript",
            direction="input",
            support_level="supported",
            docs_ref="docs/reference/voice-posture.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == (
        "supported voice surface preserves consent, policy, evidence, receipts, and redaction"
    )
    assert decision.required_controls == [
        "operator_consent",
        "transcript_redaction",
        "media_metadata_redaction",
        "policy_context",
        "evidence_links",
        "receipts",
        "documented_posture",
    ]


def test_voice_posture_requires_review_for_experimental_surface() -> None:
    decision = voice_posture_decision(
        VoiceSurface(
            id="voice_companion_preview",
            direction="bidirectional",
            support_level="experimental",
            docs_ref="docs/reference/voice-posture.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental voice surfaces require explicit review before use"


def test_voice_posture_defers_deferred_surface() -> None:
    decision = voice_posture_decision(
        VoiceSurface(
            id="voice_always_on_assistant",
            direction="input",
            support_level="deferred",
            docs_ref="docs/reference/voice-posture.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "voice surface is deferred by product posture"


def test_voice_posture_blocks_missing_consent() -> None:
    decision = voice_posture_decision(
        VoiceSurface(
            id="voice_no_consent",
            direction="input",
            support_level="supported",
            consent_required=False,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "voice surfaces require explicit operator consent"


def test_voice_posture_blocks_raw_audio_persistence() -> None:
    decision = voice_posture_decision(
        VoiceSurface(
            id="voice_raw_audio_store",
            direction="input",
            support_level="supported",
            stores_raw_audio_payloads=True,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "voice surfaces must not persist raw audio payloads"


def test_voice_posture_blocks_missing_redaction_policy_evidence_or_receipts() -> None:
    for surface, reason in [
        (
            VoiceSurface(
                id="voice_no_transcript_redaction",
                direction="input",
                support_level="supported",
                transcript_redaction=False,
            ),
            "voice surfaces require transcript and media redaction",
        ),
        (
            VoiceSurface(
                id="voice_no_policy",
                direction="input",
                support_level="supported",
                preserves_policy_context=False,
            ),
            "voice surfaces must preserve policy and evidence links",
        ),
        (
            VoiceSurface(
                id="voice_no_receipts",
                direction="input",
                support_level="supported",
                requires_receipts=False,
            ),
            "voice surfaces require receipts",
        ),
    ]:
        decision = voice_posture_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
