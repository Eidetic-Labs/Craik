from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import CapabilityReceipt, PolicyProfile, ReceiptResult
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore, UnredactedSecretError
from craik.runtime.work.receipts import ReceiptNotFoundError, ReceiptStore, receipt_links


@pytest.fixture
def receipt_store(tmp_path: Path) -> Iterator[ReceiptStore]:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    try:
        yield ReceiptStore(store)
    finally:
        store.close()


def test_record_and_require_receipt(receipt_store: ReceiptStore) -> None:
    receipt = _receipt("receipt_build", task_id="task_docs")

    assert receipt_store.record_receipt(receipt) == receipt

    assert receipt_store.require_receipt("receipt_build") == receipt


def test_list_receipts_filters_by_task_policy_and_handoff(receipt_store: ReceiptStore) -> None:
    linked = _receipt(
        "receipt_docs",
        task_id="task_docs",
        metadata={
            "policy_envelope_id": "policy_docs",
            "handoff_ids": ["handoff_docs"],
        },
    )
    other = _receipt(
        "receipt_other",
        task_id="task_other",
        metadata={
            "policy_envelope_id": "policy_other",
            "handoff_ids": ["handoff_other"],
        },
    )
    receipt_store.record_receipt(linked)
    receipt_store.record_receipt(other)

    assert receipt_store.list_receipts(task_id="task_docs") == [linked]
    assert receipt_store.list_receipts(policy_id="policy_docs") == [linked]
    assert receipt_store.list_receipts(handoff_id="handoff_docs") == [linked]
    assert receipt_store.list_receipts(task_id="task_docs", policy_id="policy_docs") == [linked]
    assert receipt_store.list_receipts(task_id="task_docs", policy_id="policy_other") == []


def test_receipt_links_include_policy_profile_and_fail_open() -> None:
    receipt = _receipt(
        "receipt_fail_open",
        task_id="task_docs",
        policy_profile="trusted-local",
        fail_open=True,
        metadata={
            "policy_envelope_id": "policy_docs",
            "handoff_ids": ["handoff_docs"],
        },
    )

    assert receipt_links(receipt) == {
        "task_id": "task_docs",
        "policy_profile": "trusted-local",
        "fail_open": True,
        "policy_envelope_id": "policy_docs",
        "handoff_ids": ["handoff_docs"],
        "runner_metadata": None,
    }


def test_receipt_links_include_redacted_runner_metadata() -> None:
    receipt = _receipt(
        "receipt_runner",
        task_id="task_docs",
        metadata={
            "runner_metadata": {
                "runner_id": "codex",
                "adapter": "codex",
                "adapter_version": "0.2.0-preview",
                "execution_mode": "fixture",
                "runner_specific": {"api_token": "redaction-fixture-value"},
            },
        },
    )

    links = receipt_links(receipt)

    assert links["runner_metadata"] == {
        "runner_id": "codex",
        "adapter": "codex",
        "adapter_version": "0.2.0-preview",
        "execution_mode": "fixture",
        "runner_specific": {"api_token": "[REDACTED]"},
    }


def test_missing_receipt_raises_clear_error(receipt_store: ReceiptStore) -> None:
    with pytest.raises(ReceiptNotFoundError, match="unknown receipt: receipt_missing"):
        receipt_store.require_receipt("receipt_missing")


def test_unredacted_secret_receipt_is_rejected(receipt_store: ReceiptStore) -> None:
    receipt = _receipt(
        "receipt_secret",
        task_id="task_docs",
        metadata={"api_token": "redaction-fixture-value"},
    )

    with pytest.raises(UnredactedSecretError, match="unredacted secret material"):
        receipt_store.record_receipt(receipt)


def _receipt(
    receipt_id: str,
    *,
    task_id: str,
    policy_profile: PolicyProfile = "strict",
    fail_open: bool = False,
    metadata: dict[str, object] | None = None,
) -> CapabilityReceipt:
    return CapabilityReceipt(
        id=receipt_id,
        task_id=task_id,
        actor="agent:codex",
        capability="shell.test",
        target="uv run pytest",
        policy_profile=policy_profile,
        fail_open=fail_open,
        reason="Validate receipt behavior.",
        result=ReceiptResult(
            status="passed",
            summary="Command completed.",
            metadata=metadata or {},
        ),
        redacted=True,
        created_at=datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    )
