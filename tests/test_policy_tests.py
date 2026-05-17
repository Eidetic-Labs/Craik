from pathlib import Path

import pytest

from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy.policy_tests import PolicyTestHarness
from craik.runtime.store import LocalStore


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_policy_test_harness_passes_core_regressions(store: LocalStore) -> None:
    report = PolicyTestHarness(store).run()
    payload = report.to_payload()

    assert payload["schema"] == "craik.policy_test_report"
    assert payload["status"] == "passed"
    assert payload["summary"] == {"passed": 6, "failed": 0, "total": 6}
    assert {result["name"] for result in payload["results"]} == {
        "immutable_path_requires_override_and_grant",
        "memory_writes_become_proposals",
        "trusted_local_fail_open_receipts",
        "automation_fails_closed",
        "provider_runner_enforces_shell_grants",
        "redaction_receipts_logs_handoffs_case_files",
    }


def test_policy_test_harness_persists_memory_proposal(store: LocalStore) -> None:
    PolicyTestHarness(store).run()

    proposals = store.list_proposals()

    assert [proposal.id for proposal in proposals] == [
        "memprop_policy_test_repo_eidetic_labs_craik_craik_policy_test"
    ]
    assert proposals[0].status == "pending"
    assert proposals[0].requires_approval is True
