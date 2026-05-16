from craik.contracts.models import (
    Assumption,
    CapabilityReceipt,
    ContradictionReport,
    DistilledInstructionProposal,
    EvidenceReference,
    Handoff,
    HumanDelegationPoint,
    InstructionPromotionReview,
    InstructionProvenance,
    InstructionSource,
    InstructionSourceSnapshot,
    PluginReceipt,
    WorkGraphEdge,
    WorkGraphExport,
    WorkGraphNode,
)
from craik.runtime.operator_views import (
    BudgetQuotaSnapshot,
    InstructionDistillationSnapshot,
    format_budget_quota_view,
    format_contradiction_inbox,
    format_delegation_queue,
    format_evidence_assumption_view,
    format_handoff_viewer,
    format_instruction_distillation_view,
    format_receipt_viewer,
    format_work_graph_explorer,
)


def test_work_graph_explorer_formats_nodes_and_edges() -> None:
    export = WorkGraphExport(
        id="graph_task_docs_reconcile",
        task_id="task_docs_reconcile",
        nodes=[
            WorkGraphNode(
                id="task:task_docs_reconcile",
                type="task",
                label="Reconcile docs",
                task_id="task_docs_reconcile",
            ),
            WorkGraphNode(
                id="handoff:handoff_docs_reconcile",
                type="handoff",
                label="Docs handoff",
                task_id="task_docs_reconcile",
            ),
        ],
        edges=[
            WorkGraphEdge(
                id="edge:has_handoff",
                type="has_handoff",
                from_node="task:task_docs_reconcile",
                to_node="handoff:handoff_docs_reconcile",
                metadata={"status": "completed"},
            )
        ],
        created_at="2026-05-16T16:55:00Z",
    )
    lines = format_work_graph_explorer(export)

    assert lines[:4] == [
        "Work Graph: graph_task_docs_reconcile",
        "Task: task_docs_reconcile",
        "Nodes: 2",
        "Edges: 1",
    ]
    assert "- task:task_docs_reconcile [task] task=task_docs_reconcile:" in lines[6]
    assert "task:task_docs_reconcile -[has_handoff]-> handoff:handoff_docs_reconcile" in lines[-1]
    assert "status=completed" in lines[-1]


def test_work_graph_explorer_empty_state() -> None:
    export = WorkGraphExport(
        id="graph_all",
        task_id=None,
        nodes=[],
        edges=[],
        created_at="2026-05-16T16:55:00Z",
    )

    lines = format_work_graph_explorer(export)

    assert lines == [
        "Work Graph: graph_all",
        "Task: all",
        "Nodes: 0",
        "Edges: 0",
        "",
        "Nodes",
        "",
        "Edges",
    ]


def test_handoff_viewer_formats_summary_links_and_empty_sections() -> None:
    handoff = Handoff.model_validate(
        {
            "id": "handoff_docs_reconcile",
            "task_id": "task_docs_reconcile",
            "project_id": "project_stigmem",
            "agent": "agent:codex",
            "status": "completed",
            "summary": "Contract schema work completed with tests and docs.",
            "self_audit": {
                "schema_validated": True,
                "redaction_reviewed": True,
                "receipts_reviewed": True,
                "assumptions_reviewed": True,
                "validation_recorded": True,
                "policy_exceptions_disclosed": True,
                "notes": [],
            },
            "completed_actions": ["Added schemas.", "Validated fixtures."],
            "artifacts": ["docs/reference/schemas.md"],
            "files_changed": ["src/craik/contracts/models.py"],
            "risks": [],
            "next_steps": ["Implement project registry."],
            "receipt_ids": ["receipt_pytest"],
            "open_human_delegation_ids": ["delegation_docs_reconcile_approval"],
            "created_at": "2026-05-16T16:55:00Z",
        }
    )

    lines = format_handoff_viewer(handoff)

    assert lines[:6] == [
        "Handoff: handoff_docs_reconcile",
        "Task: task_docs_reconcile",
        "Project: project_stigmem",
        "Status: completed",
        "Agent: agent:codex",
        "Summary: Contract schema work completed with tests and docs.",
    ]
    assert "- receipt_pytest" in lines
    assert "- docs/reference/schemas.md" in lines
    assert "- src/craik/contracts/models.py" in lines
    assert "- none" in lines
    assert "- delegation_docs_reconcile_approval" in lines


