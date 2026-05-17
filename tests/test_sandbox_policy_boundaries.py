from craik.contracts.models import SandboxBackend, SandboxBackendCapability
from craik.runtime.environment_receipts import EnvironmentReceiptContext, environment_receipt
from craik.runtime.sandbox.browser_tool_boundary import BrowserToolRequest, browser_tool_decision
from craik.runtime.sandbox.docker_sandbox_backend import (
    DockerSandboxRequest,
    docker_sandbox_decision,
)
from craik.runtime.sandbox.local_process_backend import LocalProcessRequest, local_process_decision
from craik.runtime.sandbox.remote_shell_backend import (
    RemoteShellRequest,
    RemoteShellTarget,
    remote_shell_decision,
)


def test_sandbox_policy_allows_only_policy_grant_and_receipt_bound_actions() -> None:
    local = local_process_decision(
        backend=_backend(
            backend_id="sandbox_local",
            kind="local_process",
            isolation_mode="process",
            capability="shell.execute",
        ),
        request=LocalProcessRequest(
            id="request_local",
            backend_id="sandbox_local",
            command_ref="check_local",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_local",
            receipt_id="receipt_local",
        ),
    )
    remote = remote_shell_decision(
        backend=_backend(
            backend_id="sandbox_remote",
            kind="remote_shell",
            isolation_mode="remote",
            capability="shell.remote.execute",
        ),
        target=RemoteShellTarget(
            id="target_remote",
            host_ref="REMOTE_HOST",
            auth_ref_name="REMOTE_AUTH",
        ),
        request=RemoteShellRequest(
            id="request_remote",
            backend_id="sandbox_remote",
            target_id="target_remote",
            command_ref="check_remote",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_remote",
            receipt_id="receipt_remote",
        ),
    )
    browser = browser_tool_decision(
        backend=_backend(
            backend_id="sandbox_browser",
            kind="browser_tool",
            isolation_mode="browser",
            capability="browser.open",
        ),
        request=BrowserToolRequest(
            id="request_browser",
            backend_id="sandbox_browser",
            tool_name="browser.open",
            capability="browser.open",
            action_ref="open_docs",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_browser",
            receipt_id="receipt_browser",
        ),
    )
    docker = docker_sandbox_decision(
        backend=_backend(
            backend_id="sandbox_docker",
            kind="container",
            isolation_mode="container",
            capability="container.run",
        ),
        request=DockerSandboxRequest(
            id="request_docker",
            backend_id="sandbox_docker",
            image_ref="image_python",
            command_ref="check_pytest",
            network_mode="none",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_docker",
            receipt_id="receipt_docker",
        ),
    )

    assert [local.allowed, remote.allowed, browser.allowed, docker.allowed] == [
        True,
        True,
        True,
        True,
    ]


def test_sandbox_policy_denies_missing_policy_controls_across_backends() -> None:
    local = local_process_decision(
        backend=_backend(
            backend_id="sandbox_local",
            kind="local_process",
            isolation_mode="process",
            capability="shell.execute",
        ),
        request=LocalProcessRequest(
            id="request_local",
            backend_id="sandbox_local",
            command_ref="check_local",
            capability_grant_id="grant_local",
            receipt_id="receipt_local",
        ),
    )
    browser = browser_tool_decision(
        backend=_backend(
            backend_id="sandbox_browser",
            kind="browser_tool",
            isolation_mode="browser",
            capability="browser.open",
        ),
        request=BrowserToolRequest(
            id="request_browser",
            backend_id="sandbox_browser",
            tool_name="browser.open",
            capability="browser.open",
            action_ref="open_docs",
            policy_envelope_id="policy_environment",
            receipt_id="receipt_browser",
        ),
    )
    docker = docker_sandbox_decision(
        backend=_backend(
            backend_id="sandbox_docker",
            kind="container",
            isolation_mode="container",
            capability="container.run",
        ),
        request=DockerSandboxRequest(
            id="request_docker",
            backend_id="sandbox_docker",
            image_ref="image_python",
            command_ref="check_pytest",
            network_mode="none",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_docker",
        ),
    )

    assert local.allowed is False
    assert local.reason == "local process execution requires a policy envelope"
    assert browser.allowed is False
    assert browser.reason == "browser/tool execution requires a capability grant"
    assert docker.allowed is False
    assert docker.reason == "Docker sandbox execution requires a receipt"


def test_sandbox_policy_denies_unsafe_isolation_defaults() -> None:
    remote = remote_shell_decision(
        backend=_backend(
            backend_id="sandbox_remote",
            kind="remote_shell",
            isolation_mode="remote",
            capability="shell.remote.execute",
        ),
        target=RemoteShellTarget(
            id="target_remote",
            host_ref="REMOTE_HOST",
            auth_ref_name="REMOTE_AUTH",
        ),
        request=RemoteShellRequest(
            id="request_remote",
            backend_id="sandbox_remote",
            target_id="target_remote",
            command_ref="ssh host uname -a",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_remote",
            receipt_id="receipt_remote",
        ),
    )
    docker = docker_sandbox_decision(
        backend=_backend(
            backend_id="sandbox_docker",
            kind="container",
            isolation_mode="container",
            capability="container.run",
        ),
        request=DockerSandboxRequest(
            id="request_docker",
            backend_id="sandbox_docker",
            image_ref="image_python",
            command_ref="check_pytest",
            network_mode="bridge",
            policy_envelope_id="policy_environment",
            capability_grant_id="grant_docker",
            receipt_id="receipt_docker",
        ),
    )

    assert remote.allowed is False
    assert remote.reason == "remote shell requests require command references, not inline shell"
    assert docker.allowed is False
    assert docker.reason == "Docker sandbox network mode must be none or restricted"


def test_sandbox_policy_receipts_keep_context_and_redact_payloads() -> None:
    receipt = environment_receipt(
        receipt_id="receipt_environment_policy",
        action="sandbox_action",
        context=EnvironmentReceiptContext(
            task_id="task_environment",
            policy_envelope_id="policy_environment",
            backend_id="sandbox_docker",
            command_ref="check_pytest",
            receipt_ids=["receipt_prior"],
        ),
        actor="agent:codex",
        capability="container.run",
        policy_profile="strict",
        status="passed",
        reason="Docker sandbox request allowed.",
        summary="Sandbox policy accepted the request.",
        metadata={
            "raw_command": "uv run pytest",
            "env": {"TOKEN": "secret"},
            "safe": "kept",
        },
    )

    assert receipt.result.metadata["policy_envelope_id"] == "policy_environment"
    assert receipt.result.metadata["backend_id"] == "sandbox_docker"
    assert receipt.result.metadata["command_ref"] == "check_pytest"
    assert receipt.result.metadata["safe"] == "kept"
    assert "raw_command" not in receipt.result.metadata
    assert "env" not in receipt.result.metadata


def _backend(
    *,
    backend_id: str,
    kind: str,
    isolation_mode: str,
    capability: str,
) -> SandboxBackend:
    return SandboxBackend.model_validate(
        {
            "id": backend_id,
            "name": f"{backend_id} fixture",
            "kind": kind,
            "isolation_mode": isolation_mode,
            "capabilities": [
                SandboxBackendCapability(
                    name=capability,
                    operations=["run", "open"],
                    description="Fixture sandbox capability.",
                )
            ],
            "docs": ["docs/reference/sandbox-backends.md"],
            "created_at": "2026-05-16T20:50:00Z",
        }
    )
