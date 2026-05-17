"""Provider transport protocol and fixture transport."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from craik.contracts.models import RunnerResultStatus

ProviderFamily = Literal["openai", "anthropic"]


class ProviderTransport(Protocol):
    """Provider wire transport that yields normalized response chunks."""

    @property
    def family(self) -> ProviderFamily:
        """Provider API family this transport speaks."""
        ...

    def send(self, payload: dict[str, Any], *, stream: bool) -> Iterator[dict[str, Any]]:
        """Send one provider payload and yield one or more response chunks."""
        ...


@dataclass(frozen=True)
class FixtureTransport:
    """Deterministic provider transport for tests and non-live runs."""

    family: ProviderFamily
    model: str
    response_id: str = "provider_response_fixture"
    phase: str = "fixture"
    status: RunnerResultStatus = "completed"

    def send(self, payload: dict[str, Any], *, stream: bool) -> Iterator[dict[str, Any]]:
        """Yield a deterministic provider-shaped fixture response."""
        _ = (payload, stream)
        yield _fixture_response(
            provider_family=self.family,
            model=self.model,
            response_id=self.response_id,
            phase=self.phase,
            status=self.status,
        )


def _fixture_response(
    *,
    provider_family: ProviderFamily,
    model: str,
    response_id: str,
    phase: str,
    status: RunnerResultStatus,
) -> dict[str, Any]:
    text = f"{provider_family} fixture completed {phase} with status {status}."
    structured = {
        "phase": phase,
        "status": status,
        "summary": text,
    }
    if provider_family == "openai":
        return {
            "id": response_id,
            "model": model,
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": text}]},
                {
                    "type": "function_call",
                    "id": f"fc_{phase}",
                    "call_id": f"call_{phase}",
                    "name": "record_runner_step",
                    "arguments": "{}",
                },
            ],
            "usage": {"input_tokens": 20, "output_tokens": 10, "total_tokens": 30},
        }
    return {
        "id": response_id,
        "model": model,
        "content": [
            {"type": "text", "text": text},
            {
                "type": "tool_use",
                "id": f"toolu_{phase}",
                "name": "craik_structured_output",
                "input": structured,
            },
        ],
        "usage": {"input_tokens": 22, "output_tokens": 11},
    }
