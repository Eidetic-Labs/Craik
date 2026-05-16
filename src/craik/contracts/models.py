"""Pydantic models for Craik's v0.1 contract surface."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1.0"

Priority = Literal["low", "normal", "high", "urgent"]
TaskMode = Literal["plan", "review", "implement", "verify"]
MemoryBackend = Literal["ephemeral", "local", "stigmem"]
MemoryScope = Literal["local", "team", "company", "public"]
PolicyProfile = Literal["strict", "trusted-local", "automation", "custom"]
ProposalOperation = Literal["add", "update", "invalidate"]
TrustClass = Literal["observed", "reported", "inferred", "policy", "external", "stale-risk"]
ContradictionStatus = Literal["open", "resolved", "ignored"]
WorkGraphEventType = Literal[
    "created",
    "depends_on",
    "verified_by",
    "contradicts",
    "supersedes",
    "implements",
    "blocks",
]
ReceiptStatus = Literal["passed", "failed", "blocked", "denied", "skipped"]


class CraikModel(BaseModel):
    """Base model for strict, alias-aware Craik contracts."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class EvidenceReference(CraikModel):
    """Reference to source material used to support a contract assertion."""

    schema_: Literal["craik.evidence_reference"] = Field(
        default="craik.evidence_reference",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    source: str
    kind: Literal["file", "url", "command", "fact", "issue", "pull_request", "handoff", "other"]
    locator: str
    summary: str
    captured_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Assumption(CraikModel):
    """An unresolved assumption that must not be promoted to fact without evidence."""

    schema_: Literal["craik.assumption"] = Field(default="craik.assumption", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    statement: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    status: Literal["open", "validated", "rejected"] = "open"


class IntentLock(CraikModel):
    """Stable task intent used to detect scope drift during a run."""

    schema_: Literal["craik.intent_lock"] = Field(default="craik.intent_lock", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    original_request: str
    objective: str
    accepted_interpretation: str
    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    allowed_autonomy: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)
    scope_change_rules: list[str] = Field(default_factory=list)
    created_at: datetime


class TaskRequest(CraikModel):
    """Work requested by a user, system, or another agent."""

    schema_: Literal["craik.task_request"] = Field(default="craik.task_request", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    title: str
    objective: str
    project_id: str
    requested_by: str
    priority: Priority = "normal"
    mode: TaskMode
    constraints: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    created_at: datetime


class RepoProfile(CraikModel):
    """Repository configuration for a project."""

    type: Literal["git"]
    local_path: str
    remote: str | None = None
    default_branch: str = "main"


class DocsProfile(CraikModel):
    """Documentation paths and immutable areas for a project."""

    paths: list[str] = Field(default_factory=list)
    immutable_paths: list[str] = Field(default_factory=list)


class MemoryProfile(CraikModel):
    """Configured memory backend for a project."""

    backend: MemoryBackend
    scope: MemoryScope = "team"


class ProjectProfile(CraikModel):
    """Project configuration Craik can reason about."""

    schema_: Literal["craik.project_profile"] = Field(
        default="craik.project_profile",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    name: str
    repo: RepoProfile
    docs: DocsProfile = Field(default_factory=DocsProfile)
    memory: MemoryProfile
    policies: list[str] = Field(default_factory=list)


class PolicyEnvelope(CraikModel):
    """Runtime authority and obligations for a task."""

    schema_: Literal["craik.policy_envelope"] = Field(
        default="craik.policy_envelope",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    actor: str
    profile: PolicyProfile
    fail_open: bool = False
    allowed_capabilities: list[str] = Field(default_factory=list)
    denied_capabilities: list[str] = Field(default_factory=list)
    approval_required: list[str] = Field(default_factory=list)
    verification_required: list[str] = Field(default_factory=list)
    handoff_required: bool = True
    receipt_required: bool = True
    redaction_required: bool = True


class CapabilityTarget(CraikModel):
    """Scope of a capability grant."""

    repo: str | None = None
    paths: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityGrant(CraikModel):
    """Concrete permission for an action family."""

    schema_: Literal["craik.capability_grant"] = Field(
        default="craik.capability_grant",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    capability: str
    target: CapabilityTarget
    operations: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    reason: str
    approved_by: str


class ReceiptResult(CraikModel):
    """Redacted result summary for an auditable action."""

    status: ReceiptStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityReceipt(CraikModel):
    """Record of an important action performed under policy."""

    schema_: Literal["craik.capability_receipt"] = Field(
        default="craik.capability_receipt",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    actor: str
    capability: str
    target: str
    policy_profile: PolicyProfile
    fail_open: bool = False
    reason: str
    result: ReceiptResult
    redacted: bool = True
    created_at: datetime


class FactValue(CraikModel):
    """Proposed fact payload for memory updates."""

    entity: str
    relation: str
    value: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    scope: MemoryScope
    trust_class: TrustClass


class MemoryProposal(CraikModel):
    """Reviewable memory update proposal."""

    schema_: Literal["craik.memory_proposal"] = Field(
        default="craik.memory_proposal",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    operation: ProposalOperation
    fact: FactValue
    evidence: list[EvidenceReference] = Field(default_factory=list)
    requires_approval: bool = True


class MemoryRequiredCapabilities(CraikModel):
    """Minimum memory backend behaviors Craik depends on."""

    health: bool
    metadata: bool
    fact_write: bool
    fact_query: bool
    fact_get: bool
    fact_provenance: bool


class MemoryOptionalCapabilities(CraikModel):
    """Optional memory backend behaviors Craik can use when available."""

    recall: bool = False
    conflicts: bool = False
    source_attestation: Literal["warn", "enforce", "off"] = "off"
    federation: bool = False


class MemoryBackendCapabilities(CraikModel):
    """Detected memory backend capability snapshot."""

    schema_: Literal["craik.memory_backend_capabilities"] = Field(
        default="craik.memory_backend_capabilities",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    backend: MemoryBackend
    node_url: str | None = None
    node_id: str | None = None
    auth_required: bool = False
    required: MemoryRequiredCapabilities
    optional: MemoryOptionalCapabilities = Field(default_factory=MemoryOptionalCapabilities)
    checked_at: datetime


class ContradictionReport(CraikModel):
    """Incompatible assertions that need resolution."""

    schema_: Literal["craik.contradiction_report"] = Field(
        default="craik.contradiction_report",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    facts: list[str] = Field(min_length=2)
    summary: str
    affected_artifacts: list[str] = Field(default_factory=list)
    proposed_resolution: str | None = None
    status: ContradictionStatus = "open"
    owner: str | None = None


class WorkGraphEvent(CraikModel):
    """Event that updates the work graph."""

    schema_: Literal["craik.work_graph_event"] = Field(
        default="craik.work_graph_event",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    type: WorkGraphEventType
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CaseFile(CraikModel):
    """Task-specific context assembled before execution."""

    schema_: Literal["craik.case_file"] = Field(default="craik.case_file", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    objective: str
    policy_envelope_id: str
    intent_lock_id: str | None = None
    facts: list[FactValue] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    docs: list[str] = Field(default_factory=list)
    adrs: list[str] = Field(default_factory=list)
    repo_state: dict[str, Any] = Field(default_factory=dict)
    github_state: dict[str, Any] = Field(default_factory=dict)
    recent_handoffs: list[str] = Field(default_factory=list)
    stale_risks: list[str] = Field(default_factory=list)
    contradictions: list[ContradictionReport] = Field(default_factory=list)
    verification_plan: list[str] = Field(default_factory=list)
    context_budget: dict[str, Any] = Field(default_factory=dict)


class Handoff(CraikModel):
    """Durable run summary for future agents."""

    schema_: Literal["craik.handoff"] = Field(default="craik.handoff", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str
    intent_lock_id: str | None = None
    agent: str
    summary: str
    completed_actions: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)
    tests_run: list[str] = Field(default_factory=list)
    facts_learned: list[str] = Field(default_factory=list)
    facts_invalidated: list[str] = Field(default_factory=list)
    contradictions_opened: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    created_at: datetime
