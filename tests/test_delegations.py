from pathlib import Path

import pytest
from pydantic import ValidationError

from craik.contracts.models import (
    Handoff,
    HumanDelegationPoint,
    ScopeChangeRequest,
    ScopeChangeResult,
    SelfAudit,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.reviewing.delegations import HumanDelegationManager, must_stop_for_human_decision
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _delegation(kind: str, delegation_id: str) -> HumanDelegationPoint:
    return HumanDelegationPoint(
        id=delegation_id,
        task_id="task_delegate",
        kind=kind,
        summary=f"{kind} needed.",
        requested_decision=f"Provide {kind}.",
        requested_by="agent:orchestrator",
        owner="user:maintainer",
        role_id="role_orchestrator",
        intent_lock_id="intent_delegate",
        policy_envelope_id="policy_delegate",
        created_at="2026-05-15T22:30:00Z",
    )


def _scope_request() -> ScopeChangeRequest:
    return ScopeChangeRequest(
        id="scope_change_add_files",
        task_id="task_delegate",
        intent_lock_id="intent_delegate",
        requested_by="agent:orchestrator",
        reason="The requested fix requires changing an out-of-scope file.",
        current_scope=["Update docs only."],
        proposed_scope=["Update docs and contract fixtures."],
        policy_envelope_id="policy_delegate",
        delegation_id="delegation_escalation",
        contradiction_ids=["contradiction_scope"],
        handoff_ids=["handoff_delegate"],
        created_at="2026-05-15T22:31:00Z",
    )


@pytest.mark.parametrize(
    ("kind", "delegation_id"),
    [
        ("approval", "delegation_approval"),
        ("clarification", "delegation_clarification"),
        ("escalation", "delegation_escalation"),
        ("ownership_transfer", "delegation_transfer"),
    ],
)
def test_human_delegation_points_stop_until_resolved(
    tmp_path: Path,
    kind: str,
    delegation_id: str,
) -> None:
    store = _store(tmp_path)
    try:
        manager = HumanDelegationManager(store)
        delegation = manager.open_delegation(_delegation(kind, delegation_id))

        assert must_stop_for_human_decision([delegation], []) is True

        resolved = manager.resolve_delegation(delegation.id, "Human decision recorded.")

        assert resolved.status == "resolved"
        assert resolved.resolution == "Human decision recorded."
        assert must_stop_for_human_decision([resolved], []) is False
        assert store.get_human_delegation(delegation.id) == resolved
    finally:
        store.close()


def test_rejected_scope_change_keeps_request_rejected(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        manager = HumanDelegationManager(store)
        request = manager.request_scope_change(_scope_request())

        assert must_stop_for_human_decision([], [request]) is True

        result = manager.decide_scope_change(
            ScopeChangeResult(
                id="scope_change_result_rejected",
                task_id=request.task_id,
                scope_change_request_id=request.id,
                decision="rejected",
                decided_by="user:maintainer",
                rationale="Keep the original documentation-only scope.",
                created_at="2026-05-15T22:32:00Z",
            )
        )

        updated = store.get_scope_change_request(request.id)
        assert result.decision == "rejected"
        assert updated.status == "rejected"
        assert must_stop_for_human_decision([], [updated]) is False
    finally:
        store.close()


def test_accepted_scope_change_links_updated_intent_lock(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        manager = HumanDelegationManager(store)
        request = manager.request_scope_change(_scope_request())

        result = manager.decide_scope_change(
            ScopeChangeResult(
                id="scope_change_result_accepted",
                task_id=request.task_id,
                scope_change_request_id=request.id,
                decision="accepted",
                decided_by="user:maintainer",
                rationale="Fixture updates are required to complete the contract work.",
                updated_intent_lock_id="intent_delegate_updated",
                policy_envelope_id="policy_delegate",
                handoff_ids=["handoff_delegate"],
                created_at="2026-05-15T22:33:00Z",
            )
        )

        updated = store.get_scope_change_request(request.id)
        assert result.decision == "accepted"
        assert result.updated_intent_lock_id == "intent_delegate_updated"
        assert updated.status == "accepted"
        assert store.get_scope_change_result(result.id) == result
    finally:
        store.close()


def test_handoff_surfaces_open_human_delegation_points() -> None:
    handoff = Handoff(
        id="handoff_delegate",
        task_id="task_delegate",
        project_id="project_delegate",
        agent="agent:orchestrator",
        status="blocked",
        summary="Blocked on human clarification.",
        self_audit=SelfAudit(
            schema_validated=True,
            redaction_reviewed=True,
            receipts_reviewed=True,
            assumptions_reviewed=True,
            validation_recorded=False,
            policy_exceptions_disclosed=True,
        ),
        open_human_delegation_ids=["delegation_clarification"],
        scope_change_request_ids=["scope_change_add_files"],
        created_at="2026-05-15T22:34:00Z",
    )

    assert handoff.open_human_delegation_ids == ["delegation_clarification"]
    assert handoff.scope_change_request_ids == ["scope_change_add_files"]


def test_resolved_delegation_requires_resolution_text() -> None:
    with pytest.raises(ValidationError, match="resolution text"):
        HumanDelegationPoint(
            id="delegation_invalid",
            task_id="task_delegate",
            kind="approval",
            status="resolved",
            summary="Approval was resolved.",
            requested_decision="Approve the action.",
            requested_by="agent:orchestrator",
            created_at="2026-05-15T22:35:00Z",
        )


def test_accepted_scope_change_requires_updated_intent_lock() -> None:
    with pytest.raises(ValidationError, match="updated_intent_lock_id"):
        ScopeChangeResult(
            id="scope_change_result_invalid",
            task_id="task_delegate",
            scope_change_request_id="scope_change_add_files",
            decision="accepted",
            decided_by="user:maintainer",
            rationale="Accepted but missing updated intent lock.",
            created_at="2026-05-15T22:36:00Z",
        )
