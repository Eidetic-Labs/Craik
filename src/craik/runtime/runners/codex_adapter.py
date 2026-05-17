"""Codex-compatible runner adapter preview."""

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

CODEX_RUNNER_ID = "codex"
CODEX_ADAPTER_VERSION = PREVIEW_ADAPTER_VERSION


class CodexRunnerAdapterError(RuntimeError):
    """Base error for Codex adapter failures."""


class CodexRunnerRequestError(CodexRunnerAdapterError):
    """Raised when a request cannot be handled by the Codex adapter."""


@dataclass(frozen=True)
class CodexRunnerAdapter(PreviewFixtureAdapter):
    """Preview adapter for Codex-compatible prompt handoff and fixture runs."""

    runner_id: str = CODEX_RUNNER_ID
    display_name: str = "Codex"
    live_mode: str = "live"
    adapter_version: str = CODEX_ADAPTER_VERSION
    fixture_status: RunnerResultStatus = "completed"
    live_available: bool = False
    executable: str | None = None
    metadata_extra: dict[str, Any] = field(default_factory=dict)
    request_error: type[RuntimeError] = CodexRunnerRequestError


def request_from_compiled_prompt(
    compiled: CompiledPrompt,
    *,
    created_at: datetime | None = None,
    adapter: CodexRunnerAdapter | None = None,
    context: dict[str, Any] | None = None,
) -> RunnerAdapterRequest:
    """Build a Codex runner request from a compiled prompt."""
    return _preview_request_from_compiled_prompt(
        compiled,
        runner_id=CODEX_RUNNER_ID,
        adapter_factory=CodexRunnerAdapter,
        request_error=CodexRunnerRequestError,
        created_at=created_at,
        adapter=adapter,
        context=context,
    )
