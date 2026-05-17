"""Human delegation and scope-change lifecycle helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import (
    HumanDelegationPoint,
    ScopeChangeRequest,
    ScopeChangeResult,
)
from craik.runtime.store import LocalStore


class HumanDelegationManager:
    """Persist human delegation points and scope-change decisions."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def open_delegation(self, delegation: HumanDelegationPoint) -> HumanDelegationPoint:
        """Persist an open human delegation point."""
        self._store.put_human_delegation(delegation)
        return delegation

    def resolve_delegation(self, delegation_id: str, resolution: str) -> HumanDelegationPoint:
        """Resolve an open delegation point with human-provided resolution text."""
        delegation = self._store.get_human_delegation(delegation_id)
        if delegation is None:
            raise HumanDelegationNotFoundError(f"unknown human delegation: {delegation_id}")
        resolved = delegation.model_copy(
            update={
                "status": "resolved",
                "resolution": resolution,
                "resolved_at": datetime.now(UTC),
            }
        )
        self._store.put_human_delegation(resolved)
        return resolved

    def request_scope_change(self, request: ScopeChangeRequest) -> ScopeChangeRequest:
        """Persist a pending scope-change request."""
        self._store.put_scope_change_request(request)
        return request

    def decide_scope_change(self, result: ScopeChangeResult) -> ScopeChangeResult:
        """Persist a human scope-change decision and update the request status."""
        self._store.put_scope_change_result(result)
        request = self._store.get_scope_change_request(result.scope_change_request_id)
        if request is not None:
            self._store.put_scope_change_request(
                request.model_copy(update={"status": result.decision})
            )
        return result


class HumanDelegationNotFoundError(RuntimeError):
    """Raised when a human delegation point cannot be found."""


def must_stop_for_human_decision(
    delegations: list[HumanDelegationPoint],
    scope_changes: list[ScopeChangeRequest],
) -> bool:
    """Return true when open human input should stop autonomous agent work."""
    return any(delegation.status == "open" for delegation in delegations) or any(
        request.status == "pending" for request in scope_changes
    )
