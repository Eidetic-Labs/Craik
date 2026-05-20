import sys
import threading
import time

from craik.contracts.models import (
    SandboxBackend,
    SandboxBackendCapability,
)
from craik.runtime.sandbox.local_process_backend import (
    LocalProcessCommand,
    LocalProcessCommandRegistry,
    LocalProcessRequest,
    execute_local_process_command,
    local_process_decision,
)


def _backend(**overrides: object) -> SandboxBackend:
    payload = {
        "id": "sandbox_backend_local_fixture",
        "name": "Fixture Local Process Sandbox",
        "kind": "local_process",
        "isolation_mode": "process",
        "capabilities": [
            SandboxBackendCapability(
                name="shell.execute",
                operations=["run"],
                description="Execute local process command references under policy.",
            )
        ],
        "docs": ["docs/reference/local-process-backend.md"],
        "created_at": "2026-05-16T20:20:00Z",
    }
    payload.update(overrides)
    return SandboxBackend.model_validate(payload)


def _request(**overrides: object) -> LocalProcessRequest:
    payload = {
        "id": "local_process_request_fixture",
        "backend_id": "sandbox_backend_local_fixture",
        "command_ref": "check_ruff",
        "policy_envelope_id": "policy_local_process_fixture",
        "capability_grant_id": "grant_shell_execute_fixture",
        "receipt_id": "receipt_local_process_fixture",
        "working_directory_ref": "repo_root",
    }
    payload.update(overrides)
    return LocalProcessRequest.model_validate(payload)


def test_local_process_decision_allows_policy_bound_command_reference() -> None:
    decision = local_process_decision(backend=_backend(), request=_request())

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == "local process request is policy-, grant-, and receipt-bound"
    assert decision.required_controls == [
        "policy_envelope",
        "capability_grant",
        "receipt",
        "redaction",
    ]


def test_local_process_decision_denies_non_local_process_backend() -> None:
    backend = _backend(kind="container", isolation_mode="container")

    decision = local_process_decision(backend=backend, request=_request())

    assert decision.allowed is False
    assert decision.reason == (
        "local process requests require a local_process backend with process isolation"
    )


def test_local_process_decision_denies_backend_mismatch() -> None:
    decision = local_process_decision(
        backend=_backend(),
        request=_request(backend_id="sandbox_backend_other"),
    )

    assert decision.allowed is False
    assert decision.reason == (
        "request targets sandbox_backend_other, not sandbox_backend_local_fixture"
    )


def test_local_process_decision_denies_missing_shell_capability() -> None:
    backend = _backend(
        capabilities=[
            SandboxBackendCapability(
                name="file.read",
                operations=["read"],
                description="Read files.",
            )
        ]
    )

    decision = local_process_decision(backend=backend, request=_request())

    assert decision.allowed is False
    assert decision.reason == "backend does not declare shell.execute run support"


def test_local_process_decision_denies_missing_policy_grant_or_receipt() -> None:
    assert (
        local_process_decision(
            backend=_backend(),
            request=_request(policy_envelope_id=None),
        ).reason
        == "local process execution requires a policy envelope"
    )
    assert (
        local_process_decision(
            backend=_backend(),
            request=_request(capability_grant_id=None),
        ).reason
        == "local process execution requires a capability grant"
    )
    assert (
        local_process_decision(
            backend=_backend(),
            request=_request(receipt_id=None),
        ).reason
        == "local process execution requires a receipt"
    )


def test_local_process_decision_denies_inline_shell() -> None:
    decision = local_process_decision(
        backend=_backend(),
        request=_request(command_ref="uv run pytest"),
    )

    assert decision.allowed is False
    assert decision.reason == "local process requests require command references, not inline shell"


def test_local_process_executor_runs_registered_command_reference() -> None:
    registry = LocalProcessCommandRegistry(
        [
            LocalProcessCommand(
                ref="check_python",
                argv=["python", "-c", "print('sandbox ok')"],
            )
        ]
    )

    result = execute_local_process_command(
        backend=_backend(),
        request=_request(command_ref="check_python"),
        registry=registry,
    )

    assert result.allowed is True
    assert result.executed is True
    assert result.returncode == 0
    assert result.stdout == "sandbox ok\n"


def test_local_process_executor_denies_unregistered_command_reference() -> None:
    result = execute_local_process_command(
        backend=_backend(),
        request=_request(command_ref="missing_command"),
        registry=LocalProcessCommandRegistry(),
    )

    assert result.allowed is False
    assert result.executed is False
    assert result.reason == "command reference is not registered"


def test_local_process_executor_cancels_in_flight_command_reference() -> None:
    cancel_event = threading.Event()
    registry = LocalProcessCommandRegistry(
        [
            LocalProcessCommand(
                ref="slow_python",
                argv=[sys.executable, "-c", "import time; time.sleep(5)"],
                timeout_seconds=10,
            )
        ]
    )
    timer = threading.Timer(0.1, cancel_event.set)
    timer.start()
    started = time.monotonic()
    try:
        result = execute_local_process_command(
            backend=_backend(),
            request=_request(command_ref="slow_python"),
            registry=registry,
            cancel_event=cancel_event,
        )
    finally:
        timer.cancel()

    assert time.monotonic() - started < 2
    assert result.allowed is True
    assert result.executed is True
    assert result.cancelled is True
    assert result.reason == "local process command cancelled"
