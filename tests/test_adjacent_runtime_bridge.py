from craik.runtime.bridges.adjacent_runtime_bridge import (
    AdjacentRuntimeBridgeSurface,
    adjacent_runtime_bridge_decision,
)


def test_adjacent_runtime_bridge_allows_supported_documented_surface() -> None:
    decision = adjacent_runtime_bridge_decision(
        AdjacentRuntimeBridgeSurface(
            id="local_runner_bridge",
            runtime_name="Local Runner",
            support_level="supported",
            policy_envelope_id="policy_adjacent_runtime",
            docs_ref="docs/reference/adjacent-runtime-bridge.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == (
        "adjacent runtime bridge preserves policy, evidence, capability grant, receipt, "
        "and redaction controls"
    )
    assert decision.required_controls == [
        "policy_envelope",
        "policy_context",
        "evidence_links",
        "capability_grant",
        "receipts",
        "input_redaction",
        "output_redaction",
        "documented_decision",
    ]


def test_adjacent_runtime_bridge_requires_review_for_experimental_surface() -> None:
    decision = adjacent_runtime_bridge_decision(
        AdjacentRuntimeBridgeSurface(
            id="remote_runner_bridge",
            runtime_name="Remote Runner",
            support_level="experimental",
            policy_envelope_id="policy_adjacent_runtime",
            docs_ref="docs/reference/adjacent-runtime-bridge.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental adjacent runtime bridges require explicit review"


def test_adjacent_runtime_bridge_defers_deferred_surface() -> None:
    decision = adjacent_runtime_bridge_decision(
        AdjacentRuntimeBridgeSurface(
            id="autonomous_remote_runtime",
            runtime_name="Autonomous Remote Runtime",
            support_level="deferred",
            policy_envelope_id="policy_adjacent_runtime",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "adjacent runtime bridge is deferred by product posture"


def test_adjacent_runtime_bridge_blocks_prohibited_behavior() -> None:
    cases = [
        (
            AdjacentRuntimeBridgeSurface(
                id="secret_copy_bridge",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                copies_secret_values=True,
            ),
            "adjacent runtime bridges must not copy secret values",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="unbounded_tools_bridge",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                grants_unbounded_tool_access=True,
            ),
            "adjacent runtime bridges must not grant unbounded tool access",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="authoritative_instructions_bridge",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                accepts_runtime_instructions_as_authoritative=True,
            ),
            "adjacent runtime instructions must not override Craik policy",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="silent_mutation_bridge",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                mutates_without_operator_approval=True,
            ),
            "adjacent runtime mutations require operator approval",
        ),
    ]

    for surface, reason in cases:
        decision = adjacent_runtime_bridge_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason


def test_adjacent_runtime_bridge_blocks_missing_required_controls() -> None:
    cases = [
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_policy_envelope",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="",
            ),
            "adjacent runtime bridges require policy envelope context",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_policy_context",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                preserves_policy_context=False,
            ),
            "adjacent runtime bridges must preserve policy context",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_evidence",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                preserves_evidence_links=False,
            ),
            "adjacent runtime bridges must preserve evidence links",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_grant",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                requires_capability_grant=False,
            ),
            "adjacent runtime bridges require capability grants",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_receipts",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                requires_receipts=False,
            ),
            "adjacent runtime bridges require receipts",
        ),
        (
            AdjacentRuntimeBridgeSurface(
                id="missing_redaction",
                runtime_name="Adjacent Runtime",
                support_level="supported",
                policy_envelope_id="policy_adjacent_runtime",
                redacts_inputs=False,
            ),
            "adjacent runtime bridges require input and output redaction",
        ),
    ]

    for surface, reason in cases:
        decision = adjacent_runtime_bridge_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
