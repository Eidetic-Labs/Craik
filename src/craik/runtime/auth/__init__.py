"""Authentication profile contracts and credential source protocols."""

from craik.runtime.auth.pool import (
    CREDENTIAL_POOL_SCHEMA_VERSION,
    CredentialPool,
    CredentialPoolConfig,
    CredentialPoolEntry,
    CredentialPoolError,
)
from craik.runtime.auth.profile import (
    AuthProfile,
    CredentialHealthStatus,
    CredentialKind,
    CredentialSource,
    CredentialStatus,
)
from craik.runtime.auth.store import (
    AUTH_PROFILES_SCHEMA_VERSION,
    AuthProfileNotFoundError,
    AuthProfileStore,
    AuthProfileStoreError,
)

__all__ = [
    "AUTH_PROFILES_SCHEMA_VERSION",
    "CREDENTIAL_POOL_SCHEMA_VERSION",
    "AuthProfile",
    "AuthProfileNotFoundError",
    "AuthProfileStore",
    "AuthProfileStoreError",
    "CredentialHealthStatus",
    "CredentialKind",
    "CredentialPool",
    "CredentialPoolConfig",
    "CredentialPoolEntry",
    "CredentialPoolError",
    "CredentialSource",
    "CredentialStatus",
]