def test_receipt_viewer_formats_capability_receipt_statuses() -> None:
    for status in ("passed", "failed", "denied", "skipped"):
        receipt = CapabilityReceipt.model_validate(
            {
                "id": f"receipt_{status}",
                "task_id": "task_docs_reconcile",
                "actor": "agent:codex",
                "capability": "shell.test",
                "target": "uv run --extra dev pytest",
                "policy_profile": "strict",
                "reason": "Validate operator receipt formatting.",
                "result": {
                    "status": status,
                    "summary": f"Receipt {status}.",
                    "metadata": {"redacted": True},
                },
                "redacted": True,
                "created_at": "2026-05-16T17:00:00Z",
            }
        )

        lines = format_receipt_viewer(receipt)

        assert f"Capability Receipt: receipt_{status}" in lines
        assert f"Status: {status}" in lines
        assert "Redacted: True" in lines


def test_receipt_viewer_formats_plugin_receipt_links() -> None:
    receipt = PluginReceipt.model_validate(
        {
            "id": "plugin_receipt_docs_reconcile",
            "task_id": "task_docs_reconcile",
            "actor": "agent:codex",
            "plugin_descriptor_id": "plugin_docs_reconcile",
            "action": "docs.reconcile",
            "capability_grant_ids": ["plugin_grant_docs_reconcile"],
            "trust_boundary": "project",
            "result": {
                "status": "denied",
                "summary": "Plugin action denied by policy.",
                "metadata": {"redacted": True},
            },
            "evidence_ids": ["evidence_readme_status"],
            "handoff_ids": ["handoff_docs_reconcile"],
            "redacted": True,
            "created_at": "2026-05-16T17:00:00Z",
        }
    )

    lines = format_receipt_viewer(receipt)

    assert "Plugin Receipt: plugin_receipt_docs_reconcile" in lines
    assert "Plugin: plugin_docs_reconcile" in lines
    assert "Status: denied" in lines
    assert "- plugin_grant_docs_reconcile" in lines
    assert "- evidence_readme_status" in lines
    assert "- handoff_docs_reconcile" in lines


def test_contradiction_inbox_formats_statuses_and_review_links() -> None:
    reports = [
        _contradiction("contradiction_open", "open"),
        _contradiction("contradiction_resolved", "resolved"),
        _contradiction("contradiction_ignored", "ignored", owner=None),
    ]

    lines = format_contradiction_inbox(reports)

    assert lines[0] == "Contradiction Inbox: 3"
    assert "- contradiction_ignored [ignored]" in lines
    assert "- contradiction_open [open]" in lines
    assert "- contradiction_resolved [resolved]" in lines
    assert "  Owner: unassigned" in lines
    assert "  Affected Artifacts: README.md" in lines
    assert "  Evidence: evidence_readme_status" in lines


def test_contradiction_inbox_empty_state() -> None:
    assert format_contradiction_inbox([]) == ["Contradiction Inbox: 0", "", "- none"]


def test_evidence_assumption_view_keeps_assumptions_distinct() -> None:
    evidence = EvidenceReference.model_validate(
        {
            "id": "evidence_readme_status",
            "source": "README.md",
            "kind": "file",
            "locator": "README.md#status",
            "summary": "README documents project status.",
            "captured_at": "2026-05-16T17:15:00Z",
        }
    )
    assumption = Assumption.model_validate(
        {
            "id": "assumption_docs_stale",
            "task_id": "task_docs_reconcile",
            "statement": "Docs may be stale.",
            "rationale": "Review requested docs reconciliation.",
            "evidence_ids": ["evidence_readme_status"],
            "confidence": 0.65,
            "status": "open",
        }
    )

    lines = format_evidence_assumption_view([evidence], [assumption])

    assert lines[0] == "Evidence: 1"
    assert "[file] source=README.md" in lines[2]
    assert "Assumptions: 1" in lines
    assert "[open] task=task_docs_reconcile confidence=0.65" in lines[-1]
    assert "evidence=evidence_readme_status" in lines[-1]


def test_evidence_assumption_view_empty_state() -> None:
    assert format_evidence_assumption_view([], []) == [
        "Evidence: 0",
        "",
        "- none",
        "",
        "Assumptions: 0",
        "",
        "- none",
    ]


