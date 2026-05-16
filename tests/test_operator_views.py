from craik.contracts.models import (
    WorkGraphEdge,
    WorkGraphExport,
    WorkGraphNode,
)
from craik.runtime.operator_views import format_work_graph_explorer


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
