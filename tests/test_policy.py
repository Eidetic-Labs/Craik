import pytest

from craik.contracts.models import CapabilityGrant, CapabilityTarget, DocsProfile
from craik.runtime.policy.operator_policy import check_operator_policy
from craik.runtime.policy.policy import (
    FailOpenNotAllowedError,
    check_file_write_grant,
    check_github_grant,
    check_memory_grant,
    check_shell_grant,
    denial_receipt,
    fail_open_receipt,
    generate_policy_envelope,
    is_immutable_path,
)


def test_strict_is_default_profile() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")

    assert envelope.profile == "strict"
    assert envelope.fail_open is False
    assert "repo.read" in envelope.allowed_capabilities
    assert "repo.write" in envelope.denied_capabilities
    assert envelope.receipt_required is True
    assert envelope.redaction_required is True


def test_trusted_local_requires_explicit_fail_open_opt_in() -> None:
    with pytest.raises(FailOpenNotAllowedError):
        generate_policy_envelope(
            task_id="task_policy",
            actor="agent:codex",
            profile="trusted-local",
        )


def test_trusted_local_explicit_opt_in_sets_fail_open_and_receipts() -> None:
    envelope = generate_policy_envelope(
        task_id="task_policy",
        actor="agent:codex",
        profile="trusted-local",
        trusted_local_fail_open=True,
    )

    assert envelope.profile == "trusted-local"
    assert envelope.fail_open is True
    assert envelope.receipt_required is True
    assert "repo.write.local" in envelope.allowed_capabilities
    assert "repo.write.immutable" in envelope.denied_capabilities
    assert "memory.write" in envelope.approval_required


def test_automation_fails_closed() -> None:
    envelope = generate_policy_envelope(
        task_id="task_policy",
        actor="agent:ci",
        profile="automation",
    )

    assert envelope.profile == "automation"
    assert envelope.fail_open is False
    assert "shell.interactive" in envelope.denied_capabilities
    assert "memory.write" in envelope.denied_capabilities
    assert envelope.approval_required == []


def test_fail_open_decision_creates_visible_receipt() -> None:
    receipt = fail_open_receipt(
        task_id="task_policy",
        actor="agent:codex",
        target="trusted-local",
        reason="User selected trusted-local profile.",
    )

    assert receipt.policy_profile == "trusted-local"
    assert receipt.fail_open is True
    assert receipt.capability == "policy.fail_open"
    assert receipt.result.status == "passed"
    assert receipt.redacted is True


def test_file_write_without_grant_is_denied() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    decision = check_file_write_grant(
        policy=envelope,
        grants=[],
        path="docs/index.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"]),
    )

    assert decision.allowed is False
    assert decision.capability == "repo.write.docs"
    assert decision.reason == "file write requires matching capability grant"


def test_file_write_with_matching_grant_is_allowed() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    grant = _grant("repo.write.docs", paths=["docs/**"], operations=["write"])

    decision = check_file_write_grant(
        policy=envelope,
        grants=[grant],
        path="docs/index.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"]),
    )

    assert decision.allowed is True
    assert decision.grant_id == "grant_repo_write_docs"


def test_immutable_path_is_denied_without_override_metadata() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    grant = _grant("repo.write.immutable", paths=["docs/adr/**"], operations=["write"])

    decision = check_file_write_grant(
        policy=envelope,
        grants=[grant],
        path="docs/adr/0001.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"]),
    )

    assert decision.allowed is False
    assert decision.immutable_path is True
    assert "approval metadata" in decision.reason


def test_immutable_path_requires_explicit_grant_even_with_override_metadata() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")

    decision = check_file_write_grant(
        policy=envelope,
        grants=[],
        path="docs/adr/0001.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"]),
        override={"approved_by": "user:maintainer", "reason": "Correct typo."},
    )

    assert decision.allowed is False
    assert decision.approval_required is True
    assert "without matching grant" in decision.reason


