"""Read-only operator view formatters."""

from __future__ import annotations

from craik.contracts.models import Handoff, WorkGraphEdge, WorkGraphExport, WorkGraphNode


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
