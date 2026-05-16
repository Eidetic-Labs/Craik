import pytest
from pydantic import ValidationError

from craik.contracts.models import SandboxBackend, SandboxBackendCapability
from craik.runtime.remote_shell_backend import (
    RemoteShellRequest,
    RemoteShellTarget,
    remote_shell_decision,
)


def _backend(**overrides: object) -> SandboxBackend:
    payload = {
        "id": "sandbox_backend_remote_fixture",
        "name": "Fixture Remote Shell Sandbox",
        "kind": "remote_shell",
        "isolation_mode": "remote",
        "capabilities": [
            SandboxBackendCapability(
                name="shell.remote.execute",
                operations=["run"],
                description="Execute remote shell command references under policy.",
            )
        ],
        "docs": ["docs/reference/remote-shell-backend.md"],
        "created_at": "2026-05-16T20:25:00Z",
    }
    payload.update(overrides)
    return SandboxBackend.model_validate(payload)


def _target(**overrides: object) -> RemoteShellTarget:
    payload = {
        "id": "remote_target_fixture",
        "host_ref": "REMOTE_FIXTURE_HOST",
        "user_ref": "REMOTE_FIXTURE_USER",
        "port_ref": "REMOTE_FIXTURE_PORT",
        "auth_ref_name": "REMOTE_FIXTURE_SSH_KEY",
        "metadata": {"environment": "fixture"},
    }
    payload.update(overrides)
    return RemoteShellTarget.model_validate(payload)


def _request(**overrides: object) -> RemoteShellRequest:
    payload = {
        "id": "remote_shell_request_fixture",
        "backend_id": "sandbox_backend_remote_fixture",
        "target_id": "remote_target_fixture",
        "command_ref": "remote_check_ruff",
        "policy_envelope_id": "policy_remote_shell_fixture",
        "capability_grant_id": "grant_remote_shell_fixture",
        "receipt_id": "receipt_remote_shell_fixture",
    }
    payload.update(overrides)
    return RemoteShellRequest.model_validate(payload)


def test_remote_shell_target_rejects_inline_secrets() -> None:
    with pytest.raises(ValidationError, match="host_ref must not contain inline credentials"):
        _target(host_ref="ssh://user:pass@example.invalid")

    with pytest.raises(ValidationError, match="metadata must not contain secret-like"):
        _target(metadata={"password": "not allowed"})


def test_remote_shell_decision_allows_policy_bound_remote_command_reference() -> None:
    decision = remote_shell_decision(
        backend=_backend(),
        target=_target(),
        request=_request(),
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == "remote shell request is target-, policy-, grant-, and receipt-bound"
    assert decision.receipt_id == "receipt_remote_shell_fixture"
    assert decision.required_controls == [
        "policy_envelope",
        "capability_grant",
        "receipt",
        "redaction",
        "external_auth_ref",
    ]


def test_remote_shell_decision_denies_wrong_backend_or_target() -> None:
    wrong_backend = remote_shell_decision(
        backend=_backend(kind="local_process", isolation_mode="process"),
        target=_target(),
        request=_request(),
    )
    wrong_target = remote_shell_decision(
        backend=_backend(),
        target=_target(),
        request=_request(target_id="other_target"),
    )

    assert wrong_backend.allowed is False
    assert wrong_backend.reason == (
        "remote shell requests require a remote_shell backend with remote isolation"
    )
    assert wrong_target.allowed is False
    assert wrong_target.reason == "request targets other_target, not remote_target_fixture"


def test_remote_shell_decision_denies_missing_remote_capability() -> None:
    backend = _backend(
        capabilities=[
            SandboxBackendCapability(
                name="shell.execute",
                operations=["run"],
                description="Local shell execution.",
            )
        ]
    )

    decision = remote_shell_decision(backend=backend, target=_target(), request=_request())

    assert decision.allowed is False
    assert decision.reason == "backend does not declare shell.remote.execute run support"


def test_remote_shell_decision_denies_missing_auth_policy_grant_or_receipt() -> None:
    assert (
        remote_shell_decision(
            backend=_backend(),
            target=_target(auth_ref_name=None),
            request=_request(),
        ).reason
        == "remote shell execution requires an external auth reference"
    )
    assert (
        remote_shell_decision(
            backend=_backend(),
            target=_target(),
            request=_request(policy_envelope_id=None),
        ).reason
        == "remote shell execution requires a policy envelope"
    )
    assert (
        remote_shell_decision(
            backend=_backend(),
            target=_target(),
            request=_request(capability_grant_id=None),
        ).reason
        == "remote shell execution requires a capability grant"
    )
    assert (
        remote_shell_decision(
            backend=_backend(),
            target=_target(),
            request=_request(receipt_id=None),
        ).reason
        == "remote shell execution requires a receipt"
    )


def test_remote_shell_decision_denies_inline_shell() -> None:
    decision = remote_shell_decision(
        backend=_backend(),
        target=_target(),
        request=_request(command_ref="ssh host uname -a"),
    )

    assert decision.allowed is False
    assert decision.reason == "remote shell requests require command references, not inline shell"
