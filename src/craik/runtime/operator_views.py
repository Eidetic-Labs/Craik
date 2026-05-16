"""Read-only operator view formatters."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from craik.contracts.models import (
    Assumption,
    CapabilityReceipt,
    ContradictionReport,
    DistilledInstructionProposal,
    EvidenceCoverageScore,
    EvidenceReference,
    FactValue,
    Handoff,
    HandoffQualityScore,
    HumanDelegationPoint,
    InstructionPromotionReview,
    InstructionProvenance,
    InstructionSource,
    InstructionSourceSnapshot,
    MemoryFactReference,
    MemoryImpactPreview,
    MemoryProposal,
    PluginReceipt,
    RedTeamFinding,
    RuntimeCriticFinding,
    WorkGraphEdge,
    WorkGraphExport,
    WorkGraphNode,
)


@dataclass(frozen=True)
class BudgetQuotaSnapshot:
    """Operator-visible budget and quota state."""

    configured_limits: dict[str, float | int | str] = field(default_factory=dict)
    usage: dict[str, float | int | str] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    exceeded: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QualityGateSnapshot:
    """Operator-visible quality gate review state."""

    handoff_scores: list[HandoffQualityScore] = field(default_factory=list)
    evidence_scores: list[EvidenceCoverageScore] = field(default_factory=list)
    critic_findings: list[RuntimeCriticFinding] = field(default_factory=list)
    red_team_findings: list[RedTeamFinding] = field(default_factory=list)


@dataclass(frozen=True)
class InstructionDistillationSnapshot:
    """Operator-visible instruction distillation review state."""

    sources: list[InstructionSource] = field(default_factory=list)
    snapshots: list[InstructionSourceSnapshot] = field(default_factory=list)
    provenance: list[InstructionProvenance] = field(default_factory=list)
    proposals: list[DistilledInstructionProposal] = field(default_factory=list)
    reviews: list[InstructionPromotionReview] = field(default_factory=list)


@dataclass(frozen=True)
class MemoryImpactPreviewSnapshot:
    """Operator-visible memory impact preview state."""

    preview: MemoryImpactPreview
    proposals: list[MemoryProposal] = field(default_factory=list)
    policy_envelope_id: str | None = None
    receipt_ids: list[str] = field(default_factory=list)


def format_quality_gate_view(snapshot: QualityGateSnapshot) -> list[str]:
    """Format quality gate state while keeping findings non-authoritative."""
    lines = [
        f"Quality Gate: {_quality_gate_state(snapshot)}",
        "",
        "Handoff Quality Scores",
    ]
    if not snapshot.handoff_scores:
        lines.append("- none")
    else:
        for score in sorted(snapshot.handoff_scores, key=lambda item: item.id):
            lines.extend(
                [
                    f"- {score.id} [{score.band}] score={score.score:.2f} "
                    f"handoff={score.handoff_id}",
                    f"  Blocking Reasons: {_join_or_none(score.blocking_reasons)}",
                    f"  Components: {_format_score_components(score)}",
                ]
            )

    lines.extend(["", "Evidence Coverage Scores"])
    if not snapshot.evidence_scores:
        lines.append("- none")
    else:
        for coverage_score in sorted(snapshot.evidence_scores, key=lambda item: item.id):
            lines.extend(
                [
                    f"- {coverage_score.id} [{coverage_score.band}] "
                    f"score={coverage_score.score:.2f} "
                    f"handoff={coverage_score.handoff_id or 'none'}",
                    f"  Evidence: {_join_or_none(coverage_score.evidence_ids)}",
                    "  Missing Evidence: "
                    f"{_join_or_none(coverage_score.missing_evidence_ids)}",
                    f"  Weak Claims: {_join_or_none(coverage_score.weak_claims)}",
                ]
            )

    lines.extend(["", "Critic Findings"])
    if not snapshot.critic_findings:
        lines.append("- none")
    else:
        for finding in sorted(
            snapshot.critic_findings,
            key=lambda item: (item.review_status, item.severity, item.id),
        ):
            lines.extend(
                [
                    f"- {finding.id} [{finding.review_status}/{finding.severity}] "
                    f"type={finding.finding_type}",
                    f"  Authoritative: {finding.authoritative}",
                    f"  Adjudication: {finding.adjudication_id or 'none'}",
                    f"  Affected Artifacts: {_join_or_none(finding.affected_artifacts)}",
                    f"  Evidence: {_join_or_none(finding.evidence_ids)}",
                    f"  Proposed Actions: {_join_or_none(finding.proposed_actions)}",
                    f"  Summary: {finding.summary}",
                ]
            )

    lines.extend(["", "Red-Team Findings"])
    if not snapshot.red_team_findings:
        lines.append("- none")
    else:
        for red_team_finding in sorted(
            snapshot.red_team_findings,
            key=lambda item: (not item.blocking, item.review_status, item.severity, item.id),
        ):
            lines.extend(
                [
                    f"- {red_team_finding.id} "
                    f"[{red_team_finding.review_status}/{red_team_finding.severity}] "
                    f"type={red_team_finding.finding_type} "
                    f"blocking={red_team_finding.blocking}",
                    f"  Authoritative: {red_team_finding.authoritative}",
                    f"  Adjudication: {red_team_finding.adjudication_id or 'none'}",
                    "  Affected Artifacts: "
                    f"{_join_or_none(red_team_finding.affected_artifacts)}",
                    f"  Evidence: {_join_or_none(red_team_finding.evidence_ids)}",
                    "  Proposed Actions: "
                    f"{_join_or_none(red_team_finding.proposed_actions)}",
                    f"  Summary: {red_team_finding.summary}",
                ]
            )

    return lines


def format_memory_impact_preview_view(snapshot: MemoryImpactPreviewSnapshot) -> list[str]:
    """Format memory impact without treating proposals as accepted facts."""
    preview = snapshot.preview
    lines = [
        f"Memory Impact Preview: {preview.id}",
        f"Task: {preview.task_id}",
        f"Policy: {snapshot.policy_envelope_id or 'none'}",
        f"Receipts: {_join_or_none(snapshot.receipt_ids)}",
        "",
        "Proposed Memory Writes",
    ]
    if not snapshot.proposals:
        lines.append("- none")
    else:
        for proposal in sorted(snapshot.proposals, key=lambda item: item.id):
            lines.extend(
                [
                    f"- {proposal.id} [{proposal.status}/{proposal.operation}]",
                    f"  Fact: {_format_fact_reference(proposal.fact)}",
                    f"  Evidence: {_join_or_none([item.id for item in proposal.evidence])}",
                    f"  Run: {proposal.run_id or 'none'}",
                    f"  Step: {proposal.step_id or 'none'}",
                    f"  Handoff: {proposal.handoff_id or 'none'}",
                ]
            )

    lines.extend(["", "Facts To Add"])
    lines.extend(_format_memory_fact_references(preview.facts_to_add))
    lines.extend(["", "Facts To Invalidate"])
    lines.extend(_format_memory_fact_references(preview.facts_to_invalidate))
    lines.extend(["", "Evidence Gaps", *_format_items(preview.evidence_missing)])
    lines.extend(["", "Contradiction Risks"])
    if not preview.likely_contradictions:
        lines.append("- none")
    else:
        for contradiction in sorted(
            preview.likely_contradictions,
            key=lambda item: (item.entity, item.relation, item.proposed_value),
        ):
            lines.extend(
                [
                    f"- {contradiction.entity} {contradiction.relation}",
                    f"  Existing: {contradiction.existing_value}",
                    f"  Proposed: {contradiction.proposed_value}",
                    f"  Reason: {contradiction.reason}",
                ]
            )
    lines.extend(["", "Scope Summary", *_format_mapping(preview.scope_summary)])
    return lines


def format_instruction_distillation_view(
    snapshot: InstructionDistillationSnapshot,
) -> list[str]:
    """Format instruction distillation state without promoting proposals."""
    lines = [
        "Instruction Distillation",
        "",
        "Sources",
    ]
    if not snapshot.sources:
        lines.append("- none")
    else:
        for source in sorted(snapshot.sources, key=lambda item: item.id):
            active = "active" if source.active else "inactive"
            lines.append(
                f"- {source.id} [{source.kind}/{active}] path={source.path} "
                f"owner={source.owner} trust={source.trust_boundary}"
            )

    lines.extend(["", "Snapshots"])
    if not snapshot.snapshots:
        lines.append("- none")
    else:
        for source_snapshot in sorted(snapshot.snapshots, key=lambda item: item.id):
            lines.append(
                f"- {source_snapshot.id} source={source_snapshot.source_id} "
                f"status={source_snapshot.hash_status} path={source_snapshot.path}"
            )

    lines.extend(["", "Provenance"])
    if not snapshot.provenance:
        lines.append("- none")
    else:
        for provenance in sorted(snapshot.provenance, key=lambda item: item.id):
            lines.append(
                f"- {provenance.id} source={provenance.source_id} "
                f"snapshot={provenance.snapshot_id or 'none'} "
                f"range={_format_line_range(provenance)}: {provenance.summary}"
            )

    lines.extend(["", "Distilled Proposals"])
    if not snapshot.proposals:
        lines.append("- none")
    else:
        for proposal in sorted(
            snapshot.proposals,
            key=lambda item: (item.promotion_status, item.id),
        ):
            lines.extend(
                [
                    f"- {proposal.id} [{proposal.promotion_status}/{proposal.category}]",
                    f"  Source: {proposal.source_id}",
                    f"  Snapshot: {proposal.snapshot_id or 'none'}",
                    f"  Active Constraint: {proposal.promoted_constraint_id or 'none'}",
                    f"  Provenance: {_join_or_none(proposal.provenance_ids)}",
                    f"  Evidence: {_join_or_none(proposal.evidence_ids)}",
                    f"  Contradictions: {_join_or_none(proposal.contradiction_ids)}",
                    f"  Statement: {proposal.statement}",
                ]
            )

    lines.extend(["", "Promotion Reviews"])
    if not snapshot.reviews:
        lines.append("- none")
    else:
        for review in sorted(snapshot.reviews, key=lambda item: (item.decision, item.id)):
            lines.extend(
                [
                    f"- {review.id} [{review.decision}] proposal={review.proposal_id}",
                    f"  Reviewer: {review.decided_by}",
                    f"  Active Constraint: {review.promoted_constraint_id or 'none'}",
                    f"  Policy: {review.policy_envelope_id or 'none'}",
                    f"  Receipts: {_join_or_none(review.receipt_ids)}",
                    f"  Handoffs: {_join_or_none(review.handoff_ids)}",
                    f"  Rationale: {review.rationale}",
                ]
            )

    return lines


def format_budget_quota_view(snapshot: BudgetQuotaSnapshot) -> list[str]:
    """Format budget and quota state without inventing missing data."""
    return [
        "Budget And Quota",
        "",
        "Configured Limits",
        *_format_mapping(snapshot.configured_limits),
        "",
        "Usage",
        *_format_mapping(snapshot.usage),
        "",
        "Missing Data",
        *_format_items(snapshot.missing),
        "",
        "Exceeded",
        *_format_items(snapshot.exceeded),
        "",
        "Notes",
        *_format_items(snapshot.notes),
    ]


def format_delegation_queue(delegations: list[HumanDelegationPoint]) -> list[str]:
    """Format a read-only human delegation queue."""
    lines = [f"Delegation Queue: {len(delegations)}", ""]
    if not delegations:
        return [*lines, "- none"]
    for delegation in sorted(delegations, key=lambda item: (item.status, item.id)):
        lines.extend(
            [
                f"- {delegation.id} [{delegation.status}/{delegation.kind}]",
                f"  Task: {delegation.task_id}",
                f"  Owner: {delegation.owner or 'unassigned'}",
                f"  Requested By: {delegation.requested_by}",
                f"  Decision: {delegation.requested_decision}",
                f"  Summary: {delegation.summary}",
                f"  Policy: {delegation.policy_envelope_id or 'none'}",
                f"  Receipts: {_join_or_none(delegation.receipt_ids)}",
                f"  Resolution: {delegation.resolution or 'none'}",
            ]
        )
    return lines


def format_evidence_assumption_view(
    evidence: list[EvidenceReference],
    assumptions: list[Assumption],
) -> list[str]:
    """Format evidence and assumptions while keeping assumptions distinct."""
    lines = [f"Evidence: {len(evidence)}", ""]
    lines.extend(_format_evidence(item) for item in sorted(evidence, key=lambda item: item.id))
    if not evidence:
        lines.append("- none")
    lines.extend(["", f"Assumptions: {len(assumptions)}", ""])
    lines.extend(
        _format_assumption(item) for item in sorted(assumptions, key=lambda item: item.id)
    )
    if not assumptions:
        lines.append("- none")
    return lines


def _format_evidence(evidence: EvidenceReference) -> str:
    captured = evidence.captured_at.isoformat() if evidence.captured_at else "unknown"
    return (
        f"- {evidence.id} [{evidence.kind}] source={evidence.source} "
        f"locator={evidence.locator} captured={captured}: {evidence.summary}"
    )


def _format_assumption(assumption: Assumption) -> str:
    evidence = _join_or_none(assumption.evidence_ids)
    return (
        f"- {assumption.id} [{assumption.status}] task={assumption.task_id} "
        f"confidence={assumption.confidence:.2f} evidence={evidence}: "
        f"{assumption.statement}"
    )


def format_contradiction_inbox(reports: list[ContradictionReport]) -> list[str]:
    """Format a read-only contradiction inbox."""
    lines = [f"Contradiction Inbox: {len(reports)}", ""]
    if not reports:
        return [*lines, "- none"]
    for report in sorted(reports, key=lambda item: (item.status, item.id)):
        lines.extend(
            [
                f"- {report.id} [{report.status}]",
                f"  Task: {report.task_id}",
                f"  Owner: {report.owner or 'unassigned'}",
                f"  Summary: {report.summary}",
                f"  Proposed Resolution: {report.proposed_resolution}",
                f"  Affected Artifacts: {_join_or_none(report.affected_artifacts)}",
                f"  Evidence: {_join_or_none(report.evidence_ids)}",
            ]
        )
    return lines


def format_receipt_viewer(receipt: CapabilityReceipt | PluginReceipt) -> list[str]:
    """Format a redacted capability or plugin receipt."""
    if isinstance(receipt, PluginReceipt):
        lines = [
            f"Plugin Receipt: {receipt.id}",
            f"Task: {receipt.task_id}",
            f"Actor: {receipt.actor}",
            f"Plugin: {receipt.plugin_descriptor_id}",
            f"Action: {receipt.action}",
            f"Trust Boundary: {receipt.trust_boundary}",
            f"Status: {receipt.result.status}",
            f"Summary: {receipt.result.summary}",
            f"Redacted: {receipt.redacted}",
            "",
            "Capability Grants",
            *_format_items(receipt.capability_grant_ids),
            "",
            "Evidence",
            *_format_items(receipt.evidence_ids),
            "",
            "Handoffs",
            *_format_items(receipt.handoff_ids),
        ]
        return lines
    return [
        f"Capability Receipt: {receipt.id}",
        f"Task: {receipt.task_id}",
        f"Actor: {receipt.actor}",
        f"Capability: {receipt.capability}",
        f"Target: {receipt.target}",
        f"Policy: {receipt.policy_profile}",
        f"Status: {receipt.result.status}",
        f"Reason: {receipt.reason}",
        f"Summary: {receipt.result.summary}",
        f"Redacted: {receipt.redacted}",
    ]


def format_handoff_viewer(handoff: Handoff) -> list[str]:
    """Format a redacted handoff viewer."""
    lines = [
        f"Handoff: {handoff.id}",
        f"Task: {handoff.task_id}",
        f"Project: {handoff.project_id}",
        f"Status: {handoff.status}",
        f"Agent: {handoff.agent}",
        f"Summary: {handoff.summary}",
        "",
        "Completed Actions",
        *_format_items(handoff.completed_actions),
        "",
        "Next Steps",
        *_format_items(handoff.next_steps),
        "",
        "Receipts",
        *_format_items(handoff.receipt_ids),
        "",
        "Evidence And Artifacts",
        *_format_items([*handoff.artifacts, *handoff.files_changed]),
        "",
        "Risks",
        *_format_items(handoff.risks),
        "",
        "Open Follow-Ups",
        *_format_items(
            [
                *handoff.context_debt,
                *handoff.assumptions,
                *handoff.contradictions_opened,
                *handoff.open_human_delegation_ids,
            ]
        ),
    ]
    return lines


def format_work_graph_explorer(export: WorkGraphExport) -> list[str]:
    """Format a deterministic work graph explorer view."""
    lines = [
        f"Work Graph: {export.id}",
        f"Task: {export.task_id or 'all'}",
        f"Nodes: {len(export.nodes)}",
        f"Edges: {len(export.edges)}",
        "",
        "Nodes",
    ]
    lines.extend(_format_node(node) for node in export.nodes)
    lines.append("")
    lines.append("Edges")
    lines.extend(_format_edge(edge) for edge in export.edges)
    return lines


def _format_node(node: WorkGraphNode) -> str:
    task = f" task={node.task_id}" if node.task_id else ""
    return f"- {node.id} [{node.type}]{task}: {node.label}"


def _format_edge(edge: WorkGraphEdge) -> str:
    metadata = _format_metadata(edge.metadata)
    suffix = f" {metadata}" if metadata else ""
    return f"- {edge.from_node} -[{edge.type}]-> {edge.to_node}{suffix}"


def _format_metadata(metadata: dict[str, object]) -> str:
    if not metadata:
        return ""
    parts = [f"{key}={metadata[key]}" for key in sorted(metadata)]
    return "(" + ", ".join(parts) + ")"


def _format_items(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]


def _format_mapping(items: Mapping[Any, float | int | str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {key}: {items[key]}" for key in sorted(items, key=str)]


def _format_memory_fact_references(
    items: Sequence[MemoryFactReference],
) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {_format_fact_reference(item)}" for item in items]


def _format_fact_reference(fact: FactValue | MemoryFactReference) -> str:
    return (
        f"{fact.entity} {fact.relation}={fact.value!r} "
        f"source={fact.source} scope={fact.scope} trust={fact.trust_class}"
    )


def _format_line_range(provenance: InstructionProvenance) -> str:
    if provenance.start_line is None or provenance.end_line is None:
        return "source"
    if provenance.start_line == provenance.end_line:
        return f"L{provenance.start_line}"
    return f"L{provenance.start_line}-L{provenance.end_line}"


def _quality_gate_state(snapshot: QualityGateSnapshot) -> str:
    if any(score.band == "poor" for score in snapshot.handoff_scores):
        return "blocked"
    if any(score.band == "poor" for score in snapshot.evidence_scores):
        return "blocked"
    if any(
        finding.blocking and finding.review_status != "adjudicated"
        for finding in snapshot.red_team_findings
    ):
        return "blocked"
    if any(
        finding.review_status == "reviewable"
        and finding.severity in {"high", "critical"}
        for finding in snapshot.critic_findings
    ):
        return "reviewable"
    if any(score.band == "adequate" for score in snapshot.handoff_scores):
        return "reviewable"
    if any(score.band == "adequate" for score in snapshot.evidence_scores):
        return "reviewable"
    return "clear"


def _format_score_components(score: HandoffQualityScore) -> str:
    return ", ".join(
        f"{component.name}={component.score:.2f}" for component in score.components
    )


def _join_or_none(items: list[str]) -> str:
    if not items:
        return "none"
    return ", ".join(items)
