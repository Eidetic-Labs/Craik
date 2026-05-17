from datetime import datetime

import pytest
from pydantic import ValidationError

from craik.contracts.models import Assumption, CaseFile, ContextDebtRecord
from craik.runtime.work.context_debt import (
    carry_forward_context_debt,
    context_debt_summaries,
    records_from_case_file,
    resolve_context_debt,
)


def _case_file() -> CaseFile:
    return CaseFile(
        id="case_context_debt",
        task_id="task_context_debt",
        objective="Track context debt.",
        policy_envelope_id="policy_context_debt",
        github_state={"status": "not_loaded"},
        context_budget={
            "docs_omitted": ["docs/large.md"],
            "docs_excluded": [{"path": "docs/private.md"}],
            "active_instruction_constraints": [{"id": "constraint_runtime"}],
        },
        assumptions=[
            Assumption(
                id="assumption_context_debt",
                task_id="task_context_debt",
                statement="External release state may have changed.",
                rationale="No external state was loaded.",
                evidence_ids=["evidence_context_debt"],
                confidence=0.5,
                status="open",
            )
        ],
    )


def test_context_debt_records_are_created_from_case_file() -> None:
    records = records_from_case_file(
        _case_file(),
        task_id="task_context_debt",
        project_id="project_context_debt",
        handoff_id="handoff_context_debt",
        owner="agent:codex",
        created_at=datetime.fromisoformat("2026-05-16T09:10:00+00:00"),
    )

    kinds = [record.kind for record in records]

    assert kinds == [
        "omitted_doc",
        "excluded_doc",
        "missing_external_state",
        "missing_memory_facts",
        "active_instruction_constraint",
        "unresolved_assumption",
    ]
    assert all(record.next_action for record in records)
    assert records[0].owner == "agent:codex"
    assert "GitHub state was not loaded" in context_debt_summaries(records)[2]


def test_context_debt_can_be_carried_forward_and_resolved() -> None:
    records = records_from_case_file(_case_file(), task_id="task_context_debt")

    carried = carry_forward_context_debt(records, handoff_id="handoff_next")
    resolved = resolve_context_debt(carried[0])

    assert carried[0].status == "carried_forward"
    assert carried[0].handoff_id == "handoff_next"
    assert carried[0].id.endswith("_carried_handoff_next")
    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None


def test_open_context_debt_requires_next_action() -> None:
    with pytest.raises(ValidationError, match="open context debt requires"):
        ContextDebtRecord(
            id="context_debt_missing_action",
            task_id="task_context_debt",
            kind="missing_external_state",
            summary="GitHub state is missing.",
            created_at="2026-05-16T09:10:00Z",
        )


def test_resolved_context_debt_requires_resolved_at() -> None:
    with pytest.raises(ValidationError, match="resolved context debt requires"):
        ContextDebtRecord(
            id="context_debt_bad_resolved",
            task_id="task_context_debt",
            kind="missing_external_state",
            status="resolved",
            summary="GitHub state is refreshed.",
            created_at="2026-05-16T09:10:00Z",
        )
