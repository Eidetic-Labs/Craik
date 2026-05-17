from datetime import UTC, datetime

import pytest

from craik.contracts.models import CompiledPrompt, PromptSection, RunnerAdapterRequest
from craik.runtime.runners.claude_adapter import (
    ClaudeRunnerAdapter,
    ClaudeRunnerRequestError,
    request_from_compiled_prompt,
)
from craik.runtime.runners.runners import RunnerAdapter, get_runner_capability_matrix


def test_claude_adapter_fixture_success_returns_normalized_outputs() -> None:
    compiled = _compiled_prompt()
    request = request_from_compiled_prompt(
        compiled,
        created_at=datetime(2026, 5, 16, 5, 30, tzinfo=UTC),
        context={"tests_run": ["uv run pytest"], "next_steps": ["Prepare handoff."]},
    )
    adapter = ClaudeRunnerAdapter()

    result = adapter.run(request)

    assert isinstance(adapter, RunnerAdapter)
    assert result.status == "completed"
    assert result.runner.id == "claude"
    assert result.runner.adapter_version == "0.2.0-preview"
    assert result.runner.metadata["adapter_mode"] == "fixture"
    assert result.outputs["prompt_handoff"]["prompt"] == compiled.prompt
    assert result.outputs["handoff_input"]["agent"] == "runner:claude"
    assert result.outputs["handoff_input"]["status"] == "completed"
    assert result.outputs["receipt_inputs"][0]["capability_grant_id"] == "grant_review_comment"
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "passed"
    assert result.artifacts == [compiled.case_file_id, compiled.policy_envelope_id]
    assert "fixture/prompt-handoff mode used" in result.diagnostics[0]


def test_claude_adapter_fixture_blocked_output() -> None:
    request = request_from_compiled_prompt(
        _compiled_prompt(),
        created_at=datetime(2026, 5, 16, 5, 31, tzinfo=UTC),
        context={
            "fixture_status": "blocked",
            "blocked_reason": "side effects must return through review",
            "risks": ["External tool authority unknown."],
        },
    )

    result = ClaudeRunnerAdapter().run(request)

    assert result.status == "blocked"
    assert "side effects must return through review" in result.summary
    assert result.outputs["handoff_input"]["status"] == "blocked"
    assert result.outputs["handoff_input"]["risks"] == ["External tool authority unknown."]
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "blocked"


def test_claude_adapter_fixture_failure_output() -> None:
    request = request_from_compiled_prompt(
        _compiled_prompt(),
        created_at=datetime(2026, 5, 16, 5, 32, tzinfo=UTC),
        context={
            "fixture_status": "failed",
            "failure_reason": "prompt handoff transcript missing",
            "diagnostics": ["missing transcript"],
        },
    )

    result = ClaudeRunnerAdapter().run(request)

    assert result.status == "failed"
    assert "prompt handoff transcript missing" in result.summary
    assert result.outputs["handoff_input"]["status"] == "failed"
    assert result.outputs["receipt_inputs"][0]["result"]["status"] == "failed"
    assert "missing transcript" in result.diagnostics


def test_claude_adapter_rejects_wrong_runner_request() -> None:
    request = request_from_compiled_prompt(_compiled_prompt())
    codex = get_runner_capability_matrix("codex").runner
    wrong_runner = RunnerAdapterRequest.model_validate(
        {**request.model_dump(mode="json", by_alias=True), "runner": codex}
    )

    with pytest.raises(ClaudeRunnerRequestError, match="cannot run"):
        ClaudeRunnerAdapter().run(wrong_runner)


def test_claude_request_builder_rejects_non_claude_prompt() -> None:
    prompt = _compiled_prompt().model_copy(update={"runner_id": "gemini"})

    with pytest.raises(ClaudeRunnerRequestError, match="compiled prompt runner"):
        request_from_compiled_prompt(prompt)


def _compiled_prompt() -> CompiledPrompt:
    return CompiledPrompt(
        id="prompt_review_docs_claude",
        task_id="task_review_docs",
        case_file_id="case_review_docs",
        policy_envelope_id="policy_task_review_docs",
        runner_id="claude",
        runner_mode="prompt-handoff",
        capability_grant_ids=["grant_review_comment"],
        expected_output_schemas=["craik.runner_adapter_result", "craik.handoff"],
        context_omissions=["Memory facts were not loaded into the case file."],
        stop_conditions=["Stop before using denied capabilities."],
        sections=[PromptSection(title="Task", body="Review docs.")],
        prompt="## Task\nReview docs.",
    )
