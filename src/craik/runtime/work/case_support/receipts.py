"""Case-file receipt builders."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import CapabilityReceipt, ReceiptResult, TaskRequest


def case_file_denial_receipt(
    *,
    task: TaskRequest,
    policy_id: str,
    reason: str,
) -> CapabilityReceipt:
    """Build a receipt for a denied case-file context read."""
    return CapabilityReceipt(
        id=f"receipt_{task.id}_case_file_path_denied",
        task_id=task.id,
        actor="agent:case-file",
        capability="case_file.read",
        target="case_file.discovery",
        policy_profile="strict",
        fail_open=False,
        reason=reason,
        result=ReceiptResult(
            status="denied",
            summary=reason,
            metadata={"policy_envelope_id": policy_id},
        ),
        redacted=True,
        created_at=datetime.now(UTC),
    )


__all__ = ["case_file_denial_receipt"]
