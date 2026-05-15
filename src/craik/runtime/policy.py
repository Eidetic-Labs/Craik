"""Policy profile definitions and envelope generation."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import CapabilityReceipt, PolicyEnvelope, PolicyProfile, ReceiptResult

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

