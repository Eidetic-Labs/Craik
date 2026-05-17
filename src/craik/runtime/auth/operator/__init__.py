"""Operator identity primitives for Craik auth."""

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
    "OperatorSessionNotFoundError",
    "OperatorSession",
    "OperatorSessionStore",
    "OperatorSessionStoreError",
    "operator_session_store_owner_only",
]
