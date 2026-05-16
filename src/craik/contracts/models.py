"""Pydantic models for Craik's v0.1 contract surface."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "0.1.0"

Priority = Literal["low", "normal", "high", "urgent"]
TaskMode = Literal["plan", "review", "implement", "verify"]
MemoryBackend = Literal["ephemeral", "local", "stigmem"]
MemoryScope = Literal["local", "team", "company", "public"]
PolicyProfile = Literal["strict", "trusted-local", "automation", "custom"]
ProposalOperation = Literal["add", "update", "invalidate"]
ProposalStatus = Literal["pending", "approved", "rejected"]
TrustClass = Literal["observed", "reported", "inferred", "policy", "external", "stale-risk"]
MemoryDiffChangeKind = Literal["created", "approved", "rejected", "written", "failed", "read"]
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
RunStatus = Literal["completed", "incomplete", "blocked", "failed"]
TaskRunPhase = Literal["plan", "act", "observe", "evaluate", "continue", "stop"]
TaskRunStatus = Literal["pending", "running", "completed", "blocked", "failed", "interrupted"]
RunnerMode = Literal["fixture", "prompt-handoff", "live"]
RunnerResultStatus = Literal["completed", "blocked", "failed", "partial"]
WorkerResultStatus = Literal["completed", "blocked", "failed", "partial"]
DebateTurnPosition = Literal["supports", "opposes", "clarifies", "questions", "blocks"]
DebateOutcome = Literal["agreement", "unresolved_disagreement", "contradiction_opened"]
ReviewRequestStatus = Literal["open", "completed", "cancelled"]
ReviewDecision = Literal["approved", "changes_requested", "blocked", "deferred"]
AdjudicationDecision = Literal["accepted", "rejected", "revised", "deferred"]
FindingSeverity = Literal["info", "low", "medium", "high", "critical"]
FindingReviewStatus = Literal["reviewable", "adjudicated", "dismissed"]
RuntimeCriticFindingType = Literal[
    "unsupported_claim",
    "policy_violation",
    "scope_drift",
    "missing_validation",
    "stale_evidence",
    "missing_handoff",
    "unredacted_sensitive_content",
    "risky_memory_write",
    "other",
]
RedTeamFindingType = Literal[
    "prompt_injection",
    "privilege_escalation",
    "data_exfiltration",
    "destructive_action",
    "policy_bypass",
    "memory_poisoning",
    "adversarial_input",
    "other",
]
QualityScoreBand = Literal["excellent", "adequate", "poor"]
HandoffQualityComponentName = Literal[
    "summary",
    "completed_actions",
    "validation_records",
    "receipt_links",
    "evidence_links",
    "context_debt",
    "unresolved_risks",
    "next_steps",
    "self_audit",
]
ContextDebtKind = Literal[
    "omitted_doc",
    "excluded_doc",
    "stale_instruction",
    "unresolved_assumption",
    "missing_external_state",
    "missing_memory_facts",
    "active_instruction_constraint",
    "missing_case_file",
    "other",
]
ContextDebtStatus = Literal["created", "carried_forward", "resolved"]
ToolAttestationStatus = Literal["attested", "missing", "expired"]
FreshnessProbeStatus = Literal["fresh", "expiring", "expired", "missing"]
FreshnessProbeKind = Literal[
    "github_state",
    "documentation",
    "memory_fact",
    "tool_result",
    "external_state",
    "instruction_source",
    "other",
]
KnownTrapStatus = Literal["active", "expired", "contradicted"]
KnownTrapKind = Literal[
    "workflow",
    "policy",
    "tool",
    "memory",
    "documentation",
    "security",
    "other",
]
ScratchpadStatus = Literal["active", "expired", "promoted", "discarded"]
UnknownStatus = Literal["unresolved", "resolved"]
UnknownResolutionSource = Literal[
    "user_input",
    "web_access",
    "repo_inspection",
    "tool_access",
    "memory_query",
    "external_wait",
    "other",
]
ContextRequestStatus = Literal["open", "fulfilled", "cancelled"]
ContextRequestKind = Literal[
    "user_input",
    "repo_inspection",
    "web_access",
    "tool_access",
    "memory_query",
    "external_state",
    "other",
]
ExitDisciplineStatus = Literal["complete", "blocked"]
SkillEntrypointKind = Literal["prompt", "script", "module", "workflow", "docs"]
SkillOmissionSeverity = Literal["low", "medium", "high", "critical"]
SkillScope = Literal["project", "global"]
PluginEntrypointKind = Literal["command", "module", "workflow", "service", "docs"]
PluginCapabilityRisk = Literal["low", "medium", "high", "critical"]
PluginCompatibilityStatus = Literal["supported", "experimental", "unsupported"]
PluginProbationStatus = Literal["probationary", "promoted", "rejected", "expired"]
PluginProbationDecisionKind = Literal["promote", "reject", "expire"]
PluginGrantStatus = Literal["allowed", "denied", "expired", "approval_required"]
HumanDelegationKind = Literal["approval", "clarification", "escalation", "ownership_transfer"]
HumanDelegationStatus = Literal["open", "resolved", "cancelled"]
ScopeChangeStatus = Literal["pending", "accepted", "rejected"]
InstructionSourceKind = Literal[
    "agents_md",
    "claude_md",
    "gemini_md",
    "hermes_md",
    "skills_md",
    "cursor_rules",
    "github_copilot_instructions",
    "codex_instructions",
    "policy_doc",
]
InstructionTrustBoundary = Literal["project", "repository", "organization", "user", "external"]
InstructionSourceHashStatus = Literal["unchanged", "changed", "missing", "new"]
DistilledInstructionCategory = Literal[
    "instruction",
    "policy",
    "preference",
    "command",
    "boundary",
    "handoff_rule",
    "memory_rule",
    "security_rule",
    "stale_risk",
]
DistilledInstructionPromotionStatus = Literal["proposed", "approved", "rejected", "deferred"]
InstructionPromotionDecision = Literal["approved", "rejected", "deferred"]
RecoveryStatus = Literal["clean_resume", "changed_state", "missing_prior_context"]
RunDeltaChangeKind = Literal["created", "updated", "removed", "unchanged"]
RunDeltaEntityType = Literal[
    "handoff",
    "case_file",
    "receipt",
    "contradiction",
    "instruction_constraint",
]
RunnerTrustLevel = Literal["low", "medium", "high"]
RunnerGrantPosture = Literal["deny-by-default", "prompt-for-approval", "allow-with-receipt"]
RunnerCapabilitySupport = Literal["unsupported", "prompt-handoff", "supported"]
AgentRoleKind = Literal[
    "orchestrator",
    "implementer",
    "verifier",
    "adversarial_reviewer",
    "policy_reviewer",
    "docs_reviewer",
    "memory_curator",
    "adjudicator",
]
AgentRoleAuthority = Literal["coordinate", "read", "propose", "review", "adjudicate", "implement"]


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
    discovery_include: list[str] = Field(default_factory=list)
    discovery_exclude: list[str] = Field(default_factory=list)


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


class AgentRole(CraikModel):
    """Policy-aware role definition for multi-agent coordination."""

    schema_: Literal["craik.agent_role"] = Field(default="craik.agent_role", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    kind: AgentRoleKind
    name: str
    description: str
    runner_id: str | None = None
    runner_mode: RunnerMode | None = None
    authority: list[AgentRoleAuthority] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    denied_capabilities: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None
    expected_input_schemas: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)
    handoff_required: bool = True
    receipt_required: bool = True
    redaction_required: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_role_contract(self) -> AgentRole:
        """Ensure roles carry enough authority and output boundary information."""
        if not self.authority:
            raise ValueError("agent roles require at least one authority value")
        if not self.expected_output_schemas:
            raise ValueError("agent roles require at least one expected output schema")
        required_authority: dict[AgentRoleKind, AgentRoleAuthority] = {
            "orchestrator": "coordinate",
            "implementer": "implement",
            "verifier": "review",
            "adversarial_reviewer": "review",
            "policy_reviewer": "review",
            "docs_reviewer": "review",
            "memory_curator": "review",
            "adjudicator": "adjudicate",
        }
        authority = required_authority[self.kind]
        if authority not in self.authority:
            raise ValueError(f"{self.kind} role requires {authority!r} authority")
        return self


class PromptSection(CraikModel):
    """Named deterministic section in a compiled runner prompt."""

    title: str
    body: str


class CompiledPrompt(CraikModel):
    """Policy-aware runner prompt compiled from Craik runtime state."""

    schema_: Literal["craik.compiled_prompt"] = Field(
        default="craik.compiled_prompt",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    case_file_id: str
    policy_envelope_id: str
    runner_id: str
    runner_mode: RunnerMode
    capability_grant_ids: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)
    context_omissions: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)
    sections: list[PromptSection] = Field(default_factory=list)
    prompt: str


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


class WorkerFinding(CraikModel):
    """One structured finding from a specialist worker."""

    summary: str
    severity: FindingSeverity = "info"
    evidence_ids: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)


class WorkerResult(CraikModel):
    """Typed output from a role-specific specialist agent."""

    schema_: Literal["craik.worker_result"] = Field(
        default="craik.worker_result",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    run_id: str | None = None
    role_id: str
    role_kind: AgentRoleKind
    runner: RunnerMetadata | None = None
    status: WorkerResultStatus
    summary: str
    findings: list[WorkerFinding] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    handoff_id: str | None = None
    diagnostics: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime


class RuntimeCriticFinding(CraikModel):
    """Reviewable, non-authoritative runtime critic finding."""

    schema_: Literal["craik.runtime_critic_finding"] = Field(
        default="craik.runtime_critic_finding",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    run_id: str | None = None
    handoff_id: str | None = None
    critic_role_id: str | None = None
    finding_type: RuntimeCriticFindingType
    severity: FindingSeverity = "medium"
    summary: str
    rationale: str
    affected_artifacts: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    authoritative: Literal[False] = False
    review_status: FindingReviewStatus = "reviewable"
    adjudication_id: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_review_boundary(self) -> RuntimeCriticFinding:
        """Keep critic findings actionable and non-authoritative until adjudication."""
        if self.review_status == "adjudicated" and not self.adjudication_id:
            raise ValueError("adjudicated critic findings require adjudication_id")
        if self.severity in {"high", "critical"} and not self.proposed_actions:
            raise ValueError("high-severity critic findings require proposed_actions")
        if self.finding_type in {"unsupported_claim", "stale_evidence"} and not self.evidence_ids:
            raise ValueError("evidence-related critic findings require evidence_ids")
        return self


class RedTeamFinding(CraikModel):
    """Reviewable, non-authoritative adversarial finding for high-risk work."""

    schema_: Literal["craik.red_team_finding"] = Field(
        default="craik.red_team_finding",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    run_id: str | None = None
    handoff_id: str | None = None
    red_team_role_id: str | None = None
    finding_type: RedTeamFindingType
    severity: FindingSeverity = "high"
    summary: str
    attack_path: str
    affected_artifacts: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    blocking: bool = False
    authoritative: Literal[False] = False
    review_status: FindingReviewStatus = "reviewable"
    adjudication_id: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_red_team_boundary(self) -> RedTeamFinding:
        """Require blockers to be actionable and keep findings reviewable."""
        if self.review_status == "adjudicated" and not self.adjudication_id:
            raise ValueError("adjudicated red-team findings require adjudication_id")
        if self.blocking and not self.proposed_actions:
            raise ValueError("blocking red-team findings require proposed_actions")
        if self.blocking and self.severity not in {"high", "critical"}:
            raise ValueError("blocking red-team findings must be high or critical severity")
        return self


class DebateTurn(CraikModel):
    """One structured contribution to an agent debate."""

    schema_: Literal["craik.debate_turn"] = Field(default="craik.debate_turn", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    debate_id: str
    role_id: str
    role_kind: AgentRoleKind
    worker_result_id: str | None = None
    position: DebateTurnPosition
    claim: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    assumption_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class DebateSummary(CraikModel):
    """Deterministic outcome summary for a bounded agent debate."""

    schema_: Literal["craik.debate_summary"] = Field(
        default="craik.debate_summary",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    debate_id: str
    topic: str
    turn_ids: list[str] = Field(default_factory=list)
    outcome: DebateOutcome
    summary: str
    agreements: list[str] = Field(default_factory=list)
    unresolved_disagreements: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_outcome_links(self) -> DebateSummary:
        """Require explicit disagreement or contradiction links for non-agreement outcomes."""
        if self.outcome == "unresolved_disagreement" and not self.unresolved_disagreements:
            raise ValueError("unresolved debate summaries require unresolved disagreement text")
        if self.outcome == "contradiction_opened" and not self.contradiction_ids:
            raise ValueError("contradiction debate summaries require contradiction ids")
        return self


class ReviewRequest(CraikModel):
    """Request from one role for bounded cross-agent review."""

    schema_: Literal["craik.review_request"] = Field(
        default="craik.review_request",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    requester_role_id: str
    reviewer_role_id: str
    reviewer_role_kind: AgentRoleKind
    subject_worker_result_ids: list[str] = Field(default_factory=list)
    subject_debate_summary_ids: list[str] = Field(default_factory=list)
    focus: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    status: ReviewRequestStatus = "open"
    due_at: datetime | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_subjects(self) -> ReviewRequest:
        """Require at least one worker result or debate summary under review."""
        if not self.subject_worker_result_ids and not self.subject_debate_summary_ids:
            raise ValueError("review requests require at least one review subject")
        return self


class ReviewResult(CraikModel):
    """Result returned by a specialist reviewer."""

    schema_: Literal["craik.review_result"] = Field(
        default="craik.review_result",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    review_request_id: str
    reviewer_role_id: str
    reviewer_role_kind: AgentRoleKind
    decision: ReviewDecision
    summary: str
    finding_ids: list[str] = Field(default_factory=list)
    worker_result_ids: list[str] = Field(default_factory=list)
    debate_summary_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    handoff_id: str | None = None
    created_at: datetime


class AdjudicatedFinding(CraikModel):
    """One finding decision made by an adjudicator."""

    source_worker_result_id: str | None = None
    source_finding_id: str | None = None
    source_review_result_id: str | None = None
    decision: AdjudicationDecision
    rationale: str
    revised_summary: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_revision(self) -> AdjudicatedFinding:
        """Require replacement text for revised findings."""
        if self.decision == "revised" and not self.revised_summary:
            raise ValueError("revised adjudicated findings require revised_summary")
        return self


class AdjudicationOutcome(CraikModel):
    """Final or deferred adjudicator decision over reviewed specialist outputs."""

    schema_: Literal["craik.adjudication_outcome"] = Field(
        default="craik.adjudication_outcome",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    adjudicator_role_id: str
    decision: AdjudicationDecision
    summary: str
    review_result_ids: list[str] = Field(default_factory=list)
    worker_result_ids: list[str] = Field(default_factory=list)
    debate_summary_ids: list[str] = Field(default_factory=list)
    adjudicated_findings: list[AdjudicatedFinding] = Field(default_factory=list)
    unresolved_disagreements: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    policy_review_result_ids: list[str] = Field(default_factory=list)
    adversarial_review_result_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_decision_payload(self) -> AdjudicationOutcome:
        """Ensure adjudication payloads explain their durable decision."""
        if self.decision == "deferred" and not self.unresolved_disagreements:
            raise ValueError("deferred adjudication requires unresolved disagreements")
        if self.decision != "deferred" and not self.adjudicated_findings:
            raise ValueError("non-deferred adjudication requires adjudicated findings")
        return self


class HumanDelegationPoint(CraikModel):
    """Human decision point that requires agent stop, clarification, or transfer."""

    schema_: Literal["craik.human_delegation_point"] = Field(
        default="craik.human_delegation_point",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    kind: HumanDelegationKind
    status: HumanDelegationStatus = "open"
    summary: str
    requested_decision: str
    requested_by: str
    owner: str | None = None
    role_id: str | None = None
    intent_lock_id: str | None = None
    policy_envelope_id: str | None = None
    contradiction_ids: list[str] = Field(default_factory=list)
    scope_change_request_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    resolved_at: datetime | None = None
    resolution: str | None = None

    @model_validator(mode="after")
    def validate_resolution(self) -> HumanDelegationPoint:
        """Require resolution details when a delegation point is resolved."""
        if self.status == "resolved" and not self.resolution:
            raise ValueError("resolved delegation points require resolution text")
        return self


class ScopeChangeRequest(CraikModel):
    """Request to change a task's accepted intent or authority boundary."""

    schema_: Literal["craik.scope_change_request"] = Field(
        default="craik.scope_change_request",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    intent_lock_id: str
    requested_by: str
    reason: str
    current_scope: list[str] = Field(default_factory=list)
    proposed_scope: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None
    delegation_id: str | None = None
    contradiction_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    status: ScopeChangeStatus = "pending"
    created_at: datetime

    @model_validator(mode="after")
    def validate_scope_delta(self) -> ScopeChangeRequest:
        """Require proposed scope for meaningful scope-change requests."""
        if not self.proposed_scope:
            raise ValueError("scope change requests require proposed scope")
        return self


class ScopeChangeResult(CraikModel):
    """Human decision for a requested scope change."""

    schema_: Literal["craik.scope_change_result"] = Field(
        default="craik.scope_change_result",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    scope_change_request_id: str
    decision: Literal["accepted", "rejected"]
    decided_by: str
    rationale: str
    updated_intent_lock_id: str | None = None
    policy_envelope_id: str | None = None
    contradiction_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_accepted_scope_change(self) -> ScopeChangeResult:
        """Accepted scope changes must point at the updated intent lock."""
        if self.decision == "accepted" and not self.updated_intent_lock_id:
            raise ValueError("accepted scope changes require updated_intent_lock_id")
        return self


INSTRUCTION_SOURCE_DEFAULT_PATHS: dict[InstructionSourceKind, str] = {
    "agents_md": "AGENTS.md",
    "claude_md": "CLAUDE.md",
    "gemini_md": "GEMINI.md",
    "hermes_md": "HERMES.md",
    "skills_md": "SKILLS.md",
    "cursor_rules": ".cursorrules",
    "github_copilot_instructions": ".github/copilot-instructions.md",
    "codex_instructions": ".codex/instructions.md",
    "policy_doc": "",
}


class InstructionSource(CraikModel):
    """Declared source file for runtime instruction distillation."""

    schema_: Literal["craik.instruction_source"] = Field(
        default="craik.instruction_source",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    kind: InstructionSourceKind
    path: str
    owner: str
    trust_boundary: InstructionTrustBoundary = "project"
    active: bool = True
    declared_by: str
    policy_envelope_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    @model_validator(mode="after")
    def validate_declared_path(self) -> InstructionSource:
        """Ensure standard source kinds use their canonical paths."""
        expected_path = INSTRUCTION_SOURCE_DEFAULT_PATHS[self.kind]
        if expected_path and self.path != expected_path:
            raise ValueError(f"{self.kind} instruction source path must be {expected_path!r}")
        if self.kind == "policy_doc" and not self.path:
            raise ValueError("policy_doc instruction sources require a declared path")
        return self


class InstructionSourceRegistry(CraikModel):
    """Project registry of declared instruction sources."""

    schema_: Literal["craik.instruction_source_registry"] = Field(
        default="craik.instruction_source_registry",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    sources: list[InstructionSource] = Field(default_factory=list)
    active_source_ids: list[str] = Field(default_factory=list)
    declared_policy_doc_paths: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_registry_links(self) -> InstructionSourceRegistry:
        """Require active source ids to refer to active registered sources."""
        source_by_id = {source.id: source for source in self.sources}
        unknown = sorted(set(self.active_source_ids) - set(source_by_id))
        if unknown:
            raise ValueError(f"unknown active instruction source ids: {unknown}")
        inactive = sorted(
            source_id
            for source_id in self.active_source_ids
            if not source_by_id[source_id].active
        )
        if inactive:
            raise ValueError(f"inactive instruction source ids marked active: {inactive}")
        policy_paths = sorted(
            source.path for source in self.sources if source.kind == "policy_doc"
        )
        if sorted(self.declared_policy_doc_paths) != policy_paths:
            raise ValueError("declared policy doc paths must match policy_doc sources")
        return self


class InstructionSourceSnapshot(CraikModel):
    """Hash identity for one observed instruction source state."""

    schema_: Literal["craik.instruction_source_snapshot"] = Field(
        default="craik.instruction_source_snapshot",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    source_id: str
    path: str
    hash_algorithm: Literal["sha256"] = "sha256"
    content_hash: str | None = None
    hash_status: InstructionSourceHashStatus
    byte_count: int | None = Field(default=None, ge=0)
    line_count: int | None = Field(default=None, ge=0)
    captured_at: datetime

    @model_validator(mode="after")
    def validate_hash_state(self) -> InstructionSourceSnapshot:
        """Require hashes for present sources and omit hashes for missing sources."""
        if self.hash_status == "missing" and self.content_hash is not None:
            raise ValueError("missing instruction sources must not include content_hash")
        if self.hash_status != "missing" and not self.content_hash:
            raise ValueError("present instruction sources require content_hash")
        return self


class InstructionProvenance(CraikModel):
    """Line/range provenance for distilled instruction material."""

    schema_: Literal["craik.instruction_provenance"] = Field(
        default="craik.instruction_provenance",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    source_id: str
    snapshot_id: str | None = None
    path: str
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    start_column: int | None = Field(default=None, ge=1)
    end_column: int | None = Field(default=None, ge=1)
    summary: str
    excerpt_hash: str | None = None
    captured_at: datetime

    @model_validator(mode="after")
    def validate_range(self) -> InstructionProvenance:
        """Allow source-level provenance or complete line ranges."""
        has_any_line = self.start_line is not None or self.end_line is not None
        if has_any_line and (self.start_line is None or self.end_line is None):
            raise ValueError("instruction provenance line ranges require start_line and end_line")
        if self.start_line is not None and self.end_line is not None:
            if self.end_line < self.start_line:
                raise ValueError("instruction provenance end_line must be >= start_line")
        has_any_column = self.start_column is not None or self.end_column is not None
        if has_any_column and (self.start_column is None or self.end_column is None):
            raise ValueError(
                "instruction provenance column ranges require start_column and end_column"
            )
        return self


class DistilledInstructionProposal(CraikModel):
    """Reviewable instruction distilled from declared runtime instruction sources."""

    schema_: Literal["craik.distilled_instruction_proposal"] = Field(
        default="craik.distilled_instruction_proposal",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    task_id: str | None = None
    source_id: str
    snapshot_id: str | None = None
    category: DistilledInstructionCategory
    statement: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance_ids: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    assumption_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    promotion_status: DistilledInstructionPromotionStatus = "proposed"
    promoted_constraint_id: str | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_promotion_review(self) -> DistilledInstructionProposal:
        """Keep distilled instructions reviewable until a decision is recorded."""
        if self.promotion_status == "approved" and not self.promoted_constraint_id:
            raise ValueError("approved distilled instructions require promoted_constraint_id")
        if self.promotion_status in {"approved", "rejected", "deferred"}:
            if not self.decided_by or self.decided_at is None:
                raise ValueError(
                    "decided distilled instructions require reviewer and decision time"
                )
        if self.category in {"policy", "security_rule"} and not self.evidence_ids:
            raise ValueError("policy and security-rule distillations require evidence ids")
        return self


class PromotedInstructionConstraint(CraikModel):
    """Approved distilled instruction that can be used as an active runtime constraint."""

    schema_: Literal["craik.promoted_instruction_constraint"] = Field(
        default="craik.promoted_instruction_constraint",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    proposal_id: str
    source_id: str
    snapshot_id: str
    category: DistilledInstructionCategory
    statement: str
    provenance_ids: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    active: bool = True
    created_at: datetime


class RunDeltaItem(CraikModel):
    """One observed continuity-relevant state change for recovery mode."""

    kind: RunDeltaChangeKind
    entity_type: RunDeltaEntityType
    entity_id: str
    summary: str
    previous_ref: str | None = None
    current_ref: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class RunDelta(CraikModel):
    """What changed since the previous usable handoff or resume point."""

    schema_: Literal["craik.run_delta"] = Field(default="craik.run_delta", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    task_id: str | None = None
    previous_handoff_id: str | None = None
    current_handoff_id: str | None = None
    case_file_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    active_instruction_constraint_ids: list[str] = Field(default_factory=list)
    changes: list[RunDeltaItem] = Field(default_factory=list)
    summary: str
    created_at: datetime


class RecoverySession(CraikModel):
    """Resume-time continuity summary for an agent picking work back up."""

    schema_: Literal["craik.recovery_session"] = Field(
        default="craik.recovery_session",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    task_id: str | None = None
    status: RecoveryStatus
    run_delta_id: str
    resume_summary: str
    required_actions: list[str] = Field(default_factory=list)
    stale_risks: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    case_file_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    active_instruction_constraint_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_recovery_actions(self) -> RecoverySession:
        """Require explicit next actions when recovery is not clean."""
        if self.status != "clean_resume" and not self.required_actions:
            raise ValueError("non-clean recovery sessions require required_actions")
        return self


class InstructionPromotionReview(CraikModel):
    """Auditable human or policy decision for distilled instruction promotion."""

    schema_: Literal["craik.instruction_promotion_review"] = Field(
        default="craik.instruction_promotion_review",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    proposal_id: str
    decision: InstructionPromotionDecision
    decided_by: str
    rationale: str
    promoted_constraint_id: str | None = None
    policy_envelope_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_decision_links(self) -> InstructionPromotionReview:
        """Approved reviews must link the active promoted constraint."""
        if self.decision == "approved" and not self.promoted_constraint_id:
            raise ValueError("approved promotion reviews require promoted_constraint_id")
        if self.decision != "approved" and self.promoted_constraint_id is not None:
            raise ValueError("unapproved promotion reviews must not link active constraints")
        return self


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


class RunOutput(CraikModel):
    """Inspectable observed output captured from one runner step."""

    schema_: Literal["craik.run_output"] = Field(default="craik.run_output", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    run_id: str
    step_result_id: str
    task_id: str
    phase: TaskRunPhase
    summary: str
    observed_output: dict[str, Any] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
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
    run_id: str | None = None
    step_id: str | None = None
    handoff_id: str | None = None
    operation: ProposalOperation
    fact: FactValue
    evidence: list[EvidenceReference] = Field(default_factory=list)
    requires_approval: bool = True
    status: ProposalStatus = "pending"
    decision_reason: str | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None


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


class MemoryFactReference(CraikModel):
    """Reference to a memory fact involved in a run-scoped diff."""

    id: str | None = None
    cid: str | None = None
    entity: str
    relation: str
    value: str
    source: str
    scope: MemoryScope
    trust_class: TrustClass


class MemoryWriteFailure(CraikModel):
    """A failed attempt to write memory."""

    fact: MemoryFactReference
    reason: str
    attempted_at: datetime


class MemoryContradictionPreview(CraikModel):
    """Likely contradiction identified before memory promotion."""

    entity: str
    relation: str
    existing_value: str
    proposed_value: str
    reason: str


class MemoryDiff(CraikModel):
    """Run-scoped explanation of memory reads, proposals, writes, and failures."""

    schema_: Literal["craik.memory_diff"] = Field(default="craik.memory_diff", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    proposals_created: list[str] = Field(default_factory=list)
    proposals_approved: list[str] = Field(default_factory=list)
    proposals_rejected: list[str] = Field(default_factory=list)
    facts_written: list[MemoryFactReference] = Field(default_factory=list)
    write_failures: list[MemoryWriteFailure] = Field(default_factory=list)
    facts_read: list[MemoryFactReference] = Field(default_factory=list)
    created_at: datetime


class MemoryImpactPreview(CraikModel):
    """Pre-write preview of memory changes and likely contradictions."""

    schema_: Literal["craik.memory_impact_preview"] = Field(
        default="craik.memory_impact_preview",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    facts_to_add: list[MemoryFactReference] = Field(default_factory=list)
    facts_to_invalidate: list[MemoryFactReference] = Field(default_factory=list)
    likely_contradictions: list[MemoryContradictionPreview] = Field(default_factory=list)
    evidence_missing: list[str] = Field(default_factory=list)
    scope_summary: dict[MemoryScope, int] = Field(default_factory=dict)
    created_at: datetime


class ContradictionReport(CraikModel):
    """Incompatible assertions that need resolution."""

    schema_: Literal["craik.contradiction_report"] = Field(
        default="craik.contradiction_report",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str | None = None
    facts: list[str] = Field(min_length=2)
    summary: str
    affected_artifacts: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    proposed_resolution: str | None = None
    status: ContradictionStatus = "open"
    owner: str | None = None
    stigmem_conflict_id: str | None = None
    created_at: datetime | None = None
    resolved_at: datetime | None = None


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


class WorkGraphNode(CraikModel):
    """Exported work graph node."""

    id: str
    type: str
    label: str
    task_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkGraphEdge(CraikModel):
    """Exported work graph edge."""

    id: str
    type: str
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkGraphExport(CraikModel):
    """Deterministic export of graph-connected runtime objects."""

    schema_: Literal["craik.work_graph_export"] = Field(
        default="craik.work_graph_export",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str | None = None
    nodes: list[WorkGraphNode] = Field(default_factory=list)
    edges: list[WorkGraphEdge] = Field(default_factory=list)
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


class ContextDebtRecord(CraikModel):
    """First-class record for context that was omitted, stale, unresolved, or missing."""

    schema_: Literal["craik.context_debt_record"] = Field(
        default="craik.context_debt_record",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    case_file_id: str | None = None
    handoff_id: str | None = None
    kind: ContextDebtKind
    status: ContextDebtStatus = "created"
    summary: str
    owner: str | None = None
    next_action: str | None = None
    omitted_doc_paths: list[str] = Field(default_factory=list)
    stale_instruction_ids: list[str] = Field(default_factory=list)
    assumption_ids: list[str] = Field(default_factory=list)
    missing_external_state: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    resolved_at: datetime | None = None

    @model_validator(mode="after")
    def validate_context_debt_status(self) -> ContextDebtRecord:
        """Require open debt to be actionable and resolved debt to be timestamped."""
        if self.status in {"created", "carried_forward"} and not self.next_action:
            raise ValueError("open context debt requires next_action")
        if self.status == "resolved" and self.resolved_at is None:
            raise ValueError("resolved context debt requires resolved_at")
        if self.status != "resolved" and self.resolved_at is not None:
            raise ValueError("unresolved context debt must not set resolved_at")
        return self


class ToolResultAttestation(CraikModel):
    """Observed tool or command result with freshness and trust boundaries."""

    schema_: Literal["craik.tool_result_attestation"] = Field(
        default="craik.tool_result_attestation",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    tool_name: str
    tool_identity: str
    command: str | None = None
    observed_output_summary: str
    trust_class: TrustClass
    status: ToolAttestationStatus = "attested"
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_id: str | None = None
    captured_at: datetime
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_attestation_window(self) -> ToolResultAttestation:
        """Keep attestation expiry and missing state explicit."""
        if self.expires_at is not None and self.expires_at <= self.captured_at:
            raise ValueError("tool result attestation expires_at must be after captured_at")
        if self.status == "missing" and (self.evidence_ids or self.receipt_id):
            raise ValueError("missing attestations must not include evidence or receipt links")
        if self.status == "attested" and not self.evidence_ids and self.receipt_id is None:
            raise ValueError("attested tool results require evidence_ids or receipt_id")
        return self


class KnowledgeFreshnessProbe(CraikModel):
    """Freshness probe for knowledge that can become stale or expire."""

    schema_: Literal["craik.knowledge_freshness_probe"] = Field(
        default="craik.knowledge_freshness_probe",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    target: str
    kind: FreshnessProbeKind
    status: FreshnessProbeStatus
    trust_class: TrustClass
    observed_output_summary: str
    attestation_id: str | None = None
    captured_at: datetime | None = None
    expires_at: datetime | None = None
    stale_risk_warning: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_freshness_state(self) -> KnowledgeFreshnessProbe:
        """Require stale-risk warnings for non-fresh probe states."""
        if self.expires_at is not None and self.captured_at is not None:
            if self.expires_at <= self.captured_at:
                raise ValueError("freshness probe expires_at must be after captured_at")
        if self.status in {"expiring", "expired", "missing"} and not self.stale_risk_warning:
            raise ValueError("non-fresh freshness probes require stale_risk_warning")
        if self.status == "missing" and self.attestation_id is not None:
            raise ValueError("missing freshness probes must not link an attestation")
        return self


class KnownTrap(CraikModel):
    """Known pitfall agents should avoid when working in a project."""

    schema_: Literal["craik.known_trap"] = Field(default="craik.known_trap", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str | None = None
    task_id: str | None = None
    kind: KnownTrapKind
    status: KnownTrapStatus = "active"
    statement: str
    avoidance: str
    evidence_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_known_trap_status(self) -> KnownTrap:
        """Require evidence for active traps and contradiction links for contradicted traps."""
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError("known trap expires_at must be after created_at")
        if self.status == "active" and not self.evidence_ids:
            raise ValueError("active known traps require evidence_ids")
        if self.status == "contradicted" and not self.contradiction_ids:
            raise ValueError("contradicted known traps require contradiction_ids")
        return self


class NegativeKnowledge(CraikModel):
    """Evidence-backed statement about what is not true or not available."""

    schema_: Literal["craik.negative_knowledge"] = Field(
        default="craik.negative_knowledge",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str | None = None
    task_id: str | None = None
    statement: str
    scope: str
    trust_class: TrustClass
    evidence_ids: list[str] = Field(default_factory=list)
    handoff_ids: list[str] = Field(default_factory=list)
    contradiction_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_negative_knowledge(self) -> NegativeKnowledge:
        """Keep negative knowledge evidence-backed and freshness-bounded."""
        if not self.evidence_ids:
            raise ValueError("negative knowledge requires evidence_ids")
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError("negative knowledge expires_at must be after created_at")
        return self


class ScratchpadRecord(CraikModel):
    """Temporary working note that must expire before it becomes durable context."""

    schema_: Literal["craik.scratchpad_record"] = Field(
        default="craik.scratchpad_record",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    owner: str
    status: ScratchpadStatus = "active"
    note: str
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def validate_scratchpad_expiry(self) -> ScratchpadRecord:
        """Require scratchpad entries to have a future expiry at creation time."""
        if self.expires_at <= self.created_at:
            raise ValueError("scratchpad expires_at must be after created_at")
        return self


class UnknownRecord(CraikModel):
    """First-class unknown that identifies what is needed to resolve it."""

    schema_: Literal["craik.unknown_record"] = Field(
        default="craik.unknown_record",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    owner: str | None = None
    status: UnknownStatus = "unresolved"
    question: str
    needed_resolution: UnknownResolutionSource
    next_action: str
    evidence_ids: list[str] = Field(default_factory=list)
    resolved_answer: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None

    @model_validator(mode="after")
    def validate_unknown_status(self) -> UnknownRecord:
        """Require resolved unknowns to carry answer and timestamp."""
        if self.status == "resolved" and (not self.resolved_answer or self.resolved_at is None):
            raise ValueError("resolved unknowns require resolved_answer and resolved_at")
        if self.status == "unresolved" and self.resolved_at is not None:
            raise ValueError("unresolved unknowns must not set resolved_at")
        return self


class ContextRequest(CraikModel):
    """Structured request for context needed before work can continue safely."""

    schema_: Literal["craik.context_request"] = Field(
        default="craik.context_request",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    requester: str
    kind: ContextRequestKind
    status: ContextRequestStatus = "open"
    question: str
    needed_for: str
    handoff_id: str | None = None
    recovery_session_id: str | None = None
    unknown_id: str | None = None
    fulfilled_by: str | None = None
    fulfilled_at: datetime | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_context_request_status(self) -> ContextRequest:
        """Require fulfillment details only for fulfilled requests."""
        if self.status == "fulfilled" and (not self.fulfilled_by or self.fulfilled_at is None):
            raise ValueError("fulfilled context requests require fulfilled_by and fulfilled_at")
        if self.status != "fulfilled" and (self.fulfilled_by or self.fulfilled_at is not None):
            raise ValueError("open context requests must not include fulfillment details")
        return self


class ExitDisciplineCheck(CraikModel):
    """Checks that an agent exit includes validation, handoff, risks, and next steps."""

    schema_: Literal["craik.exit_discipline_check"] = Field(
        default="craik.exit_discipline_check",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    handoff_id: str | None = None
    status: ExitDisciplineStatus
    validation_recorded: bool
    handoff_recorded: bool
    residual_risks_recorded: bool
    next_steps_recorded: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    context_request_ids: list[str] = Field(default_factory=list)
    unknown_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_exit_status(self) -> ExitDisciplineCheck:
        """Require blocking reasons for blocked exits and complete checklist for complete exits."""
        complete = all(
            [
                self.validation_recorded,
                self.handoff_recorded,
                self.residual_risks_recorded,
                self.next_steps_recorded,
            ]
        )
        if self.status == "complete" and (not complete or self.blocking_reasons):
            raise ValueError("complete exit discipline checks require all checks and no blockers")
        if self.status == "blocked" and not self.blocking_reasons:
            raise ValueError("blocked exit discipline checks require blocking_reasons")
        return self


class SkillEntrypoint(CraikModel):
    """One callable or readable entrypoint inside a skill package."""

    id: str
    kind: SkillEntrypointKind
    path: str
    description: str
    expected_input_schemas: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)


class SkillPackage(CraikModel):
    """Reusable skill package metadata without plugin runtime authority."""

    schema_: Literal["craik.skill_package"] = Field(
        default="craik.skill_package",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    name: str
    package_version: str
    description: str
    entrypoints: list[SkillEntrypoint] = Field(min_length=1)
    docs: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    expected_input_schemas: list[str] = Field(default_factory=list)
    expected_output_schemas: list[str] = Field(default_factory=list)
    provenance_ids: list[str] = Field(default_factory=list)
    plugin_descriptor_id: str | None = None
    runtime_authority: Literal[False] = False
    created_at: datetime

    @model_validator(mode="after")
    def validate_skill_package(self) -> SkillPackage:
        """Require versioned packages with docs and at least one entrypoint."""
        if "." not in self.package_version:
            raise ValueError("skill package_version must be semantic-version-like")
        if not self.docs:
            raise ValueError("skill packages require docs")
        if self.runtime_authority is not False:
            raise ValueError("skill packages must not carry runtime authority")
        return self


class SkillContextInput(CraikModel):
    """Input contract made available to a skill invocation."""

    schema_name: str
    contract_id: str
    required: bool = True
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)


class SkillContextOutput(CraikModel):
    """Output expected from or produced by a skill invocation."""

    schema_name: str
    contract_id: str | None = None
    required: bool = True
    produced: bool = False
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)


class SkillContextOmission(CraikModel):
    """Required or expected context omitted from a skill invocation."""

    schema_name: str
    reason: str
    impact: str
    severity: SkillOmissionSeverity
    mitigation: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class SkillInvocationContext(CraikModel):
    """Auditable context boundary for one skill invocation."""

    schema_: Literal["craik.skill_invocation_context"] = Field(
        default="craik.skill_invocation_context",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    skill_package_id: str
    policy_envelope_id: str
    handoff_id: str | None = None
    inputs: list[SkillContextInput] = Field(min_length=1)
    outputs: list[SkillContextOutput] = Field(default_factory=list)
    omissions: list[SkillContextOmission] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime

    @model_validator(mode="after")
    def validate_skill_invocation_context(self) -> SkillInvocationContext:
        """Require policy-linked, redacted skill context with tracked outputs."""
        if not self.policy_envelope_id:
            raise ValueError("skill invocation context requires a policy_envelope_id")
        if not self.redacted:
            raise ValueError("skill invocation context must be redacted")
        if not self.outputs and not self.omissions:
            raise ValueError("skill invocation context requires outputs or omissions")
        missing_required_outputs = [
            output.schema_name
            for output in self.outputs
            if output.required and not output.produced and not output.contract_id
        ]
        if missing_required_outputs and not self.omissions:
            raise ValueError("missing required outputs must be explained by omissions")
        return self


class SkillRegistryEntry(CraikModel):
    """One discovered project-local or global skill package entry."""

    id: str
    skill_package_id: str
    scope: SkillScope
    project_id: str | None = None
    source_path: str
    trust_boundary: InstructionTrustBoundary
    precedence: int = Field(ge=0)
    active: bool = True
    provenance_ids: list[str] = Field(min_length=1)
    declared_by: str
    created_at: datetime

    @model_validator(mode="after")
    def validate_scope_project_link(self) -> SkillRegistryEntry:
        """Require project ids only for project-scoped skills."""
        if self.scope == "project" and not self.project_id:
            raise ValueError("project-scoped skill entries require project_id")
        if self.scope == "global" and self.project_id is not None:
            raise ValueError("global skill entries must not set project_id")
        return self


class SkillRegistry(CraikModel):
    """Registry of project-local and global skills with explicit precedence."""

    schema_: Literal["craik.skill_registry"] = Field(
        default="craik.skill_registry",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    entries: list[SkillRegistryEntry] = Field(min_length=1)
    active_entry_ids: list[str] = Field(default_factory=list)
    precedence_order: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_skill_registry(self) -> SkillRegistry:
        """Require active links and project-local precedence over globals."""
        entry_by_id = {entry.id: entry for entry in self.entries}
        unknown = sorted(set(self.active_entry_ids) - set(entry_by_id))
        if unknown:
            raise ValueError(f"unknown active skill entry ids: {unknown}")
        inactive = sorted(
            entry_id
            for entry_id in self.active_entry_ids
            if not entry_by_id[entry_id].active
        )
        if inactive:
            raise ValueError(f"inactive skill entry ids marked active: {inactive}")
        if self.precedence_order:
            unknown_order = sorted(set(self.precedence_order) - set(entry_by_id))
            if unknown_order:
                raise ValueError(f"unknown precedence skill entry ids: {unknown_order}")
            missing_active = sorted(set(self.active_entry_ids) - set(self.precedence_order))
            if missing_active:
                raise ValueError(f"active skill entry ids missing precedence: {missing_active}")
        active_entries = [entry_by_id[entry_id] for entry_id in self.active_entry_ids]
        precedence_values = [entry.precedence for entry in active_entries]
        if len(precedence_values) != len(set(precedence_values)):
            raise ValueError("active skill entry precedence values must be unique")
        packages = {entry.skill_package_id for entry in active_entries}
        for package_id in packages:
            project_precedence = [
                entry.precedence
                for entry in active_entries
                if entry.skill_package_id == package_id and entry.scope == "project"
            ]
            global_precedence = [
                entry.precedence
                for entry in active_entries
                if entry.skill_package_id == package_id and entry.scope == "global"
            ]
            if project_precedence and global_precedence:
                if min(project_precedence) > min(global_precedence):
                    raise ValueError("project-scoped skills must outrank global skills")
        return self


class PluginEntrypoint(CraikModel):
    """One declared entrypoint inside a governed plugin descriptor."""

    id: str
    kind: PluginEntrypointKind
    path: str
    description: str


class PluginCapabilityDeclaration(CraikModel):
    """Capability a plugin may request, without granting runtime authority."""

    capability: str
    description: str
    required: bool = True
    grant_required: bool = True
    risk: PluginCapabilityRisk
    operations: list[str] = Field(default_factory=list)
    targets: list[str] = Field(default_factory=list)


class PluginCompatibility(CraikModel):
    """Runtime and platform compatibility metadata for a plugin descriptor."""

    craik_versions: list[str] = Field(min_length=1)
    python_versions: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    status: PluginCompatibilityStatus
    notes: str | None = None


class PluginDescriptor(CraikModel):
    """Governed plugin metadata that declares needs but grants no authority."""

    schema_: Literal["craik.plugin_descriptor"] = Field(
        default="craik.plugin_descriptor",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    name: str
    plugin_version: str
    description: str
    publisher: str
    entrypoints: list[PluginEntrypoint] = Field(min_length=1)
    capabilities: list[PluginCapabilityDeclaration] = Field(min_length=1)
    docs: list[str] = Field(min_length=1)
    compatibility: PluginCompatibility
    security_notes: list[str] = Field(min_length=1)
    skill_package_ids: list[str] = Field(default_factory=list)
    provenance_ids: list[str] = Field(default_factory=list)
    runtime_authority: Literal[False] = False
    created_at: datetime

    @model_validator(mode="after")
    def validate_plugin_descriptor(self) -> PluginDescriptor:
        """Require versioned descriptors and grant separation for risky capabilities."""
        if "." not in self.plugin_version:
            raise ValueError("plugin plugin_version must be semantic-version-like")
        for capability in self.capabilities:
            if capability.risk in {"high", "critical"} and not capability.grant_required:
                raise ValueError("high-risk plugin capabilities require explicit grants")
        if self.runtime_authority is not False:
            raise ValueError("plugin descriptors must not carry runtime authority")
        return self


class PluginProbationCriterion(CraikModel):
    """One review criterion for probationary plugin governance."""

    name: str
    required: bool = True
    passed: bool = False
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)


class PluginProbationDecision(CraikModel):
    """Promotion, rejection, or expiration decision for plugin probation."""

    decision: PluginProbationDecisionKind
    decided_by: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    decided_at: datetime


class PluginProbation(CraikModel):
    """Governance record for probationary plugin review."""

    schema_: Literal["craik.plugin_probation"] = Field(
        default="craik.plugin_probation",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    plugin_descriptor_id: str
    policy_envelope_id: str
    status: PluginProbationStatus = "probationary"
    criteria: list[PluginProbationCriterion] = Field(min_length=1)
    compatibility_check_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    decision: PluginProbationDecision | None = None
    expires_at: datetime | None = None
    durable_trust_granted: bool = False
    created_at: datetime

    @model_validator(mode="after")
    def validate_plugin_probation(self) -> PluginProbation:
        """Require review evidence before promotion and deny durable trust by default."""
        if self.status == "probationary":
            if self.decision is not None:
                raise ValueError("probationary plugin records must not include a decision")
            if self.durable_trust_granted:
                raise ValueError("probationary plugins must not receive durable trust")
        if self.status == "promoted":
            if self.decision is None or self.decision.decision != "promote":
                raise ValueError("promoted plugin records require a promote decision")
            failed_required = [
                criterion.name
                for criterion in self.criteria
                if criterion.required and not criterion.passed
            ]
            if failed_required:
                raise ValueError("promoted plugin records require required criteria to pass")
            if not self.compatibility_check_ids:
                raise ValueError("promoted plugin records require compatibility checks")
        if self.status == "rejected":
            if self.decision is None or self.decision.decision != "reject":
                raise ValueError("rejected plugin records require a reject decision")
        if self.status == "expired":
            if self.decision is None or self.decision.decision != "expire":
                raise ValueError("expired plugin records require an expire decision")
            if self.expires_at is None:
                raise ValueError("expired plugin records require expires_at")
        if self.status != "promoted" and self.durable_trust_granted:
            raise ValueError("only promoted plugin records may grant durable trust")
        return self


class PluginReceipt(CraikModel):
    """Redacted receipt for a plugin action or output."""

    schema_: Literal["craik.plugin_receipt"] = Field(
        default="craik.plugin_receipt",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    actor: str
    plugin_descriptor_id: str
    plugin_probation_id: str | None = None
    action: str
    capability_grant_ids: list[str] = Field(min_length=1)
    trust_boundary: InstructionTrustBoundary
    result: ReceiptResult
    evidence_ids: list[str] = Field(min_length=1)
    handoff_ids: list[str] = Field(min_length=1)
    redacted: bool = True
    created_at: datetime

    @model_validator(mode="after")
    def validate_plugin_receipt(self) -> PluginReceipt:
        """Require redacted plugin receipts with grant and evidence links."""
        if not self.redacted:
            raise ValueError("plugin receipts must be redacted")
        if self.result.status == "passed" and not self.capability_grant_ids:
            raise ValueError("successful plugin receipts require capability grants")
        if self.result.status == "denied" and not self.result.summary:
            raise ValueError("denied plugin receipts require a denial summary")
        return self


class PluginCapabilityGrant(CraikModel):
    """Least-privilege capability grant scoped to one plugin descriptor."""

    schema_: Literal["craik.plugin_capability_grant"] = Field(
        default="craik.plugin_capability_grant",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    plugin_descriptor_id: str
    policy_envelope_id: str
    capability: str
    target: CapabilityTarget
    operations: list[str] = Field(min_length=1)
    status: PluginGrantStatus
    approval_required: bool = False
    approved_by: str | None = None
    expires_at: datetime | None = None
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_plugin_capability_grant(self) -> PluginCapabilityGrant:
        """Validate plugin grant state and least-privilege approval boundaries."""
        if self.status == "allowed":
            if self.approval_required and not self.approved_by:
                raise ValueError("approval-required allowed plugin grants require approved_by")
            if self.expires_at is None:
                raise ValueError("allowed plugin grants require expires_at")
        if self.status == "denied" and self.approved_by is not None:
            raise ValueError("denied plugin grants must not include approved_by")
        if self.status == "expired" and self.expires_at is None:
            raise ValueError("expired plugin grants require expires_at")
        if self.status == "approval_required":
            if not self.approval_required:
                raise ValueError("approval_required grants must set approval_required")
            if self.approved_by is not None:
                raise ValueError("approval_required grants must not include approved_by")
        return self


class AgentOnboarding(CraikModel):
    """Runner-readable project context for an agent starting work."""

    schema_: Literal["craik.agent_onboarding"] = Field(
        default="craik.agent_onboarding",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    project_id: str
    project_model: dict[str, Any]
    active_policy: PolicyEnvelope
    docs_boundaries: dict[str, Any]
    recent_handoffs: list[dict[str, Any]] = Field(default_factory=list)
    unresolved_contradictions: list[ContradictionReport] = Field(default_factory=list)
    stale_risk_warnings: list[str] = Field(default_factory=list)
    validation_commands: list[str] = Field(default_factory=list)
    stigmem_backend_status: dict[str, Any] = Field(default_factory=dict)
    known_traps: list[str] = Field(default_factory=list)
    allowed_next_actions: list[str] = Field(default_factory=list)
    created_at: datetime


class SelfAudit(CraikModel):
    """Required handoff self-audit checklist."""

    schema_validated: bool
    redaction_reviewed: bool
    receipts_reviewed: bool
    assumptions_reviewed: bool
    validation_recorded: bool
    policy_exceptions_disclosed: bool
    notes: list[str] = Field(default_factory=list)


class Handoff(CraikModel):
    """Durable run summary for future agents."""

    schema_: Literal["craik.handoff"] = Field(default="craik.handoff", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str
    intent_lock_id: str | None = None
    agent: str
    status: RunStatus = "completed"
    summary: str
    self_audit: SelfAudit
    completed_actions: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)
    tests_run: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    context_debt: list[str] = Field(default_factory=list)
    policy_exceptions: list[str] = Field(default_factory=list)
    facts_learned: list[str] = Field(default_factory=list)
    facts_invalidated: list[str] = Field(default_factory=list)
    contradictions_opened: list[str] = Field(default_factory=list)
    adjudication_ids: list[str] = Field(default_factory=list)
    unresolved_disagreements: list[str] = Field(default_factory=list)
    open_human_delegation_ids: list[str] = Field(default_factory=list)
    scope_change_request_ids: list[str] = Field(default_factory=list)
    scope_change_result_ids: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    memory_proposal_ids: list[str] = Field(default_factory=list)
    runner_metadata: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class QualityScoreComponent(CraikModel):
    """One weighted scoring input for a handoff or evidence coverage score."""

    name: HandoffQualityComponentName
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(gt=0.0, le=1.0)
    rationale: str


class HandoffQualityScore(CraikModel):
    """Derived quality score for a handoff's completeness and recovery value."""

    schema_: Literal["craik.handoff_quality_score"] = Field(
        default="craik.handoff_quality_score",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str
    handoff_id: str
    score: float = Field(ge=0.0, le=1.0)
    band: QualityScoreBand
    components: list[QualityScoreComponent] = Field(min_length=1)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_handoff_score_band(self) -> HandoffQualityScore:
        """Keep the derived band aligned with the numeric score."""
        if self.score >= 0.85 and self.band != "excellent":
            raise ValueError("handoff scores >= 0.85 must be excellent")
        if 0.60 <= self.score < 0.85 and self.band != "adequate":
            raise ValueError("handoff scores between 0.60 and 0.85 must be adequate")
        if self.score < 0.60 and self.band != "poor":
            raise ValueError("handoff scores below 0.60 must be poor")
        if self.band == "poor" and not self.blocking_reasons:
            raise ValueError("poor handoff quality scores require blocking_reasons")
        return self


class EvidenceCoverageScore(CraikModel):
    """Derived score for evidence links supporting a handoff or output."""

    schema_: Literal["craik.evidence_coverage_score"] = Field(
        default="craik.evidence_coverage_score",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    project_id: str | None = None
    handoff_id: str | None = None
    score: float = Field(ge=0.0, le=1.0)
    band: QualityScoreBand
    evidence_ids: list[str] = Field(default_factory=list)
    required_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence_ids: list[str] = Field(default_factory=list)
    weak_claims: list[str] = Field(default_factory=list)
    created_at: datetime

    @model_validator(mode="after")
    def validate_evidence_score(self) -> EvidenceCoverageScore:
        """Require explicit gaps for poor evidence coverage scores."""
        if self.score >= 0.85 and self.band != "excellent":
            raise ValueError("evidence scores >= 0.85 must be excellent")
        if 0.60 <= self.score < 0.85 and self.band != "adequate":
            raise ValueError("evidence scores between 0.60 and 0.85 must be adequate")
        if self.score < 0.60 and self.band != "poor":
            raise ValueError("evidence scores below 0.60 must be poor")
        if self.band == "poor" and not self.missing_evidence_ids and not self.weak_claims:
            raise ValueError(
                "poor evidence coverage scores require missing evidence or weak claims"
            )
        return self


class TaskRun(CraikModel):
    """Durable state for one governed single-agent task run."""

    schema_: Literal["craik.task_run"] = Field(default="craik.task_run", alias="schema")
    version: Literal["0.1.0"] = "0.1.0"
    id: str
    task_id: str
    case_file_id: str
    policy_envelope_id: str
    intent_lock_id: str | None = None
    runner_id: str
    runner_mode: RunnerMode
    status: TaskRunStatus = "pending"
    phase: TaskRunPhase = "plan"
    iteration: int = Field(default=0, ge=0)
    max_iterations: int = Field(default=5, ge=1)
    started_at: datetime
    phase_started_at: datetime
    updated_at: datetime
    ended_at: datetime | None = None
    stop_reason: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)
    handoff_id: str | None = None
    runner_metadata: list[dict[str, Any]] = Field(default_factory=list)
