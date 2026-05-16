"""Read-only operator view formatters."""

from __future__ import annotations

from craik.contracts.models import WorkGraphEdge, WorkGraphExport, WorkGraphNode


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
