"""Operator identity primitives for Craik auth."""

from craik.runtime.auth.operator.context import (
    OPERATOR_REQUIRED_METADATA_KEY,
    active_operator_session,
    bind_operator_metadata,
    operator_identity_required,
)
from craik.runtime.auth.operator.oidc import (
    OIDCAuthenticationError,
    OIDCAuthenticator,
    OIDCConfig,
)
from craik.runtime.auth.operator.session import OperatorSession
from craik.runtime.auth.operator.store import (
    OPERATOR_SESSION_SCHEMA_VERSION,
    OperatorSessionNotFoundError,
    OperatorSessionStore,
    OperatorSessionStoreError,
    operator_session_store_owner_only,
)

__all__ = [
    "OIDCAuthenticationError",
    "OIDCAuthenticator",
    "OIDCConfig",
    "OPERATOR_SESSION_SCHEMA_VERSION",
    "OPERATOR_REQUIRED_METADATA_KEY",
    "OperatorSessionNotFoundError",
    "OperatorSession",
    "OperatorSessionStore",
    "OperatorSessionStoreError",
    "active_operator_session",
    "bind_operator_metadata",
    "operator_identity_required",
    "operator_session_store_owner_only",
]
