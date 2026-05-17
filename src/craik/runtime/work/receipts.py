"""Receipt persistence and lookup helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypedDict

from craik.contracts.models import CapabilityReceipt
from craik.runtime.runners.runner_metadata import runner_metadata_from_receipt_metadata
from craik.runtime.store import LocalStore


class ReceiptLinks(TypedDict):
    """Normalized references connected to a capability receipt."""

    task_id: str
    policy_profile: str
    fail_open: bool
    policy_envelope_id: str | None
    handoff_ids: list[str]
    runner_metadata: dict[str, Any] | None


class ReceiptStoreError(RuntimeError):
    """Base error for receipt store failures."""


class ReceiptNotFoundError(ReceiptStoreError):
    """Raised when a requested receipt does not exist."""


class ReceiptStore:
    """Task-aware receipt queries over the local runtime store."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def record_receipt(self, receipt: CapabilityReceipt) -> CapabilityReceipt:
        """Persist a validated receipt and return the stored model."""
        self._store.put_receipt(receipt)
        return receipt

    def get_receipt(self, receipt_id: str) -> CapabilityReceipt | None:
        """Load one receipt by id."""
        return self._store.get_receipt(receipt_id)

    def require_receipt(self, receipt_id: str) -> CapabilityReceipt:
        """Load one receipt by id or raise a clear error."""
        receipt = self.get_receipt(receipt_id)
        if receipt is None:
            raise ReceiptNotFoundError(f"unknown receipt: {receipt_id}")
        return receipt

    def list_receipts(
        self,
        *,
        task_id: str | None = None,
        policy_id: str | None = None,
        handoff_id: str | None = None,
    ) -> list[CapabilityReceipt]:
        """List receipts with optional task, policy envelope, and handoff filters."""
        receipts: Iterable[CapabilityReceipt] = self._store.list_receipts()
        if task_id is not None:
            receipts = (receipt for receipt in receipts if receipt.task_id == task_id)
        if policy_id is not None:
            receipts = (
                receipt
                for receipt in receipts
                if receipt_links(receipt)["policy_envelope_id"] == policy_id
            )
        if handoff_id is not None:
            receipts = (
                receipt
                for receipt in receipts
                if handoff_id in receipt_links(receipt)["handoff_ids"]
            )
        return list(receipts)


def receipt_links(receipt: CapabilityReceipt) -> ReceiptLinks:
    """Return normalized linkage fields carried by a receipt."""
    metadata = receipt.result.metadata
    return {
        "task_id": receipt.task_id,
        "policy_profile": receipt.policy_profile,
        "fail_open": receipt.fail_open,
        "policy_envelope_id": _optional_string(metadata.get("policy_envelope_id")),
        "handoff_ids": _string_list(metadata.get("handoff_ids")),
        "runner_metadata": runner_metadata_from_receipt_metadata(metadata),
    }


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []
