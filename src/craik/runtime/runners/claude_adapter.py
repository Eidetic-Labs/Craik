"""Claude-compatible runner adapter preview."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from craik.contracts.models import CompiledPrompt, RunnerAdapterRequest, RunnerResultStatus
from craik.runtime.runners.preview_adapter import (
    PREVIEW_ADAPTER_VERSION,
    PreviewFixtureAdapter,
)
from craik.runtime.runners.preview_adapter import (
    request_from_compiled_prompt as _preview_request_from_compiled_prompt,
)

CLAUDE_RUNNER_ID = "claude"
CLAUDE_ADAPTER_VERSION = PREVIEW_ADAPTER_VERSION


class ClaudeRunnerAdapterError(RuntimeError):
    """Base error for Claude adapter failures."""


class ClaudeRunnerRequestError(ClaudeRunnerAdapterError):
    """Raised when a request cannot be handled by the Claude adapter."""


@dataclass(frozen=True)
class ClaudeRunnerAdapter(PreviewFixtureAdapter):
    """Preview adapter for Claude-compatible prompt handoff and fixture runs."""

    runner_id: str = CLAUDE_RUNNER_ID
    display_name: str = "Claude"
    live_mode: str = "prompt-handoff"
    adapter_version: str = CLAUDE_ADAPTER_VERSION
    fixture_status: RunnerResultStatus = "completed"
    live_available: bool = False
    executable: str | None = None
    metadata_extra: dict[str, Any] = field(default_factory=dict)
    request_error: type[RuntimeError] = ClaudeRunnerRequestError


def request_from_compiled_prompt(
    compiled: CompiledPrompt,
    *,
    created_at: datetime | None = None,
    adapter: ClaudeRunnerAdapter | None = None,
    context: dict[str, Any] | None = None,
) -> RunnerAdapterRequest:
    """Build a Claude runner request from a compiled prompt."""
    return _preview_request_from_compiled_prompt(
        compiled,
        runner_id=CLAUDE_RUNNER_ID,
        adapter_factory=ClaudeRunnerAdapter,
        request_error=ClaudeRunnerRequestError,
        created_at=created_at,
        adapter=adapter,
        context=context,
    )
