"""Read-only multi-agent investigation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from craik.contracts.models import (
    AgentRole,
    CapabilityReceipt,
    CaseFile,
    PolicyEnvelope,
    ReceiptResult,
    ReceiptStatus,
    RunnerMetadata,
    WorkerFinding,
    WorkerResult,
)
from craik.runtime.store import LocalStore


class InvestigationError(RuntimeError):
    """Base error for investigation orchestration failures."""


class InvestigationContextError(InvestigationError):
    """Raised when required investigation context is unavailable."""


@dataclass(frozen=True)
class InvestigationRequest:
    """Bounded read-only request for one specialist role."""

    id: str
    task_id: str
    case_file_id: str
    policy_envelope_id: str
    role: AgentRole
    question: str
    context_refs: list[str]


@dataclass(frozen=True)
class InvestigationBatch:
    """Created investigation requests and persisted worker results."""

    requests: list[InvestigationRequest]
    results: list[WorkerResult]
    receipts: list[CapabilityReceipt]


class InvestigationSpecialist(Protocol):
    """Boundary implemented by deterministic or live read-only specialists."""

    def investigate(self, request: InvestigationRequest) -> WorkerResult:
        """Return a typed worker result for one read-only investigation."""


@dataclass(frozen=True)
class FixtureInvestigationSpecialist:
    """Deterministic read-only specialist for tests and demos."""

    runner: RunnerMetadata | None = None

    def investigate(self, request: InvestigationRequest) -> WorkerResult:
        return WorkerResult(
            id=f"worker_result_{request.id}",
            task_id=request.task_id,
            role_id=request.role.id,
            role_kind=request.role.kind,
            runner=self.runner,
            status="completed",
            summary=f"{request.role.kind} investigated: {request.question}",
            findings=[
                WorkerFinding(
                    summary=f"Read-only finding for {request.role.kind}.",
                    evidence_ids=request.context_refs,
                )
            ],
            evidence=[],
            receipt_ids=[investigation_receipt_id(request.id)],
            created_at=datetime.now(UTC),
        )


class ReadOnlyInvestigationOrchestrator:
    """Create and run bounded read-only specialist investigations."""

    def __init__(self, store: LocalStore, specialist: InvestigationSpecialist) -> None:
        self.store = store
        self.specialist = specialist

    def run(
        self,
        *,
        task_id: str,
        case_file_id: str,
        policy: PolicyEnvelope,
        roles: list[AgentRole],
        questions: dict[str, str],
    ) -> InvestigationBatch:
        case_file = self.store.get_case_file(case_file_id)
        if case_file is None:
            raise InvestigationContextError(f"unknown case file: {case_file_id}")
        requests = [
            self._request_for_role(
                task_id=task_id,
                case_file=case_file,
                policy=policy,
                role=role,
                question=questions.get(role.id, f"Investigate as {role.name}."),
            )
            for role in roles
        ]
        receipts: list[CapabilityReceipt] = []
        results: list[WorkerResult] = []
        for request in requests:
            receipt = _investigation_receipt(policy=policy, request=request)
            self.store.put_receipt(receipt)
            receipts.append(receipt)
            if receipt.result.status == "blocked":
                result = _blocked_result(request, receipt)
            else:
                result = self.specialist.investigate(request)
                if receipt.id not in result.receipt_ids:
                    result = result.model_copy(
                        update={"receipt_ids": [*result.receipt_ids, receipt.id]}
                    )
            self.store.put_worker_result(result)
            results.append(result)
        return InvestigationBatch(requests=requests, results=results, receipts=receipts)

    def _request_for_role(
        self,
        *,
        task_id: str,
        case_file: CaseFile,
        policy: PolicyEnvelope,
        role: AgentRole,
        question: str,
    ) -> InvestigationRequest:
        context_refs = [evidence.id for evidence in case_file.evidence]
        context_refs.extend(fact.source for fact in case_file.facts)
        return InvestigationRequest(
            id=f"investigation_{task_id.removeprefix('task_')}_{role.id}",
            task_id=task_id,
            case_file_id=case_file.id,
            policy_envelope_id=policy.id,
            role=role,
            question=question,
            context_refs=sorted(dict.fromkeys(context_refs)),
        )


def investigation_receipt_id(request_id: str) -> str:
    """Return the deterministic receipt id for an investigation request."""
    return f"receipt_{request_id}"


def _investigation_receipt(
    *,
    policy: PolicyEnvelope,
    request: InvestigationRequest,
) -> CapabilityReceipt:
    allowed = _read_only_allowed(policy, request.role)
    status: ReceiptStatus = "passed" if allowed else "blocked"
    summary = (
        "Read-only investigation allowed by role and policy."
        if allowed
        else "Read-only investigation requires repo.read or memory.read policy access."
    )
    return CapabilityReceipt(
        id=investigation_receipt_id(request.id),
        task_id=request.task_id,
        actor=f"role:{request.role.id}",
        capability="investigation.read_only",
        target=request.case_file_id,
        policy_profile=policy.profile,
        fail_open=policy.fail_open,
        reason=summary,
        result=ReceiptResult(status=status, summary=summary),
        redacted=True,
        created_at=datetime.now(UTC),
    )


def _blocked_result(request: InvestigationRequest, receipt: CapabilityReceipt) -> WorkerResult:
    return WorkerResult(
        id=f"worker_result_{request.id}",
        task_id=request.task_id,
        role_id=request.role.id,
        role_kind=request.role.kind,
        status="blocked",
        summary=receipt.reason,
        risks=[receipt.reason],
        receipt_ids=[receipt.id],
        diagnostics=[receipt.reason],
        created_at=datetime.now(UTC),
    )


def _read_only_allowed(policy: PolicyEnvelope, role: AgentRole) -> bool:
    if "read" not in role.authority and "review" not in role.authority:
        return False
    if "repo.write" in role.allowed_capabilities or "memory.write" in role.allowed_capabilities:
        return False
    return (
        "repo.read" in policy.allowed_capabilities
        or "memory.read" in policy.allowed_capabilities
    )
