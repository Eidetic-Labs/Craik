"""Runner metadata snapshots for receipts and handoffs."""

from __future__ import annotations

from typing import Any, cast

from craik.contracts.models import RunnerMetadata
from craik.runtime.redaction import redact
from craik.runtime.runners import get_runner_capability_matrix


def runner_metadata_snapshot(runner: RunnerMetadata) -> dict[str, Any]:
    """Return a redacted stable metadata snapshot for adapter-produced work."""
    snapshot: dict[str, Any] = {
        "runner_id": runner.id,
        "runner_name": runner.name,
        "adapter": runner.adapter,
        "adapter_version": runner.adapter_version,
        "execution_mode": runner.mode,
        "capabilities": runner.capabilities,
        "runner_specific": runner.metadata,
    }
    try:
        matrix = get_runner_capability_matrix(runner.id)
    except KeyError:
        matrix = None
    if matrix is not None:
        snapshot["trust_profile"] = {
            "level": matrix.trust.level,
            "boundary": matrix.trust.boundary,
            "default_grant_posture": matrix.trust.default_grant_posture,
            "requires_receipts": matrix.trust.requires_receipts,
            "requires_redaction": matrix.trust.requires_redaction,
            "notes": matrix.trust.notes,
        }
        snapshot["capability_profile"] = [
            {
                "name": capability.name,
                "support": capability.support,
                "grant_required": capability.grant_required,
                "notes": capability.notes,
            }
            for capability in matrix.capabilities
        ]
        snapshot["policy_notes"] = matrix.policy_notes
    return cast(dict[str, Any], redact(snapshot).value)


def runner_metadata_from_receipt_metadata(metadata: dict[str, Any]) -> dict[str, Any] | None:
    """Read runner metadata from receipt result metadata when present."""
    value = metadata.get("runner_metadata")
    if isinstance(value, dict):
        return cast(dict[str, Any], redact(value).value)
    return None


def unique_runner_metadata(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return runner metadata snapshots in first-seen order without duplicates."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for snapshot in snapshots:
        key = "|".join(
            str(snapshot.get(part, ""))
            for part in ("runner_id", "adapter", "adapter_version", "execution_mode")
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(snapshot)
    return unique
