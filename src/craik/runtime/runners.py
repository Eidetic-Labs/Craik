"""Runner adapter protocol and fixture implementation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from craik.contracts.models import (
    RunnerAdapterRequest,
    RunnerAdapterResult,
    RunnerMetadata,
)


@runtime_checkable
class RunnerAdapter(Protocol):
    """Interface future runner adapters must implement."""

    @property
    def metadata(self) -> RunnerMetadata:
        """Return stable runner identity and capability metadata."""

    def run(self, request: RunnerAdapterRequest) -> RunnerAdapterResult:
        """Run or guide one task request and return normalized output."""


@dataclass(frozen=True)
class FixtureRunnerAdapter:
    """Deterministic adapter for contract tests and adapter scaffolding."""

    metadata: RunnerMetadata
    result: RunnerAdapterResult

    def run(self, request: RunnerAdapterRequest) -> RunnerAdapterResult:
        """Return the configured fixture result after validating request linkage."""
        if request.runner.id != self.metadata.id:
            raise ValueError("runner request metadata does not match adapter metadata")
        if self.result.request_id != request.id:
            raise ValueError("runner fixture result does not match request id")
        return self.result
