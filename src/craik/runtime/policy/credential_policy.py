"""Credential-bound policy checks."""

from __future__ import annotations

from fnmatch import fnmatchcase

from craik.contracts.models import PolicyEnvelope
from craik.runtime.auth import CredentialKind
from craik.runtime.policy.policy import GrantDecision


def check_credential_policy(
    *,
    policy: PolicyEnvelope,
    auth_profile_id: str,
    auth_kind: CredentialKind,
) -> GrantDecision:
    """Evaluate policy-level credential profile and kind requirements."""
    capability = "credential.use"
    metadata = _credential_policy_metadata(policy)
    if not metadata:
        return GrantDecision(
            allowed=True,
            capability=capability,
            target=auth_profile_id,
            reason="credential use is not restricted by policy",
        )
    if not _credential_kind_allowed(policy.allowed_credential_kinds, auth_kind):
        return GrantDecision(
            allowed=False,
            capability=capability,
            target=auth_profile_id,
            reason="credential kind denied by policy",
            receipt_metadata={
                **metadata,
                "auth_profile_id": auth_profile_id,
                "auth_kind": auth_kind.value,
            },
        )
    if not _credential_profile_allowed(policy.allowed_credential_profiles, auth_profile_id):
        return GrantDecision(
            allowed=False,
            capability=capability,
            target=auth_profile_id,
            reason="credential profile denied by policy",
            receipt_metadata={
                **metadata,
                "auth_profile_id": auth_profile_id,
                "auth_kind": auth_kind.value,
            },
        )
    return GrantDecision(
        allowed=True,
        capability=capability,
        target=auth_profile_id,
        reason="credential use allowed by policy",
        receipt_metadata={
            **metadata,
            "auth_profile_id": auth_profile_id,
            "auth_kind": auth_kind.value,
        },
    )


def credential_policy_metadata(policy: PolicyEnvelope) -> dict[str, object]:
    """Return provider request metadata that preserves credential policy constraints."""
    return _credential_policy_metadata(policy)


def _credential_policy_metadata(policy: PolicyEnvelope) -> dict[str, object]:
    if policy.allowed_credential_kinds is None and policy.allowed_credential_profiles is None:
        return {}
    return {
        "policy_id": policy.id,
        "allowed_credential_kinds": list(policy.allowed_credential_kinds or []),
        "allowed_credential_profiles": list(policy.allowed_credential_profiles or []),
    }


def _credential_kind_allowed(
    allowed_kinds: list[str] | None,
    auth_kind: CredentialKind,
) -> bool:
    if allowed_kinds is None:
        return True
    return auth_kind.value in allowed_kinds


def _credential_profile_allowed(
    allowed_profiles: list[str] | None,
    auth_profile_id: str,
) -> bool:
    if allowed_profiles is None:
        return True
    return any(fnmatchcase(auth_profile_id, pattern) for pattern in allowed_profiles)
