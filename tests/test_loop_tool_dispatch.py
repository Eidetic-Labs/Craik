import json
from datetime import UTC, datetime

from craik.contracts.models import (
    CapabilityReceipt,
    ReceiptResult,
    RunnerMetadata,
    RunnerStepResult,
)
from craik.runtime.side_effects import SideEffectResult
from craik.runtime.work.loop_support.tool_dispatch import (
    dispatchable_tool_calls,
    result_with_stream_chunks,
    tool_arguments,
    tool_message,
    tool_result_attestation,
)


def test_dispatchable_tool_calls_accepts_supported_shapes() -> None:
    result = _step_result(
        {
            "tool_calls": [
                {"id": "call_1", "name": "shell.execute"},
                {"id": "call_2", "function": {"name": "github.write"}},
                {"id": "call_3", "name": "unknown.tool"},
                "not-a-call",
            ]
        }
    )

    assert [call["id"] for call in dispatchable_tool_calls(result)] == [
        "call_1",
        "call_2",
    ]


def test_tool_arguments_decodes_json_function_arguments() -> None:
    assert tool_arguments(
        {"function": {"arguments": '{"command_ref": "fixture-action"}'}}
    ) == {"command_ref": "fixture-action"}


def test_result_with_stream_chunks_preserves_replayable_text() -> None:
    result = result_with_stream_chunks(_step_result({}), ["Hel", "lo"])

    assert result.observed_output["stream_chunks"] == ["Hel", "lo"]
    assert result.observed_output["stream_text"] == "Hello"


def test_tool_message_serializes_side_effect_result() -> None:
    message = tool_message(
        {"id": "call_shell"},
        SideEffectResult(
            kind="shell",
            allowed=True,
            receipt=_receipt(),
            output={"ok": True},
        ),
        attestation_id="attestation_tool",
    )

    assert message["role"] == "tool"
    assert message["tool_call_id"] == "call_shell"
    content = json.loads(message["content"])
    assert content == {
        "allowed": True,
        "attestation_id": "attestation_tool",
        "output": {"ok": True},
        "receipt_id": "receipt_tool",
        "summary": "allowed",
    }


def test_tool_result_attestation_hashes_replayed_payload() -> None:
    attestation = tool_result_attestation(
        task_id="task_tool_dispatch",
        case_file_id="case_tool_dispatch",
        tool_call={"id": "call_shell", "name": "shell.execute", "arguments": {"command": "status"}},
        side_effect=SideEffectResult(
            kind="shell",
            allowed=True,
            receipt=_receipt(),
            output={"result": "ok"},
        ),
    )

    assert attestation.id == "attestation_task_tool_dispatch_call_shell"
    assert attestation.case_file_id == "case_tool_dispatch"
    assert attestation.tool_name == "shell.execute"
    assert attestation.tool_identity == "call_shell"
    assert attestation.command == "status"
    assert attestation.output_hash
    assert attestation.receipt_id == "receipt_tool"
    assert attestation.status == "attested"


def _step_result(observed_output: dict[str, object]) -> RunnerStepResult:
    return RunnerStepResult(
        id="runner_step_result_tool_dispatch",
        request_id="runner_step_request_tool_dispatch",
        run_id="run_tool_dispatch",
        task_id="task_tool_dispatch",
        phase="act",
        runner=RunnerMetadata(
            id="runner_fixture",
            name="Fixture Runner",
            adapter="fixture",
            adapter_version="0.1.0",
            mode="fixture",
            capabilities=["prompt.read", "result.structured", "shell.execute"],
            metadata={"contract_test": True},
        ),
        status="completed",
        summary="completed",
        observed_output=observed_output,
        created_at=datetime.now(UTC),
    )


def _receipt() -> CapabilityReceipt:
    return CapabilityReceipt(
        id="receipt_tool",
        task_id="task_tool_dispatch",
        actor="runner:fixture",
        capability="shell.execute",
        target="fixture-action",
        policy_profile="trusted-local",
        fail_open=False,
        reason="allowed",
        result=ReceiptResult(status="passed", summary="allowed"),
        redacted=True,
        created_at=datetime.now(UTC),
    )
