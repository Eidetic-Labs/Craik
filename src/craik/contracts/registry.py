"""Schema registry for Craik runtime contracts."""

from __future__ import annotations

from pydantic import BaseModel

from craik.contracts.models import (
    AgentOnboarding,
    Assumption,
    CapabilityGrant,
    CapabilityReceipt,
    CaseFile,
    ContradictionReport,
    EvidenceReference,
    Handoff,
    IntentLock,
    MemoryBackendCapabilities,
    MemoryDiff,
    MemoryImpactPreview,
    MemoryProposal,
    PolicyEnvelope,
    ProjectProfile,
    RunnerAdapterRequest,
    RunnerAdapterResult,
    RunnerMetadata,
    TaskRequest,
    WorkGraphEvent,
    WorkGraphExport,
)

type ContractModel = type[BaseModel]

CONTRACT_REGISTRY: dict[str, ContractModel] = {
    "craik.agent_onboarding": AgentOnboarding,
    "craik.assumption": Assumption,
    "craik.capability_grant": CapabilityGrant,
    "craik.capability_receipt": CapabilityReceipt,
    "craik.case_file": CaseFile,
    "craik.contradiction_report": ContradictionReport,
    "craik.evidence_reference": EvidenceReference,
    "craik.handoff": Handoff,
    "craik.intent_lock": IntentLock,
    "craik.memory_backend_capabilities": MemoryBackendCapabilities,
    "craik.memory_diff": MemoryDiff,
    "craik.memory_impact_preview": MemoryImpactPreview,
    "craik.memory_proposal": MemoryProposal,
    "craik.policy_envelope": PolicyEnvelope,
    "craik.project_profile": ProjectProfile,
    "craik.runner_adapter_request": RunnerAdapterRequest,
    "craik.runner_adapter_result": RunnerAdapterResult,
    "craik.runner_metadata": RunnerMetadata,
    "craik.task_request": TaskRequest,
    "craik.work_graph_export": WorkGraphExport,
    "craik.work_graph_event": WorkGraphEvent,
}


def schema_names() -> list[str]:
    """Return known schema names in stable order."""
    return sorted(CONTRACT_REGISTRY)


def schema_model(name: str) -> ContractModel:
    """Return the Pydantic model registered for a schema name."""
    return CONTRACT_REGISTRY[name]
