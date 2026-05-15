import pytest

from craik.runtime.policy import (
    FailOpenNotAllowedError,
    fail_open_receipt,
    generate_policy_envelope,
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

