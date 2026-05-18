"""Policy profile definitions and envelope generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityReceipt,
    DocsProfile,
    PolicyEnvelope,
    PolicyProfile,
    ReceiptResult,
)
from craik.runtime.policy.redaction import redact

STRICT_ALLOWED_CAPABILITIES = ("repo.read", "memory.read", "receipt.write")
STRICT_DENIED_CAPABILITIES = (
    "repo.write",
    "repo.write.immutable",
    "shell.execute",
    "git.mutate",
    "github.write",
    "memory.write",
)
STRICT_APPROVAL_REQUIRED = (
    "repo.write.docs",
    "shell.test",
    "github.create_pr",
    "memory.write",
)

TRUSTED_LOCAL_ALLOWED_CAPABILITIES = (
    "repo.read",
    "repo.write.local",
    "shell.local",
    "memory.read",
    "memory.propose",
    "receipt.write",
)
TRUSTED_LOCAL_DENIED_CAPABILITIES = (
    "repo.write.immutable",
    "git.force_push",
    "github.write",
    "memory.write",
)
TRUSTED_LOCAL_APPROVAL_REQUIRED = (
    "repo.write.immutable",
    "github.write",
    "memory.write",
)

AUTOMATION_ALLOWED_CAPABILITIES = ("repo.read", "memory.read", "receipt.write")
AUTOMATION_DENIED_CAPABILITIES = (
    "repo.write",
    "repo.write.immutable",
    "shell.interactive",
    "shell.unbounded",
    "git.mutate",
    "github.write",
    "memory.write",
)
AUTOMATION_APPROVAL_REQUIRED: tuple[str, ...] = ()


class PolicyError(RuntimeError):
    """Base error for policy profile failures."""


class FailOpenNotAllowedError(PolicyError):
    """Raised when fail-open behavior was requested without explicit opt-in."""


class CapabilityDeniedError(PolicyError):
    """Raised when a requested action is denied by policy."""


@dataclass(frozen=True)
class GrantDecision:
    """Policy decision for a requested capability action."""

    allowed: bool
    capability: str
    target: str
    reason: str
    grant_id: str | None = None
    approval_required: bool = False
    immutable_path: bool = False
    receipt_metadata: dict[str, object] = field(default_factory=dict)


def generate_policy_envelope(
    *,
    task_id: str,
    actor: str,
    profile: PolicyProfile = "strict",
    trusted_local_fail_open: bool = False,
) -> PolicyEnvelope:
    """Generate a v0.1.0 policy envelope for a named profile."""
    if profile == "strict":
        return _envelope(
            task_id=task_id,
            actor=actor,
            profile="strict",
            fail_open=False,
            allowed=STRICT_ALLOWED_CAPABILITIES,
            denied=STRICT_DENIED_CAPABILITIES,
            approvals=STRICT_APPROVAL_REQUIRED,
            verification=("git.diff_check",),
        )
    if profile == "trusted-local":
        if not trusted_local_fail_open:
            raise FailOpenNotAllowedError(
                "trusted-local fail-open requires explicit trusted_local_fail_open=True"
            )
        return _envelope(
            task_id=task_id,
            actor=actor,
            profile="trusted-local",
            fail_open=True,
            allowed=TRUSTED_LOCAL_ALLOWED_CAPABILITIES,
            denied=TRUSTED_LOCAL_DENIED_CAPABILITIES,
            approvals=TRUSTED_LOCAL_APPROVAL_REQUIRED,
            verification=("receipt.review",),
        )
    if profile == "automation":
        return _envelope(
            task_id=task_id,
            actor=actor,
            profile="automation",
            fail_open=False,
            allowed=AUTOMATION_ALLOWED_CAPABILITIES,
            denied=AUTOMATION_DENIED_CAPABILITIES,
            approvals=AUTOMATION_APPROVAL_REQUIRED,
            verification=("ci.required",),
        )

    raise PolicyError(f"unsupported policy profile: {profile}")


def check_file_write_grant(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    path: str,
    docs: DocsProfile,
    override: dict[str, str] | None = None,
) -> GrantDecision:
    """Evaluate whether a file write is allowed."""
    capability = "repo.write.docs"
    immutable = is_immutable_path(path, docs.immutable_paths)
    if immutable and not _valid_immutable_override(override):
        return _denied(
            policy=policy,
            capability=capability,
            target=path,
            reason="immutable path writes require explicit approval metadata",
            immutable_path=True,
        )
    if immutable and "repo.write.immutable" in policy.denied_capabilities:
        grant = _matching_grant(grants, "repo.write.immutable", "write", path)
        if grant is None:
            return _denied(
                policy=policy,
                capability="repo.write.immutable",
                target=path,
                reason="immutable path write denied by policy without matching grant",
                immutable_path=True,
                approval_required=True,
            )
        return _allowed(
            grant=grant,
            capability="repo.write.immutable",
            target=path,
            reason="immutable path write allowed by explicit grant and override metadata",
            immutable_path=True,
            approval_required=True,
        )

    grant = _matching_grant(grants, capability, "write", path)
    if grant is None:
        return _denied(
            policy=policy,
            capability=capability,
            target=path,
            reason="file write requires matching capability grant",
        )
    return _allowed(
        grant=grant,
        capability=capability,
        target=path,
        reason="file write allowed by matching capability grant",
    )


def check_shell_grant(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    command: str,
) -> GrantDecision:
    """Evaluate whether a shell command is allowed."""
    return _check_capability(
        policy=policy,
        grants=grants,
        capability="shell.execute",
        operation="execute",
        target=command,
        denied_reason="shell execution requires matching capability grant",
    )


def check_github_grant(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    operation: str,
    target: str,
) -> GrantDecision:
    """Evaluate whether a GitHub write hook is allowed."""
    return _check_capability(
        policy=policy,
        grants=grants,
        capability="github.write",
        operation=operation,
        target=target,
        denied_reason="GitHub write requires matching capability grant",
    )


def check_memory_grant(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    operation: str,
    target: str,
) -> GrantDecision:
    """Evaluate whether a direct memory write hook is allowed."""
    return _check_capability(
        policy=policy,
        grants=grants,
        capability="memory.write",
        operation=operation,
        target=target,
        denied_reason="direct memory write requires matching capability grant",
    )


def denial_receipt(
    *,
    policy: PolicyEnvelope,
    decision: GrantDecision,
    actor: str,
) -> CapabilityReceipt:
    """Create a receipt for a denied capability decision."""
    metadata = redact(decision.receipt_metadata).value
    return CapabilityReceipt(
        id=f"receipt_denied_{policy.task_id}_{_receipt_slug(decision.capability)}",
        task_id=policy.task_id,
        actor=actor,
        capability=decision.capability,
        target=str(redact(decision.target).value),
        policy_profile=policy.profile,
        fail_open=policy.fail_open,
        reason=decision.reason,
        result=ReceiptResult(
            status="denied",
            summary=decision.reason,
            metadata=metadata if isinstance(metadata, dict) else {},
        ),
        redacted=True,
        created_at=datetime.now(UTC),
    )


def fail_open_receipt(
    *,
    task_id: str,
    actor: str,
    target: str,
    reason: str,
) -> CapabilityReceipt:
    """Create the mandatory receipt for a trusted-local fail-open decision."""
    return CapabilityReceipt(
        id=f"receipt_fail_open_{task_id}",
        task_id=task_id,
        actor=actor,
        capability="policy.fail_open",
        target=target,
        policy_profile="trusted-local",
        fail_open=True,
        reason=reason,
        result=ReceiptResult(
            status="passed",
            summary="Trusted-local fail-open profile explicitly selected.",
        ),
        redacted=True,
        created_at=datetime.now(UTC),
    )


def is_immutable_path(path: str, immutable_paths: list[str]) -> bool:
    """Return whether a path falls under an immutable path prefix."""
    normalized = _normalize_path(path)
    for candidate in immutable_paths:
        immutable = _normalize_path(candidate)
        if normalized == immutable or normalized.startswith(f"{immutable.rstrip('/')}/"):
            return True
    return False


def _check_capability(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    capability: str,
    operation: str,
    target: str,
    denied_reason: str,
) -> GrantDecision:
    grant = _matching_grant(grants, capability, operation, target)
    if grant is None:
        return _denied(
            policy=policy,
            capability=capability,
            target=target,
            reason=denied_reason,
        )
    return _allowed(
        grant=grant,
        capability=capability,
        target=target,
        reason=f"{capability} allowed by matching capability grant",
    )


def _matching_grant(
    grants: list[CapabilityGrant],
    capability: str,
    operation: str,
    target: str,
) -> CapabilityGrant | None:
    for grant in grants:
        if grant.capability != capability:
            continue
        if operation not in grant.operations:
            continue
        if not _target_matches(grant, target):
            continue
        return grant
    return None


def _target_matches(grant: CapabilityGrant, target: str) -> bool:
    paths = grant.target.paths
    excludes = grant.target.exclude
    if not paths:
        return True
    normalized = _normalize_path(target)
    if not _safe_target_value(normalized):
        return False
    if any(not _safe_target_pattern(pattern) for pattern in paths + excludes):
        return False
    if any(_path_matches(pattern, normalized) for pattern in excludes):
        return False
    return any(_path_matches(pattern, normalized) for pattern in paths)


def _path_matches(pattern: str, path: str) -> bool:
    normalized_pattern = _normalize_path(pattern)
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(f"{prefix}/")
    if normalized_pattern.endswith("/"):
        prefix = normalized_pattern.rstrip("/")
        return path == prefix or path.startswith(f"{prefix}/")
    return PurePosixPath(path).match(normalized_pattern)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _safe_target_value(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return bool(path) and ".." not in parts


def _safe_target_pattern(pattern: str) -> bool:
    normalized = _normalize_path(pattern)
    if not _safe_target_value(normalized):
        return False
    if pattern.startswith(("/", "\\")):
        return False
    if normalized in {"*", "**", "*/**"}:
        return False
    parts = PurePosixPath(normalized).parts
    if any(part == "**" for part in parts[:-1]):
        return False
    return True


def _valid_immutable_override(override: dict[str, str] | None) -> bool:
    if not override:
        return False
    return all(override.get(key) for key in ("approved_by", "reason"))


def _allowed(
    *,
    grant: CapabilityGrant,
    capability: str,
    target: str,
    reason: str,
    approval_required: bool = False,
    immutable_path: bool = False,
) -> GrantDecision:
    return GrantDecision(
        allowed=True,
        capability=capability,
        target=target,
        reason=reason,
        grant_id=grant.id,
        approval_required=approval_required,
        immutable_path=immutable_path,
        receipt_metadata={"grant_id": grant.id},
    )


def _denied(
    *,
    policy: PolicyEnvelope,
    capability: str,
    target: str,
    reason: str,
    approval_required: bool = False,
    immutable_path: bool = False,
) -> GrantDecision:
    return GrantDecision(
        allowed=False,
        capability=capability,
        target=target,
        reason=reason,
        approval_required=approval_required,
        immutable_path=immutable_path,
        receipt_metadata={
            "policy_id": policy.id,
            "profile": policy.profile,
            "immutable_path": immutable_path,
        },
    )


def _receipt_slug(value: str) -> str:
    return value.replace(".", "_").replace(":", "_").replace("/", "_")


def _envelope(
    *,
    task_id: str,
    actor: str,
    profile: PolicyProfile,
    fail_open: bool,
    allowed: tuple[str, ...],
    denied: tuple[str, ...],
    approvals: tuple[str, ...],
    verification: tuple[str, ...],
) -> PolicyEnvelope:
    return PolicyEnvelope(
        id=f"policy_{task_id}",
        task_id=task_id,
        actor=actor,
        profile=profile,
        fail_open=fail_open,
        allowed_capabilities=list(allowed),
        denied_capabilities=list(denied),
        approval_required=list(approvals),
        verification_required=list(verification),
        handoff_required=True,
        receipt_required=True,
        redaction_required=True,
    )


if not TYPE_CHECKING:
    __all__ = [name for name in globals() if not name.startswith("_")]
