import pytest
from pydantic import ValidationError

from craik.contracts.models import SandboxBackend, SandboxBackendCapability
from craik.runtime.sandbox.docker_sandbox_backend import (
    DockerMount,
    DockerSandboxRequest,
    docker_sandbox_decision,
)


def _backend(**overrides: object) -> SandboxBackend:
    payload = {
        "id": "sandbox_backend_docker_fixture",
        "name": "Fixture Docker Sandbox",
        "kind": "container",
        "isolation_mode": "container",
        "capabilities": [
            SandboxBackendCapability(
                name="container.run",
                operations=["run"],
                description="Run containerized command references under policy.",
            )
        ],
        "docs": ["docs/reference/docker-sandbox-backend.md"],
        "created_at": "2026-05-16T20:40:00Z",
    }
    payload.update(overrides)
    return SandboxBackend.model_validate(payload)


def _request(**overrides: object) -> DockerSandboxRequest:
    payload = {
        "id": "docker_request_fixture",
        "backend_id": "sandbox_backend_docker_fixture",
        "image_ref": "image_fixture_python",
        "command_ref": "check_pytest",
        "network_mode": "none",
        "mounts": [DockerMount(source_ref="repo_readonly", target_path="/workspace")],
        "env_ref_names": ["PYTHONPATH"],
        "policy_envelope_id": "policy_docker_fixture",
        "capability_grant_id": "grant_container_run_fixture",
        "receipt_id": "receipt_docker_fixture",
    }
    payload.update(overrides)
    return DockerSandboxRequest.model_validate(payload)


def test_docker_sandbox_decision_allows_safe_isolated_request() -> None:
    decision = docker_sandbox_decision(backend=_backend(), request=_request())

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == "Docker sandbox request is isolated, policy-bound, and receipt-ready"
    assert decision.network_mode == "none"
    assert decision.required_controls == [
        "policy_envelope",
        "capability_grant",
        "receipt",
        "redaction",
        "explicit_isolation",
    ]


def test_docker_sandbox_request_rejects_secret_like_refs() -> None:
    with pytest.raises(ValidationError, match="image_ref must not contain secret-like"):
        _request(image_ref="image?token=raw")

    with pytest.raises(ValidationError, match="mount source_ref must not contain secret-like"):
        _request(mounts=[DockerMount(source_ref="repo?password=raw", target_path="/workspace")])


def test_docker_sandbox_decision_denies_wrong_backend_or_missing_capability() -> None:
    wrong_backend = docker_sandbox_decision(
        backend=_backend(kind="local_process", isolation_mode="process"),
        request=_request(),
    )
    missing_capability = docker_sandbox_decision(
        backend=_backend(
            capabilities=[
                SandboxBackendCapability(
                    name="shell.execute",
                    operations=["run"],
                    description="Run local commands.",
                )
            ]
        ),
        request=_request(),
    )

    assert wrong_backend.allowed is False
    assert wrong_backend.reason == (
        "Docker requests require a container backend with container isolation"
    )
    assert missing_capability.allowed is False
    assert missing_capability.reason == "backend does not declare container.run support"


def test_docker_sandbox_decision_denies_unsafe_defaults() -> None:
    assert (
        docker_sandbox_decision(backend=_backend(), request=_request(privileged=True)).reason
        == "Docker sandbox requests must not be privileged"
    )
    assert (
        docker_sandbox_decision(backend=_backend(), request=_request(network_mode="bridge")).reason
        == "Docker sandbox network mode must be none or restricted"
    )
    assert (
        docker_sandbox_decision(
            backend=_backend(),
            request=_request(
                mounts=[
                    DockerMount(
                        source_ref="repo_write",
                        target_path="/workspace",
                        mode="read_write",
                    )
                ]
            ),
        ).reason
        == "Docker sandbox mounts must be read-only by default"
    )


def test_docker_sandbox_decision_denies_missing_policy_grant_or_receipt() -> None:
    assert (
        docker_sandbox_decision(
            backend=_backend(),
            request=_request(policy_envelope_id=None),
        ).reason
        == "Docker sandbox execution requires a policy envelope"
    )
    assert (
        docker_sandbox_decision(
            backend=_backend(),
            request=_request(capability_grant_id=None),
        ).reason
        == "Docker sandbox execution requires a capability grant"
    )
    assert (
        docker_sandbox_decision(
            backend=_backend(),
            request=_request(receipt_id=None),
        ).reason
        == "Docker sandbox execution requires a receipt"
    )
