from datetime import UTC, datetime

import pytest

from craik.contracts.models import CompiledPrompt, PromptSection, RunnerAdapterRequest
from craik.runtime.codex_adapter import (
    CodexRunnerAdapter,
    CodexRunnerRequestError,
    request_from_compiled_prompt,
)
from craik.runtime.runners import RunnerAdapter, get_runner_capability_matrix


def test_codex_adapter_fixture_success_returns_normalized_outputs() -> None:
    compiled = _compiled_prompt()
    request = request_from_compiled_prompt(
        compiled,
        created_at=datetime(2026, 5, 16, 5, 0, tzinfo=UTC),
        context={"tests_run": ["uv run pytest"], "next_steps": ["Open PR."]},
    )
    adapter = CodexRunnerAdapter()

    result = adapter.run(request)

    assert isinstance(adapter, RunnerAdapter)
    assert result.status == "completed"
    assert result.runner.id == "codex"
    assert result.runner.adapter_version == "0.2.0-preview"
    assert result.runner.metadata["adapter_mode"] == "fixture"
    assert result.outputs["prompt_handoff"]["prompt"] == compiled.prompt
    assert result.outputs["handoff_input"]["status"] == "completed"
    assert result.outputs["handoff_input"]["tests_run"] == ["uv run pytest"]
    assert result.outputs["receipt_inputs"][0]["capability_grant_id"] == "grant_repo_write"
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "passed"
    assert result.artifacts == [compiled.case_file_id, compiled.policy_envelope_id]
    assert "fixture/prompt-handoff mode used" in result.diagnostics[0]


def test_codex_adapter_fixture_blocked_output() -> None:
    request = request_from_compiled_prompt(
        _compiled_prompt(),
        created_at=datetime(2026, 5, 16, 5, 1, tzinfo=UTC),
        context={
            "fixture_status": "blocked",
            "blocked_reason": "missing approval for shell.execute",
            "risks": ["Approval missing."],
        },
    )

    result = CodexRunnerAdapter().run(request)

    assert result.status == "blocked"
    assert "missing approval for shell.execute" in result.summary
    assert result.outputs["handoff_input"]["status"] == "blocked"
    assert result.outputs["handoff_input"]["risks"] == ["Approval missing."]
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "blocked"


def test_codex_adapter_fixture_failure_output() -> None:
    request = request_from_compiled_prompt(
        _compiled_prompt(),
        created_at=datetime(2026, 5, 16, 5, 2, tzinfo=UTC),
        context={
            "fixture_status": "failed",
            "failure_reason": "adapter process exited non-zero",
            "diagnostics": ["exit status 2"],
        },
    )

    result = CodexRunnerAdapter().run(request)

    assert result.status == "failed"
    assert "adapter process exited non-zero" in result.summary
    assert result.outputs["handoff_input"]["status"] == "failed"
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "failed"
    assert "exit status 2" in result.diagnostics


def test_codex_adapter_rejects_wrong_runner_request() -> None:
    request = request_from_compiled_prompt(_compiled_prompt())
    claude = get_runner_capability_matrix("claude").runner
    wrong_runner = RunnerAdapterRequest.model_validate(
        {**request.model_dump(mode="json", by_alias=True), "runner": claude}
    )

    with pytest.raises(CodexRunnerRequestError, match="cannot run"):
        CodexRunnerAdapter().run(wrong_runner)


def test_codex_request_builder_rejects_non_codex_prompt() -> None:
    prompt = _compiled_prompt().model_copy(update={"runner_id": "gemini"})

    with pytest.raises(CodexRunnerRequestError, match="compiled prompt runner"):
        request_from_compiled_prompt(prompt)


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
