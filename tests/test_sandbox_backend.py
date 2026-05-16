import pytest
from pydantic import ValidationError

from craik.contracts.models import (
    SandboxBackend,
    SandboxBackendCapability,
    SandboxBackendPolicy,
)


def _backend(**overrides: object) -> SandboxBackend:
    payload = {
        "id": "sandbox_backend_local_fixture",
        "name": "Local Process Sandbox",
        "kind": "local_process",
        "isolation_mode": "process",
        "capabilities": [
            SandboxBackendCapability(
                name="shell.execute",
                operations=["run"],
                description="Execute local process commands under policy.",
            )
        ],
        "policy": SandboxBackendPolicy(
            notes=["Local process execution requires operator-controlled policy."]
        ),
        "runtime_ref": "craik.runtime.sandbox.local_process",
        "metadata": {"platforms": ["darwin", "linux"]},
        "docs": ["docs/reference/sandbox-backends.md"],
        "created_at": "2026-05-16T20:10:00Z",
    }
    payload.update(overrides)
    return SandboxBackend.model_validate(payload)


def test_sandbox_backend_accepts_local_container_remote_and_browser_backends() -> None:
    assert _backend(kind="local_process", isolation_mode="process").kind == "local_process"
    assert _backend(kind="container", isolation_mode="container").kind == "container"
    assert _backend(kind="remote_shell", isolation_mode="remote").kind == "remote_shell"
    assert _backend(kind="browser_tool", isolation_mode="browser").kind == "browser_tool"


def test_sandbox_backend_rejects_wrong_isolation_mode() -> None:
    with pytest.raises(ValidationError, match="local_process backends require 'process'"):
        _backend(isolation_mode="container")


def test_sandbox_backend_requires_policy_boundaries() -> None:
    with pytest.raises(ValidationError, match="policy envelopes"):
        _backend(policy=SandboxBackendPolicy(policy_envelope_required=False))

    with pytest.raises(ValidationError, match="capability grants"):
        _backend(policy=SandboxBackendPolicy(capability_grant_required=False))

    with pytest.raises(ValidationError, match="receipts"):
        _backend(policy=SandboxBackendPolicy(receipt_required=False))

    with pytest.raises(ValidationError, match="redaction"):
        _backend(policy=SandboxBackendPolicy(redaction_required=False))


def test_sandbox_backend_capabilities_require_grants_and_receipts() -> None:
    with pytest.raises(ValidationError, match="capabilities require grants"):
        _backend(
            capabilities=[
                SandboxBackendCapability(
                    name="shell.execute",
                    operations=["run"],
                    grant_required=False,
                    description="Run commands.",
                )
            ]
        )

    with pytest.raises(ValidationError, match="capabilities require receipts"):
        _backend(
            capabilities=[
                SandboxBackendCapability(
                    name="shell.execute",
                    operations=["run"],
                    receipt_required=False,
                    description="Run commands.",
                )
            ]
        )


def test_sandbox_backend_rejects_secret_and_provider_metadata() -> None:
    with pytest.raises(ValidationError, match="secret or provider keys"):
        _backend(metadata={"api_key": "not allowed"})

    with pytest.raises(ValidationError, match="secret or provider keys"):
        _backend(metadata={"provider_id": "provider_fixture_local"})
