"""Bridge work graph exports to visual workspace records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field

from craik.contracts.models import CraikModel, WorkGraphExport
from craik.runtime.policy.redaction import redact


class VisualWorkspaceNode(CraikModel):
    """Visual node derived from a work graph node."""

    id: str
    source_node_id: str
    type: str
    label: str
    x: int
    y: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisualWorkspaceEdge(CraikModel):
    """Visual edge derived from a work graph edge."""

    id: str
    source_edge_id: str
    type: str
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkGraphVisualWorkspace(CraikModel):
    """Portable visual workspace projection of a work graph export."""

    schema_: Literal["craik.work_graph_visual_workspace"] = Field(
        default="craik.work_graph_visual_workspace",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    source_graph_id: str
    task_id: str | None = None
    nodes: list[VisualWorkspaceNode] = Field(default_factory=list)
    edges: list[VisualWorkspaceEdge] = Field(default_factory=list)
    policy_envelope_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    redacted_paths: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def work_graph_visual_workspace(
    *,
    workspace_id: str,
    graph: WorkGraphExport,
    created_at: datetime | None = None,
) -> WorkGraphVisualWorkspace:
    """Build a deterministic visual workspace projection from a work graph export."""
    redacted_paths: list[str] = []
    nodes = [
        _visual_node(index=index, node=node, redacted_paths=redacted_paths)
        for index, node in enumerate(graph.nodes)
    ]
    source_to_visual = {node.source_node_id: node.id for node in nodes}
    edges = [
        _visual_edge(edge=edge, source_to_visual=source_to_visual, redacted_paths=redacted_paths)
        for edge in graph.edges
        if edge.from_node in source_to_visual and edge.to_node in source_to_visual
    ]

    return WorkGraphVisualWorkspace(
        id=workspace_id,
        source_graph_id=graph.id,
        task_id=graph.task_id,
        nodes=nodes,
        edges=edges,
        policy_envelope_ids=_metadata_ids(graph, "policy_envelope_id"),
        evidence_ids=_typed_ids(graph, "evidence"),
        receipt_ids=_typed_ids(graph, "receipt"),
        redacted_paths=sorted(set(redacted_paths)),
        created_at=created_at or datetime.now(UTC),
    )


def _visual_node(index: int, node: Any, redacted_paths: list[str]) -> VisualWorkspaceNode:
    column = index % 4
    row = index // 4
    return VisualWorkspaceNode(
        id=f"visual_node_{_slug(node.id)}",
        source_node_id=node.id,
        type=node.type,
        label=str(_safe_value(node.label, redacted_paths)),
        x=column * 320,
        y=row * 180,
        metadata=_safe_metadata(node.metadata, redacted_paths),
    )


def _visual_edge(
    *,
    edge: Any,
    source_to_visual: dict[str, str],
    redacted_paths: list[str],
) -> VisualWorkspaceEdge:
    return VisualWorkspaceEdge(
        id=f"visual_edge_{_slug(edge.id)}",
        source_edge_id=edge.id,
        type=edge.type,
        **{
            "from": source_to_visual[edge.from_node],
            "to": source_to_visual[edge.to_node],
        },
        metadata=_safe_metadata(edge.metadata, redacted_paths),
    )


def _safe_metadata(metadata: dict[str, Any], redacted_paths: list[str]) -> dict[str, Any]:
    safe = _safe_value(metadata, redacted_paths)
    if isinstance(safe, dict):
        return safe
    return {}


def _safe_value(value: Any, redacted_paths: list[str]) -> Any:
    redacted = redact(value)
    redacted_paths.extend(redacted.redacted_paths)
    return redacted.value


def _metadata_ids(graph: WorkGraphExport, key: str) -> list[str]:
    ids: set[str] = set()
    for node in graph.nodes:
        value = node.metadata.get(key)
        if isinstance(value, str) and value:
            ids.add(value)
    for edge in graph.edges:
        value = edge.metadata.get(key)
        if isinstance(value, str) and value:
            ids.add(value)
    return sorted(ids)


def _typed_ids(graph: WorkGraphExport, node_type: str) -> list[str]:
    prefix = f"{node_type}:"
    return sorted(
        node.id.removeprefix(prefix) for node in graph.nodes if node.id.startswith(prefix)
    )


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
