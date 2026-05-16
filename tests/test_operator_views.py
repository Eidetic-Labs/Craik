from craik.contracts.models import (
    Handoff,
    WorkGraphEdge,
    WorkGraphExport,
    WorkGraphNode,
)
from craik.runtime.operator_views import format_handoff_viewer, format_work_graph_explorer


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
