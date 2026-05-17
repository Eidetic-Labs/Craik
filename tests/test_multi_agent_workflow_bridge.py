from craik.runtime.bridges.multi_agent_workflow_bridge import (
    MultiAgentWorkflowBridgeSurface,
    multi_agent_workflow_bridge_decision,
)


def test_multi_agent_workflow_bridge_allows_supported_documented_surface() -> None:
    decision = multi_agent_workflow_bridge_decision(
        MultiAgentWorkflowBridgeSurface(
            id="review_queue_bridge",
            workflow_name="Review Queue",
            support_level="supported",
            policy_envelope_id="policy_workflow_bridge",
            docs_ref="docs/reference/multi-agent-workflow-bridge.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == (
        "multi-agent workflow bridge preserves role, queue, approval, policy, evidence, "
        "receipt, and redaction controls"
    )
    assert decision.required_controls == [
        "policy_envelope",
        "role_boundaries",
        "queue_boundaries",
        "approval_gates",
        "policy_context",
        "evidence_links",
        "receipts",
        "payload_redaction",
        "documented_decision",
    ]


def test_multi_agent_workflow_bridge_requires_review_for_experimental_surface() -> None:
    decision = multi_agent_workflow_bridge_decision(
        MultiAgentWorkflowBridgeSurface(
            id="external_swarm_bridge",
            workflow_name="External Swarm",
            support_level="experimental",
            policy_envelope_id="policy_workflow_bridge",
            docs_ref="docs/reference/multi-agent-workflow-bridge.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental multi-agent workflow bridges require explicit review"


def test_multi_agent_workflow_bridge_defers_deferred_surface() -> None:
    decision = multi_agent_workflow_bridge_decision(
        MultiAgentWorkflowBridgeSurface(
            id="autonomous_swarm_bridge",
            workflow_name="Autonomous Swarm",
            support_level="deferred",
            policy_envelope_id="policy_workflow_bridge",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "multi-agent workflow bridge is deferred by product posture"


def test_multi_agent_workflow_bridge_blocks_prohibited_behavior() -> None:
    cases = [
        (
            MultiAgentWorkflowBridgeSurface(
                id="secret_copy_bridge",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                copies_secret_values=True,
            ),
            "multi-agent workflow bridges must not copy secret values",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="unbounded_dispatch_bridge",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                allows_unbounded_dispatch=True,
            ),
            "multi-agent workflow bridges must not allow unbounded dispatch",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="approval_bypass_bridge",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                bypasses_human_approval=True,
            ),
            "multi-agent workflow bridges must preserve approval gates",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="identity_merge_bridge",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                merges_agent_identities=True,
            ),
            "multi-agent workflow bridges must preserve agent identities",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="authoritative_instruction_bridge",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                accepts_external_instructions_as_authoritative=True,
            ),
            "external workflow instructions must not override Craik policy",
        ),
    ]

    for surface, reason in cases:
        decision = multi_agent_workflow_bridge_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason


def test_multi_agent_workflow_bridge_blocks_missing_required_controls() -> None:
    cases = [
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_policy",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="",
            ),
            "multi-agent workflow bridges require policy envelope context",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_roles",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                preserves_role_boundaries=False,
            ),
            "multi-agent workflow bridges must preserve role boundaries",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_queue",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                preserves_queue_boundaries=False,
            ),
            "multi-agent workflow bridges must preserve queue boundaries",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_approval",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                preserves_approval_gates=False,
            ),
            "multi-agent workflow bridges must preserve approval gates",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_policy_context",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                preserves_policy_context=False,
            ),
            "multi-agent workflow bridges must preserve policy context",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_evidence",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                preserves_evidence_links=False,
            ),
            "multi-agent workflow bridges must preserve evidence links",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_receipts",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                requires_receipts=False,
            ),
            "multi-agent workflow bridges require receipts",
        ),
        (
            MultiAgentWorkflowBridgeSurface(
                id="missing_redaction",
                workflow_name="External Workflow",
                support_level="supported",
                policy_envelope_id="policy_workflow_bridge",
                redacts_payloads=False,
            ),
            "multi-agent workflow bridges require payload redaction",
        ),
    ]

    for surface, reason in cases:
        decision = multi_agent_workflow_bridge_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
