from craik.contracts.models import CompiledPrompt, PromptSection
from craik.runtime.codex_adapter import CodexRunnerAdapter, request_from_compiled_prompt
from craik.runtime.runner_metadata import runner_metadata_snapshot


def test_runner_metadata_snapshot_includes_trust_and_redacts_runner_specific_data() -> None:
    adapter = CodexRunnerAdapter(metadata_extra={"api_token": "redaction-fixture-value"})

    snapshot = runner_metadata_snapshot(adapter.metadata)

    assert snapshot["runner_id"] == "codex"
    assert snapshot["adapter"] == "codex"
    assert snapshot["adapter_version"] == "0.2.0-preview"
    assert snapshot["execution_mode"] == "fixture"
    assert snapshot["trust_profile"]["level"] == "medium"
    assert snapshot["trust_profile"]["default_grant_posture"] == "prompt-for-approval"
    assert snapshot["runner_specific"]["api_token"] == "[REDACTED]"
    assert any(item["name"] == "shell.execute" for item in snapshot["capability_profile"])


def test_adapter_outputs_copy_runner_metadata_to_receipt_and_handoff_inputs() -> None:
    result = CodexRunnerAdapter().run(request_from_compiled_prompt(_compiled_prompt()))

    snapshot = result.outputs["runner_metadata"]
    receipt_input = result.outputs["receipt_inputs"][0]
    handoff_input = result.outputs["handoff_input"]

    assert snapshot["runner_id"] == "codex"
    assert receipt_input["result"]["metadata"]["runner_metadata"] == snapshot
    assert handoff_input["runner_metadata"] == [snapshot]


def _compiled_prompt() -> CompiledPrompt:
    return CompiledPrompt(
        id="prompt_review_docs_codex",
        task_id="task_review_docs",
        case_file_id="case_review_docs",
        policy_envelope_id="policy_task_review_docs",
        runner_id="codex",
        runner_mode="live",
        capability_grant_ids=["grant_repo_write"],
        expected_output_schemas=["craik.runner_adapter_result", "craik.handoff"],
        context_omissions=["GitHub issue and pull request state was not loaded."],
        stop_conditions=["Stop before using denied capabilities."],
        sections=[PromptSection(title="Task", body="Review docs.")],
        prompt="## Task\nReview docs.",
    )
