"""Runner-related Craik contract models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from craik.contracts.models.base import (
    CraikModel,
    RunnerCapabilitySupport,
    RunnerGrantPosture,
    RunnerMode,
    RunnerResultStatus,
    RunnerTrustLevel,
    TaskRunPhase,
)


class RunnerMetadata(CraikModel):
    """Stable identity and capability summary for a runner adapter."""

    schema_: Literal["craik.runner_metadata"] = Field(
        default="craik.runner_metadata",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    name: str
    adapter: str
    adapter_version: str
    mode: RunnerMode
    capabilities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunnerCapability(CraikModel):
    """One normalized runner capability entry used by policy and prompt compilation."""

    name: str
    support: RunnerCapabilitySupport
    grant_required: bool = True
    notes: str | None = None


class RunnerTrustProfile(CraikModel):
    """Default trust boundary and grant posture for a runner."""

    level: RunnerTrustLevel
    boundary: str
    default_grant_posture: RunnerGrantPosture = "deny-by-default"
    requires_receipts: bool = True
    requires_redaction: bool = True
    notes: list[str] = Field(default_factory=list)


class RunnerCapabilityMatrix(CraikModel):
    """Validated capability and trust profile for a runner adapter."""

    schema_: Literal["craik.runner_capability_matrix"] = Field(
        default="craik.runner_capability_matrix",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    runner: RunnerMetadata
    trust: RunnerTrustProfile
    capabilities: list[RunnerCapability] = Field(default_factory=list)
    policy_notes: list[str] = Field(default_factory=list)


class RunnerAdapterRequest(CraikModel):
    """Normalized input handed from Craik core to a runner adapter."""

    schema_: Literal["craik.runner_adapter_request"] = Field(
        default="craik.runner_adapter_request",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    runner: RunnerMetadata
    task_request_id: str
    case_file_id: str
    policy_envelope_id: str
    capability_grant_ids: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RunnerAdapterResult(CraikModel):
    """Normalized output returned from a runner adapter to Craik core."""

    schema_: Literal["craik.runner_adapter_result"] = Field(
        default="craik.runner_adapter_result",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    request_id: str
    task_id: str
    runner: RunnerMetadata
    status: RunnerResultStatus
    summary: str
    outputs: dict[str, Any] = Field(default_factory=dict)
    receipt_ids: list[str] = Field(default_factory=list)
    handoff_id: str | None = None
    memory_proposal_ids: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)
    created_at: datetime


class RunnerStepRequest(CraikModel):
    """Normalized input for one governed runner loop step."""

    schema_: Literal["craik.runner_step_request"] = Field(
        default="craik.runner_step_request",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    run_id: str
    task_id: str
    phase: TaskRunPhase
    runner: RunnerMetadata
    policy_envelope_id: str
    intent_lock_id: str | None = None
    capability_grant_ids: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)
    input_prompt: str
    context: dict[str, Any] = Field(default_factory=dict)
    redaction_required: bool = True
    created_at: datetime


class RunnerStepResult(CraikModel):
    """Normalized output from one governed runner loop step."""

    schema_: Literal["craik.runner_step_result"] = Field(
        default="craik.runner_step_result",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    request_id: str
    run_id: str
    task_id: str
    phase: TaskRunPhase
    runner: RunnerMetadata
    status: RunnerResultStatus
    summary: str
    observed_output: dict[str, Any] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime
