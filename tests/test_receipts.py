import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import CapabilityReceipt, PolicyProfile, ReceiptResult
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore, LocalStoreCorruptError, UnredactedSecretError
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

    recorded = receipt_store.record_receipt(receipt)

    assert recorded.id == receipt.id
    assert recorded.self_hash
    assert receipt_store.require_receipt("receipt_build") == recorded


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


def test_receipt_hash_changes_with_payload() -> None:
    first = _receipt("receipt_hash", task_id="task_docs")
    second = _receipt(
        "receipt_hash",
        task_id="task_docs",
        metadata={"detail": "changed"},
    )

    assert first.self_hash
    assert second.self_hash
    assert first.self_hash != second.self_hash


def test_receipt_store_links_receipts_with_previous_hash(tmp_path: Path) -> None:
    store = _local_store(tmp_path)
    try:
        first = _receipt("receipt_first", task_id="task_docs")
        second = _receipt("receipt_second", task_id="task_docs")

        store.put_receipt(first)
        stored_first = store.get_receipt("receipt_first")
        assert stored_first is not None
        store.put_receipt(second)
        stored_second = store.get_receipt("receipt_second")

        assert stored_second is not None
        assert stored_second.previous_receipt_hash == stored_first.self_hash
    finally:
        store.close()


def test_receipt_store_rejects_tampered_receipt_payload(tmp_path: Path) -> None:
    store = _local_store(tmp_path)
    try:
        receipt = _receipt("receipt_tamper", task_id="task_docs")
        store.put_receipt(receipt)
        stored = store.get_receipt("receipt_tamper")
        assert stored is not None
        payload = stored.model_dump(mode="json", by_alias=True)
        payload["reason"] = "Tampered reason."
        with store.transaction() as connection:
            connection.execute(
                """
                UPDATE records
                SET payload_json = ?
                WHERE kind = ? AND id = ?
                """,
                (
                    json.dumps(payload, sort_keys=True, separators=(",", ":")),
                    "receipts",
                    "receipt_tamper",
                ),
            )

        with pytest.raises(LocalStoreCorruptError, match="failed validation"):
            store.get_receipt("receipt_tamper")
    finally:
        store.close()


def test_receipt_store_rejects_broken_receipt_chain(tmp_path: Path) -> None:
    store = _local_store(tmp_path)
    try:
        store.put_receipt(_receipt("receipt_first", task_id="task_docs"))
        store.put_receipt(_receipt("receipt_second", task_id="task_docs"))
        second = store.get_receipt("receipt_second")
        assert second is not None
        payload = second.model_dump(mode="json", by_alias=True)
        payload["previous_receipt_hash"] = "broken"
        payload["self_hash"] = ""
        payload = CapabilityReceipt.model_validate(payload).model_dump(
            mode="json",
            by_alias=True,
        )
        with store.transaction() as connection:
            connection.execute(
                """
                UPDATE records
                SET payload_json = ?
                WHERE kind = ? AND id = ?
                """,
                (
                    json.dumps(payload, sort_keys=True, separators=(",", ":")),
                    "receipts",
                    "receipt_second",
                ),
            )

        with pytest.raises(LocalStoreCorruptError, match="receipt chain"):
            store.list_receipts()
    finally:
        store.close()


def test_receipt_store_preserves_hash_history_across_upserts(tmp_path: Path) -> None:
    store = _local_store(tmp_path)
    try:
        store.put_receipt(_receipt("receipt_first", task_id="task_docs"))
        original_second = store.put_receipt(_receipt("receipt_second", task_id="task_docs"))
        store.put_receipt(
            _receipt(
                "receipt_second",
                task_id="task_docs",
                metadata={"updated": True},
            )
        )
        store.put_receipt(_receipt("receipt_third", task_id="task_docs"))

        receipts = store.list_receipts()
        updated_second = store.get_receipt("receipt_second")
        assert updated_second is not None
        assert original_second.self_hash in updated_second.result.metadata[
            "receipt_hash_history"
        ]
        assert len(receipts) == 3
    finally:
        store.close()


def _local_store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


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
