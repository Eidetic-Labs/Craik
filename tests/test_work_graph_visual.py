from datetime import UTC, datetime

from craik.contracts.models import WorkGraphEdge, WorkGraphExport, WorkGraphNode
from craik.runtime.work_graph_visual import work_graph_visual_workspace

NOW = datetime(2026, 5, 16, 19, 5, tzinfo=UTC)


def test_work_graph_visual_workspace_preserves_source_links() -> None:
    workspace = work_graph_visual_workspace(
        workspace_id="visual_workspace_docs_reconcile",
        graph=_graph(),
        created_at=NOW,
    )
    payload = workspace.model_dump(by_alias=True, mode="json")

    assert payload["schema"] == "craik.work_graph_visual_workspace"
    assert payload["source_graph_id"] == "graph_task_docs_reconcile"
    assert payload["task_id"] == "task_docs_reconcile"
    assert payload["nodes"][0]["source_node_id"] == "task:task_docs_reconcile"
    assert payload["nodes"][1]["source_node_id"] == "evidence:evidence_docs"
    assert payload["edges"][0]["source_edge_id"] == "edge_task_evidence"
    assert payload["edges"][0]["from"] == "visual_node_task_task_docs_reconcile"
    assert payload["edges"][0]["to"] == "visual_node_evidence_evidence_docs"
    assert payload["evidence_ids"] == ["evidence_docs"]
    assert payload["receipt_ids"] == ["receipt_docs"]
    assert payload["policy_envelope_ids"] == ["policy_docs"]
    assert payload["created_at"] == "2026-05-16T19:05:00Z"


def test_work_graph_visual_workspace_uses_deterministic_layout() -> None:
    workspace = work_graph_visual_workspace(
        workspace_id="visual_workspace_docs_reconcile",
        graph=_graph(),
        created_at=NOW,
    )

    assert [(node.x, node.y) for node in workspace.nodes] == [(0, 0), (320, 0), (640, 0)]


def test_work_graph_visual_workspace_redacts_metadata() -> None:
    graph = _graph(
        nodes=[
            WorkGraphNode(
                id="task:task_docs_reconcile",
                type="task",
                label="token=redactionfixture123",
                task_id="task_docs_reconcile",
                metadata={"api_token": "redaction-fixture-value"},
            )
        ],
        edges=[],
    )

    workspace = work_graph_visual_workspace(
        workspace_id="visual_workspace_docs_reconcile",
        graph=graph,
        created_at=NOW,
    )

    assert workspace.nodes[0].label == "token=[REDACTED]"
    assert workspace.nodes[0].metadata["api_token"] == "[REDACTED]"
    assert workspace.redacted_paths


def _graph(
    *,
    nodes: list[WorkGraphNode] | None = None,
    edges: list[WorkGraphEdge] | None = None,
) -> WorkGraphExport:
    return WorkGraphExport(
        id="graph_task_docs_reconcile",
        task_id="task_docs_reconcile",
        nodes=nodes
        or [
            WorkGraphNode(
                id="task:task_docs_reconcile",
                type="task",
                label="Docs reconcile",
                task_id="task_docs_reconcile",
                metadata={"policy_envelope_id": "policy_docs"},
            ),
            WorkGraphNode(
                id="evidence:evidence_docs",
                type="evidence",
                label="Docs evidence",
                task_id="task_docs_reconcile",
            ),
            WorkGraphNode(
                id="receipt:receipt_docs",
                type="receipt",
                label="Docs receipt",
                task_id="task_docs_reconcile",
            ),
        ],
        edges=edges
        or [
            WorkGraphEdge(
                id="edge_task_evidence",
                type="supported_by",
                **{"from": "task:task_docs_reconcile", "to": "evidence:evidence_docs"},
            ),
            WorkGraphEdge(
                id="edge_task_receipt",
                type="has_receipt",
                **{"from": "task:task_docs_reconcile", "to": "receipt:receipt_docs"},
            ),
        ],
        created_at=NOW,
    )
