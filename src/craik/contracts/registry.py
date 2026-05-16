"""Schema registry for Craik runtime contracts."""

from __future__ import annotations

from pydantic import BaseModel

from craik.contracts.models import (
    AdjudicationOutcome,
    AgentOnboarding,
    AgentRole,
    Assumption,
    CapabilityGrant,
    CapabilityReceipt,
    CaseFile,
    CompiledPrompt,
    ContradictionReport,
    DebateSummary,
    DebateTurn,
    EvidenceReference,
    Handoff,
    HumanDelegationPoint,
    InstructionProvenance,
    InstructionSource,
    InstructionSourceRegistry,
    InstructionSourceSnapshot,
    IntentLock,
    MemoryBackendCapabilities,
    MemoryDiff,
    MemoryImpactPreview,
    MemoryProposal,
    PolicyEnvelope,
    ProjectProfile,
    ReviewRequest,
    ReviewResult,
    RunnerAdapterRequest,
    RunnerAdapterResult,
    RunnerCapabilityMatrix,
    RunnerMetadata,
    RunnerStepRequest,
    RunnerStepResult,
    RunOutput,
    ScopeChangeRequest,
    ScopeChangeResult,
    TaskRequest,
    TaskRun,
    WorkerResult,
    WorkGraphEvent,
    WorkGraphExport,
)

type ContractModel = type[BaseModel]

CONTRACT_REGISTRY: dict[str, ContractModel] = {
    "craik.adjudication_outcome": AdjudicationOutcome,
    "craik.agent_onboarding": AgentOnboarding,
    "craik.agent_role": AgentRole,
    "craik.assumption": Assumption,
    "craik.capability_grant": CapabilityGrant,
    "craik.capability_receipt": CapabilityReceipt,
    "craik.case_file": CaseFile,
    "craik.compiled_prompt": CompiledPrompt,
    "craik.contradiction_report": ContradictionReport,
    "craik.debate_summary": DebateSummary,
    "craik.debate_turn": DebateTurn,
    "craik.evidence_reference": EvidenceReference,
    "craik.handoff": Handoff,
    "craik.human_delegation_point": HumanDelegationPoint,
    "craik.instruction_source": InstructionSource,
    "craik.instruction_provenance": InstructionProvenance,
    "craik.instruction_source_registry": InstructionSourceRegistry,
    "craik.instruction_source_snapshot": InstructionSourceSnapshot,
    "craik.intent_lock": IntentLock,
    "craik.memory_backend_capabilities": MemoryBackendCapabilities,
    "craik.memory_diff": MemoryDiff,
    "craik.memory_impact_preview": MemoryImpactPreview,
    "craik.memory_proposal": MemoryProposal,
    "craik.policy_envelope": PolicyEnvelope,
    "craik.project_profile": ProjectProfile,
    "craik.review_request": ReviewRequest,
    "craik.review_result": ReviewResult,
    "craik.run_output": RunOutput,
    "craik.scope_change_request": ScopeChangeRequest,
    "craik.scope_change_result": ScopeChangeResult,
    "craik.runner_adapter_request": RunnerAdapterRequest,
    "craik.runner_adapter_result": RunnerAdapterResult,
    "craik.runner_capability_matrix": RunnerCapabilityMatrix,
    "craik.runner_metadata": RunnerMetadata,
    "craik.runner_step_request": RunnerStepRequest,
    "craik.runner_step_result": RunnerStepResult,
    "craik.task_run": TaskRun,
    "craik.task_request": TaskRequest,
    "craik.work_graph_export": WorkGraphExport,
    "craik.work_graph_event": WorkGraphEvent,
    "craik.worker_result": WorkerResult,
}


def schema_names() -> list[str]:
    """Return known schema names in stable order."""
    return sorted(CONTRACT_REGISTRY)


def schema_model(name: str) -> ContractModel:
    """Return the Pydantic model registered for a schema name."""
    return CONTRACT_REGISTRY[name]