def test_immutable_path_allowed_with_override_metadata_and_grant() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    grant = _grant("repo.write.immutable", paths=["docs/adr/**"], operations=["write"])

    decision = check_file_write_grant(
        policy=envelope,
        grants=[grant],
        path="docs/adr/0001.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"]),
        override={"approved_by": "user:maintainer", "reason": "Correct typo."},
    )

    assert decision.allowed is True
    assert decision.immutable_path is True
    assert decision.approval_required is True


def test_grant_exclude_blocks_path() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    grant = _grant(
        "repo.write.docs",
        paths=["docs/**"],
        exclude=["docs/adr/**"],
        operations=["write"],
    )

    decision = check_file_write_grant(
        policy=envelope,
        grants=[grant],
        path="docs/adr/0001.md",
        docs=DocsProfile(paths=["docs/"], immutable_paths=[]),
    )

    assert decision.allowed is False


def test_shell_github_and_memory_hooks_require_matching_grants() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")

    assert check_shell_grant(policy=envelope, grants=[], command="pytest").allowed is False
    assert check_github_grant(
        policy=envelope,
        grants=[],
        operation="create_pr",
        target="Eidetic-Labs/Craik",
    ).allowed is False
    assert check_memory_grant(
        policy=envelope,
        grants=[],
        operation="write",
        target="scope:team",
    ).allowed is False

    assert check_shell_grant(
        policy=envelope,
        grants=[_grant("shell.execute", operations=["execute"])],
        command="pytest",
    ).allowed is True
    assert check_github_grant(
        policy=envelope,
        grants=[_grant("github.write", operations=["create_pr"])],
        operation="create_pr",
        target="Eidetic-Labs/Craik",
    ).allowed is True
    assert check_memory_grant(
        policy=envelope,
        grants=[_grant("memory.write", operations=["write"])],
        operation="write",
        target="scope:team",
    ).allowed is True


def test_operator_policy_requires_matching_group() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    envelope = envelope.model_copy(
        update={"required_operator": True, "allowed_operator_groups": ["prod-deploy"]}
    )

    denied = check_operator_policy(
        policy=envelope,
        operator_subject="operator-123",
        operator_issuer="https://issuer.example.test",
        operator_groups=["platform"],
    )
    allowed = check_operator_policy(
        policy=envelope,
        operator_subject="operator-123",
        operator_issuer="https://issuer.example.test",
        operator_groups=["platform", "prod-deploy"],
    )

    assert denied.allowed is False
    assert denied.reason == "operator groups denied by policy"
    assert allowed.allowed is True
    assert allowed.receipt_metadata["matched_operator_group"] == "prod-deploy"


def test_operator_policy_requires_identity_when_configured() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    envelope = envelope.model_copy(update={"required_operator": True})

    decision = check_operator_policy(
        policy=envelope,
        operator_subject=None,
        operator_issuer=None,
        operator_groups=[],
    )

    assert decision.allowed is False
    assert "run craik login" in decision.reason


def test_denied_decision_can_create_receipt() -> None:
    envelope = generate_policy_envelope(task_id="task_policy", actor="agent:codex")
    decision = check_shell_grant(policy=envelope, grants=[], command="pytest")

    receipt = denial_receipt(policy=envelope, decision=decision, actor="agent:codex")

    assert receipt.result.status == "denied"
    assert receipt.capability == "shell.execute"
    assert receipt.policy_profile == "strict"
    assert receipt.fail_open is False


def test_is_immutable_path_matches_prefixes() -> None:
    assert is_immutable_path("docs/adr/0001.md", ["docs/adr/"])
    assert not is_immutable_path("docs/guides/index.md", ["docs/adr/"])


def _grant(
    capability: str,
    *,
    paths: list[str] | None = None,
    exclude: list[str] | None = None,
    operations: list[str],
) -> CapabilityGrant:
    return CapabilityGrant(
        id=f"grant_{capability.replace('.', '_')}",
        task_id="task_policy",
        capability=capability,
        target=CapabilityTarget(paths=paths or [], exclude=exclude or []),
        operations=operations,
        reason="Test grant.",
        approved_by="user:maintainer",
    )