def test_delegation_queue_formats_open_resolved_and_cancelled() -> None:
    delegations = [
        _delegation("delegation_open", "open", "approval"),
        _delegation("delegation_resolved", "resolved", "clarification", resolution="Approved."),
        _delegation("delegation_cancelled", "cancelled", "escalation", owner=None),
    ]

    lines = format_delegation_queue(delegations)

    assert lines[0] == "Delegation Queue: 3"
    assert "- delegation_cancelled [cancelled/escalation]" in lines
    assert "- delegation_open [open/approval]" in lines
    assert "- delegation_resolved [resolved/clarification]" in lines
    assert "  Owner: unassigned" in lines
    assert "  Policy: policy_docs_reconcile" in lines
    assert "  Receipts: receipt_pytest" in lines
    assert "  Resolution: Approved." in lines


def test_delegation_queue_empty_state() -> None:
    assert format_delegation_queue([]) == ["Delegation Queue: 0", "", "- none"]


def test_budget_quota_view_formats_configured_missing_and_exceeded_states() -> None:
    snapshot = BudgetQuotaSnapshot(
        configured_limits={"tokens": 1000, "requests": 25},
        usage={"tokens": 1200, "requests": 10},
        missing=["cost_usd"],
        exceeded=["tokens"],
        notes=["Cost data unavailable in local fixtures."],
    )

    lines = format_budget_quota_view(snapshot)

    assert lines[:3] == ["Budget And Quota", "", "Configured Limits"]
    assert "- requests: 25" in lines
    assert "- tokens: 1200" in lines
    assert "- cost_usd" in lines
    assert "- tokens" in lines
    assert "- Cost data unavailable in local fixtures." in lines


def test_budget_quota_view_empty_state_does_not_infer_costs() -> None:
    lines = format_budget_quota_view(BudgetQuotaSnapshot(missing=["cost_usd"]))

    assert lines.count("- none") == 4
    assert "- cost_usd" in lines


