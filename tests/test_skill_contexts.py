import pytest
from pydantic import ValidationError

from craik.contracts.models import SkillInvocationContext
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore


def _context(**overrides: object) -> SkillInvocationContext:
    payload = {
        "id": "skill_context_docs_reconcile",
        "task_id": "task_docs_reconcile",
        "skill_package_id": "skill_docs_reconcile",
        "policy_envelope_id": "policy_docs_reconcile",
        "handoff_id": "handoff_docs_reconcile",
        "inputs": [
            {
                "schema_name": "craik.case_file",
                "contract_id": "case_docs_reconcile",
                "required": True,
                "summary": "Task case file supplied to the skill.",
                "evidence_ids": ["evidence_readme_status"],
            }
        ],
        "outputs": [
            {
                "schema_name": "craik.worker_result",
                "contract_id": "worker_result_docs_reconcile_verifier",
                "required": True,
                "produced": True,
                "summary": "Worker result produced by the skill.",
                "evidence_ids": ["evidence_worker_result_docs_reconcile"],
            }
        ],
        "omissions": [],
        "evidence_ids": ["evidence_readme_status"],
        "receipt_ids": ["receipt_runner_fixture"],
        "redacted": True,
        "created_at": "2026-05-16T15:50:00Z",
    }
    payload.update(overrides)
    return SkillInvocationContext.model_validate(payload)


def test_skill_invocation_context_round_trips_in_store(tmp_path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    try:
        context = _context()
        store.put_skill_invocation_context(context)

        assert store.get_skill_invocation_context(context.id) == context
        assert store.list_skill_invocation_contexts() == [context]
        assert context.redacted is True
    finally:
        store.close()


def test_skill_invocation_context_requires_inputs() -> None:
    with pytest.raises(ValidationError):
        _context(inputs=[])


def test_skill_invocation_context_requires_outputs_or_omissions() -> None:
    with pytest.raises(ValidationError, match="outputs or omissions"):
        _context(outputs=[], omissions=[])


def test_skill_invocation_context_tracks_omissions() -> None:
    context = _context(
        outputs=[
            {
                "schema_name": "craik.worker_result",
                "required": True,
                "produced": False,
                "summary": "Worker result was expected but not produced.",
            }
        ],
        omissions=[
            {
                "schema_name": "craik.worker_result",
                "reason": "The skill stopped before emitting structured output.",
                "impact": "A verifier needs to rerun or replace the skill output.",
                "severity": "high",
                "mitigation": "Create a context request before retrying.",
                "evidence_ids": ["evidence_readme_status"],
            }
        ],
    )

    assert context.omissions[0].schema_name == "craik.worker_result"


def test_skill_invocation_context_requires_policy_links_and_redaction() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        _context(policy_envelope_id="")

    with pytest.raises(ValidationError, match="must be redacted"):
        _context(redacted=False)
