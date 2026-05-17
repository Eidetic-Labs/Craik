"""Provider-call operator identity context."""

from __future__ import annotations

from craik.runtime.auth.operator.session import OperatorSession
from craik.runtime.auth.operator.store import OperatorSessionNotFoundError, OperatorSessionStore
from craik.runtime.paths import resolve_craik_home

OPERATOR_REQUIRED_METADATA_KEY = "operator_identity_required"


def active_operator_session() -> OperatorSession | None:
    """Return the active operator session without creating local auth state."""
    store = OperatorSessionStore(resolve_craik_home())
    if not store.path.exists():
        return None
    try:
        return store.get()
    except OperatorSessionNotFoundError:
        return None


def operator_identity_required(metadata: dict[str, object]) -> bool:
    """Return whether request metadata requires an active operator session."""
    return bool(metadata.get(OPERATOR_REQUIRED_METADATA_KEY))


def bind_operator_metadata(
    metadata: dict[str, object],
    session: OperatorSession,
) -> dict[str, object]:
    """Return metadata enriched with the active operator identity."""
    updated = dict(metadata)
    updated["operator_subject"] = session.subject
    updated["operator_issuer"] = session.issuer
    updated["operator_email"] = session.email
    updated["operator_groups"] = list(session.groups)
    return updated
