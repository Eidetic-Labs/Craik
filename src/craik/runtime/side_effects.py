"""Policy-enforced side-effect wrappers with durable receipts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
from pathlib import Path
from typing import Any, Literal, cast

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityReceipt,
    DocsProfile,
    FactValue,
    PolicyEnvelope,
)
from craik.runtime.environment_receipts import EnvironmentReceiptContext, environment_receipt
from craik.runtime.policy.policy import (
    GrantDecision,
    check_file_write_grant,
    check_github_grant,
    check_memory_grant,
    check_shell_grant,
    denial_receipt,
)
from craik.runtime.policy.redaction import redact
from craik.runtime.store import LocalStore

SideEffectKind = Literal["shell", "file_write", "memory_write", "github_write"]


@dataclass(frozen=True)
class SideEffectResult:
    """Result of one governed side-effect attempt."""

    kind: SideEffectKind
    allowed: bool
    receipt: CapabilityReceipt
    output: dict[str, Any] | None = None


CommandExecutor = Callable[[str], dict[str, Any]]
GitHubWriter = Callable[[str, str], dict[str, Any]]


def run_shell_command_ref(
    *,
    store: LocalStore,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    actor: str,
    command_ref: str,
    executor: CommandExecutor | None = None,
) -> SideEffectResult:
    """Authorize and optionally execute a shell command reference."""
    decision = check_shell_grant(policy=policy, grants=grants, command=command_ref)
    denied = _persist_denial(store=store, policy=policy, decision=decision, actor=actor)
    if denied is not None:
        return SideEffectResult(kind="shell", allowed=False, receipt=denied)
    output = executor(command_ref) if executor else {"command_ref": command_ref}
    receipt = _passed_receipt(
        policy=policy,
        actor=actor,
        capability=decision.capability,
        target=command_ref,
        reason=decision.reason,
        metadata={"command_ref": command_ref, "output": redact(output).value},
    )
    receipt = store.put_receipt(receipt)
    return SideEffectResult(kind="shell", allowed=True, receipt=receipt, output=output)


def write_policy_file(
    *,
    store: LocalStore,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    actor: str,
    repo_root: Path,
    relative_path: str,
    content: str,
    docs: DocsProfile,
    immutable_override: dict[str, str] | None = None,
) -> SideEffectResult:
    """Authorize and write one repository-relative file."""
    path = _safe_repo_path(repo_root, relative_path)
    decision = check_file_write_grant(
        policy=policy,
        grants=grants,
        path=relative_path,
        docs=docs,
        override=immutable_override,
    )
    denied = _persist_denial(store=store, policy=policy, decision=decision, actor=actor)
    if denied is not None:
        return SideEffectResult(kind="file_write", allowed=False, receipt=denied)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(redact(content).value))
    receipt = _passed_receipt(
        policy=policy,
        actor=actor,
        capability=decision.capability,
        target=relative_path,
        reason=decision.reason,
        metadata={
            "path": relative_path,
            "bytes_written": len(path.read_bytes()),
            "immutable_path": decision.immutable_path,
        },
    )
    receipt = store.put_receipt(receipt)
    return SideEffectResult(kind="file_write", allowed=True, receipt=receipt)


def write_memory_fact(
    *,
    store: LocalStore,
    memory: Any,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    actor: str,
    fact: FactValue,
) -> SideEffectResult:
    """Authorize and write one durable memory fact."""
    target = f"{fact.scope}:{fact.entity}:{fact.relation}"
    decision = check_memory_grant(policy=policy, grants=grants, operation="write", target=target)
    denied = _persist_denial(store=store, policy=policy, decision=decision, actor=actor)
    if denied is not None:
        return SideEffectResult(kind="memory_write", allowed=False, receipt=denied)
    written = _write_fact(memory=memory, fact=fact, policy=policy, grants=grants)
    receipt = _passed_receipt(
        policy=policy,
        actor=actor,
        capability=decision.capability,
        target=target,
        reason=decision.reason,
        metadata={
            "entity": written.entity,
            "relation": written.relation,
            "scope": written.scope,
            "confidence": written.confidence,
        },
    )
    receipt = store.put_receipt(receipt)
    return SideEffectResult(kind="memory_write", allowed=True, receipt=receipt)


def _write_fact(
    *,
    memory: Any,
    fact: FactValue,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
) -> FactValue:
    write_fact = memory.write_fact
    parameters = signature(write_fact).parameters
    if "policy" in parameters and "grants" in parameters:
        return cast(FactValue, write_fact(fact, **{"policy": policy, "grants": grants}))
    return cast(FactValue, write_fact(fact))


def run_github_write(
    *,
    store: LocalStore,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    actor: str,
    operation: str,
    target: str,
    writer: GitHubWriter | None = None,
) -> SideEffectResult:
    """Authorize and optionally execute one GitHub write operation."""
    decision = check_github_grant(
        policy=policy,
        grants=grants,
        operation=operation,
        target=target,
    )
    denied = _persist_denial(store=store, policy=policy, decision=decision, actor=actor)
    if denied is not None:
        return SideEffectResult(kind="github_write", allowed=False, receipt=denied)
    output = writer(operation, target) if writer else {"operation": operation, "target": target}
    receipt = _passed_receipt(
        policy=policy,
        actor=actor,
        capability=decision.capability,
        target=target,
        reason=decision.reason,
        metadata={"operation": operation, "github_result": redact(output).value},
    )
    receipt = store.put_receipt(receipt)
    return SideEffectResult(kind="github_write", allowed=True, receipt=receipt, output=output)


def _persist_denial(
    *,
    store: LocalStore,
    policy: PolicyEnvelope,
    decision: GrantDecision,
    actor: str,
) -> CapabilityReceipt | None:
    if decision.allowed:
        return None
    receipt = denial_receipt(policy=policy, decision=decision, actor=actor)
    return store.put_receipt(receipt)


def _passed_receipt(
    *,
    policy: PolicyEnvelope,
    actor: str,
    capability: str,
    target: str,
    reason: str,
    metadata: dict[str, Any],
) -> CapabilityReceipt:
    redacted_target = str(redact(target).value)
    return environment_receipt(
        receipt_id=f"receipt_{policy.task_id}_{_slug(capability)}_{_slug(redacted_target)}",
        action="sandbox_action",
        context=EnvironmentReceiptContext(
            task_id=policy.task_id,
            policy_envelope_id=policy.id,
            target_id=redacted_target,
        ),
        actor=actor,
        capability=capability,
        policy_profile=policy.profile,
        status="passed",
        reason=reason,
        summary=reason,
        metadata=metadata,
    )


def _safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    root = repo_root.resolve()
    path = (root / relative_path).resolve()
    if root != path and root not in path.parents:
        raise ValueError(f"file write escapes repository root: {relative_path}")
    return path


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