def test_instruction_distillation_view_formats_sources_proposals_and_reviews() -> None:
    source = InstructionSource.model_validate(
        {
            "id": "instruction_source_agents_md",
            "project_id": "project_craik",
            "kind": "agents_md",
            "path": "AGENTS.md",
            "owner": "team:platform",
            "trust_boundary": "repository",
            "active": True,
            "declared_by": "user:maintainer",
            "created_at": "2026-05-16T17:30:00Z",
        }
    )
    source_snapshot = InstructionSourceSnapshot.model_validate(
        {
            "id": "snapshot_agents_md",
            "project_id": "project_craik",
            "source_id": "instruction_source_agents_md",
            "path": "AGENTS.md",
            "content_hash": "abc123",
            "hash_status": "unchanged",
            "captured_at": "2026-05-16T17:31:00Z",
        }
    )
    provenance = InstructionProvenance.model_validate(
        {
            "id": "provenance_agents_review",
            "project_id": "project_craik",
            "source_id": "instruction_source_agents_md",
            "snapshot_id": "snapshot_agents_md",
            "path": "AGENTS.md",
            "start_line": 10,
            "end_line": 12,
            "summary": "Review instructions before promotion.",
            "captured_at": "2026-05-16T17:32:00Z",
        }
    )
    approved = DistilledInstructionProposal.model_validate(
        {
            "id": "proposal_review_before_promotion",
            "project_id": "project_craik",
            "source_id": "instruction_source_agents_md",
            "snapshot_id": "snapshot_agents_md",
            "category": "policy",
            "statement": "Review distilled instructions before promotion.",
            "rationale": "Instruction files are evidence, not automatic authority.",
            "confidence": 0.9,
            "provenance_ids": ["provenance_agents_review"],
            "evidence_ids": ["evidence_agents_md"],
            "promotion_status": "approved",
            "promoted_constraint_id": "constraint_review_before_promotion",
            "decided_by": "user:maintainer",
            "decided_at": "2026-05-16T17:35:00Z",
            "created_at": "2026-05-16T17:33:00Z",
        }
    )
    deferred = DistilledInstructionProposal.model_validate(
        {
            "id": "proposal_stale_instruction",
            "project_id": "project_craik",
            "source_id": "instruction_source_agents_md",
            "snapshot_id": "snapshot_agents_md",
            "category": "stale_risk",
            "statement": "Prior context may be stale after instruction changes.",
            "rationale": "Snapshot changed after extraction.",
            "confidence": 0.7,
            "provenance_ids": ["provenance_agents_review"],
            "promotion_status": "deferred",
            "decided_by": "user:maintainer",
            "decided_at": "2026-05-16T17:36:00Z",
            "created_at": "2026-05-16T17:34:00Z",
        }
    )
    review = InstructionPromotionReview.model_validate(
        {
            "id": "review_review_before_promotion",
            "project_id": "project_craik",
            "proposal_id": "proposal_review_before_promotion",
            "decision": "approved",
            "decided_by": "user:maintainer",
            "rationale": "Promotion keeps trust boundary explicit.",
            "promoted_constraint_id": "constraint_review_before_promotion",
            "policy_envelope_id": "policy_instruction_review",
            "receipt_ids": ["receipt_instruction_review"],
            "handoff_ids": ["handoff_instruction_review"],
            "created_at": "2026-05-16T17:37:00Z",
        }
    )

    lines = format_instruction_distillation_view(
        InstructionDistillationSnapshot(
            sources=[source],
            snapshots=[source_snapshot],
            provenance=[provenance],
            proposals=[deferred, approved],
            reviews=[review],
        )
    )

    assert lines[:3] == ["Instruction Distillation", "", "Sources"]
    assert (
        "- instruction_source_agents_md [agents_md/active] path=AGENTS.md "
        "owner=team:platform trust=repository"
    ) in lines
    assert any(
        line.startswith(
            "- snapshot_agents_md source=instruction_source_agents_md status=unchanged"
        )
        for line in lines
    )
    assert any(
        "range=L10-L12: Review instructions before promotion." in line for line in lines
    )
    assert "- proposal_review_before_promotion [approved/policy]" in lines
    assert "  Active Constraint: constraint_review_before_promotion" in lines
    assert "- proposal_stale_instruction [deferred/stale_risk]" in lines
    assert "  Active Constraint: none" in lines
    assert "- review_review_before_promotion [approved]" in lines[-7]
    assert "  Receipts: receipt_instruction_review" in lines
    assert "  Handoffs: handoff_instruction_review" in lines


def test_instruction_distillation_view_empty_state() -> None:
    lines = format_instruction_distillation_view(InstructionDistillationSnapshot())

    assert lines == [
        "Instruction Distillation",
        "",
        "Sources",
        "- none",
        "",
        "Snapshots",
        "- none",
        "",
        "Provenance",
        "- none",
        "",
        "Distilled Proposals",
        "- none",
        "",
        "Promotion Reviews",
        "- none",
    ]


def _delegation(
    delegation_id: str,
    status: str,
    kind: str,
    *,
    owner: str | None = "user:maintainer",
    resolution: str | None = None,
) -> HumanDelegationPoint:
    return HumanDelegationPoint.model_validate(
        {
            "id": delegation_id,
            "task_id": "task_docs_reconcile",
            "kind": kind,
            "status": status,
            "summary": "Human review required.",
            "requested_decision": "Approve fixture update.",
            "requested_by": "agent:codex",
            "owner": owner,
            "policy_envelope_id": "policy_docs_reconcile",
            "receipt_ids": ["receipt_pytest"],
            "created_at": "2026-05-16T17:20:00Z",
            "resolved_at": "2026-05-16T17:25:00Z" if resolution else None,
            "resolution": resolution,
        }
    )


def _contradiction(
    report_id: str,
    status: str,
    *,
    owner: str | None = "user:maintainer",
) -> ContradictionReport:
    return ContradictionReport.model_validate(
        {
            "id": report_id,
            "task_id": "task_docs_reconcile",
            "facts": ["fact_docs_planned", "fact_cli_implemented"],
            "summary": "Docs and implementation disagree.",
            "affected_artifacts": ["README.md"],
            "evidence_ids": ["evidence_readme_status"],
            "proposed_resolution": "Update docs to match implementation.",
            "status": status,
            "owner": owner,
            "created_at": "2026-05-16T17:10:00Z",
        }
    )
