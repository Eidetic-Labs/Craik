"""Schema registry for Craik runtime contracts."""

from __future__ import annotations

from pydantic import BaseModel

from craik.contracts.models import (
    Assumption,
    CapabilityGrant,
    CapabilityReceipt,
    CaseFile,
    ContradictionReport,
    EvidenceReference,
    Handoff,
    IntentLock,
    MemoryBackendCapabilities,
    MemoryProposal,
    PolicyEnvelope,
    ProjectProfile,
    TaskRequest,
    WorkGraphEvent,
)

type ContractModel = type[BaseModel]

CONTRACT_REGISTRY: dict[str, ContractModel] = {
    "craik.assumption": Assumption,
    "craik.capability_grant": CapabilityGrant,
    "craik.capability_receipt": CapabilityReceipt,
    "craik.case_file": CaseFile,
    "craik.contradiction_report": ContradictionReport,
    "craik.evidence_reference": EvidenceReference,
    "craik.handoff": Handoff,
    "craik.intent_lock": IntentLock,
    "craik.memory_backend_capabilities": MemoryBackendCapabilities,
    "craik.memory_proposal": MemoryProposal,
    "craik.policy_envelope": PolicyEnvelope,
    "craik.project_profile": ProjectProfile,
    "craik.task_request": TaskRequest,
    "craik.work_graph_event": WorkGraphEvent,
}


def schema_names() -> list[str]:
    """Return known schema names in stable order."""
    return sorted(CONTRACT_REGISTRY)


def schema_model(name: str) -> ContractModel:
    """Return the Pydantic model registered for a schema name."""
    return CONTRACT_REGISTRY[name]
