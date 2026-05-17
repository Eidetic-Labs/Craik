from pathlib import Path

from craik.contracts.models import (
    CaseFile,
    ContradictionReport,
    Handoff,
    ProjectProfile,
    PromotedInstructionConstraint,
    SelfAudit,
    TaskRequest,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore
from craik.runtime.work.recovery import RecoveryBuilder, render_recovery_markdown


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _project() -> ProjectProfile:
    return ProjectProfile(
        id="project_recovery",
        name="Recovery Fixture",
        repo={"type": "git", "local_path": "/workspace/recovery"},
        memory={"backend": "local", "scope": "team"},
    )


def _task() -> TaskRequest:
    return TaskRequest(
        id="task_recovery",
        title="Recovery task",
        objective="Verify recovery mode.",
        project_id="project_recovery",
        requested_by="user:maintainer",
        mode="implement",
        created_at="2026-05-15T22:00:00Z",
    )


def _audit() -> SelfAudit:
    return SelfAudit(
        schema_validated=True,
        redaction_reviewed=True,
        receipts_reviewed=True,
        assumptions_reviewed=True,
        validation_recorded=True,
        policy_exceptions_disclosed=True,
    )


def _handoff(handoff_id: str, created_at: str) -> Handoff:
    return Handoff(
        id=handoff_id,
        task_id="task_recovery",
        project_id="project_recovery",
        agent="agent:fixture",
        status="completed",
        summary=f"Fixture handoff {handoff_id}.",
        self_audit=_audit(),
        created_at=created_at,
    )


def _case_file() -> CaseFile:
    return CaseFile(
        id="case_recovery",
        task_id="task_recovery",
        objective="Verify recovery mode.",
        policy_envelope_id="policy_recovery",
    )


def test_recovery_reports_missing_prior_context(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        store.put_project(_project())
        store.put_task(_task())
        session = RecoveryBuilder(store).build(
            project_id="project_recovery",
            task_id="task_recovery",
        )
        delta = store.get_run_delta(session.run_delta_id)

        assert session.status == "missing_prior_context"
        assert session.required_actions == [
            "Rebuild a case file and establish a handoff before resuming."
        ]
        assert delta is not None
        assert delta.changes[0].entity_id == "missing_handoff"
    finally:
        store.close()


def test_recovery_reports_clean_resume(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        store.put_project(_project())
        store.put_task(_task())
        store.put_case_file(_case_file())
        store.put_handoff(_handoff("handoff_recovery", "2026-05-15T22:30:00Z"))

        session = RecoveryBuilder(store).build(
            project_id="project_recovery",
            task_id="task_recovery",
        )
        delta = store.get_run_delta(session.run_delta_id)

        assert session.status == "clean_resume"
        assert session.required_actions == []
        assert session.handoff_ids == ["handoff_recovery"]
        assert session.case_file_ids == ["case_recovery"]
        assert delta is not None
        assert render_recovery_markdown(session, delta).startswith(
            "# Recovery Session: recovery_session_task_recovery"
        )
    finally:
        store.close()


def test_recovery_reports_changed_state(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        store.put_project(_project())
        store.put_task(_task())
        store.put_handoff(_handoff("handoff_previous", "2026-05-15T22:20:00Z"))
        store.put_handoff(_handoff("handoff_current", "2026-05-15T22:40:00Z"))
        store.put_contradiction(
            ContradictionReport(
                id="contradiction_recovery",
                task_id="task_recovery",
                facts=["old fact", "new fact"],
                summary="Facts conflict during recovery.",
                status="open",
            )
        )
        store.put_promoted_instruction_constraint(
            PromotedInstructionConstraint(
                id="constraint_recovery",
                project_id="project_recovery",
                proposal_id="proposal_recovery",
                source_id="source_recovery",
                snapshot_id="snapshot_recovery",
                category="instruction",
                statement="Review recovery deltas before resuming.",
                provenance_ids=["provenance_recovery"],
                created_at="2026-05-15T22:35:00Z",
            )
        )

        session = RecoveryBuilder(store).build(
            project_id="project_recovery",
            task_id="task_recovery",
        )
        delta = store.get_run_delta(session.run_delta_id)

        assert session.status == "changed_state"
        assert session.contradiction_ids == ["contradiction_recovery"]
        assert session.active_instruction_constraint_ids == ["constraint_recovery"]
        assert session.required_actions == [
            "Review open contradictions before promoting new facts.",
            "Apply active instruction constraints to the resumed runtime context.",
        ]
        assert delta is not None
        assert delta.previous_handoff_id == "handoff_previous"
        assert delta.current_handoff_id == "handoff_current"
    finally:
        store.close()
