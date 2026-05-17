"""Memory, contradiction, evidence, and graph store methods."""

# ruff: noqa: F403,F405,I001

from __future__ import annotations

from .base import *


class MemoryStoreMixin(LocalStoreCore):
    def put_proposal(self, proposal: MemoryProposal) -> None:
        self.put_contract(proposal)

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        contract = self.get_contract("craik.memory_proposal", proposal_id)
        return _cast_optional(MemoryProposal, contract)

    def list_proposals(self) -> list[MemoryProposal]:
        return _cast_list(MemoryProposal, self.list_contracts("craik.memory_proposal"))

    def put_memory_diff(self, diff: MemoryDiff) -> None:
        self.put_contract(diff)

    def get_memory_diff(self, diff_id: str) -> MemoryDiff | None:
        contract = self.get_contract("craik.memory_diff", diff_id)
        return _cast_optional(MemoryDiff, contract)

    def list_memory_diffs(self) -> list[MemoryDiff]:
        return _cast_list(MemoryDiff, self.list_contracts("craik.memory_diff"))

    def put_memory_impact_preview(self, preview: MemoryImpactPreview) -> None:
        self.put_contract(preview)

    def get_memory_impact_preview(self, preview_id: str) -> MemoryImpactPreview | None:
        contract = self.get_contract("craik.memory_impact_preview", preview_id)
        return _cast_optional(MemoryImpactPreview, contract)

    def list_memory_impact_previews(self) -> list[MemoryImpactPreview]:
        return _cast_list(
            MemoryImpactPreview,
            self.list_contracts("craik.memory_impact_preview"),
        )

    def put_contradiction(self, contradiction: ContradictionReport) -> None:
        self.put_contract(contradiction)

    def get_contradiction(self, contradiction_id: str) -> ContradictionReport | None:
        contract = self.get_contract("craik.contradiction_report", contradiction_id)
        return _cast_optional(ContradictionReport, contract)

    def list_contradictions(self) -> list[ContradictionReport]:
        return _cast_list(ContradictionReport, self.list_contracts("craik.contradiction_report"))

    def put_context_debt_record(self, debt: ContextDebtRecord) -> None:
        self.put_contract(debt)

    def get_context_debt_record(self, debt_id: str) -> ContextDebtRecord | None:
        contract = self.get_contract("craik.context_debt_record", debt_id)
        return _cast_optional(ContextDebtRecord, contract)

    def list_context_debt_records(self) -> list[ContextDebtRecord]:
        return _cast_list(
            ContextDebtRecord,
            self.list_contracts("craik.context_debt_record"),
        )

    def put_context_request(self, request: ContextRequest) -> None:
        self.put_contract(request)

    def get_context_request(self, request_id: str) -> ContextRequest | None:
        contract = self.get_contract("craik.context_request", request_id)
        return _cast_optional(ContextRequest, contract)

    def list_context_requests(self) -> list[ContextRequest]:
        return _cast_list(ContextRequest, self.list_contracts("craik.context_request"))

    def put_assumption(self, assumption: Assumption) -> None:
        self.put_contract(assumption)

    def get_assumption(self, assumption_id: str) -> Assumption | None:
        contract = self.get_contract("craik.assumption", assumption_id)
        return _cast_optional(Assumption, contract)

    def list_assumptions(self) -> list[Assumption]:
        return _cast_list(Assumption, self.list_contracts("craik.assumption"))

    def put_evidence(self, evidence: EvidenceReference) -> None:
        self.put_contract(evidence)

    def get_evidence(self, evidence_id: str) -> EvidenceReference | None:
        contract = self.get_contract("craik.evidence_reference", evidence_id)
        return _cast_optional(EvidenceReference, contract)

    def list_evidence(self) -> list[EvidenceReference]:
        return _cast_list(EvidenceReference, self.list_contracts("craik.evidence_reference"))

    def put_evidence_coverage_score(self, score: EvidenceCoverageScore) -> None:
        self.put_contract(score)

    def get_evidence_coverage_score(self, score_id: str) -> EvidenceCoverageScore | None:
        contract = self.get_contract("craik.evidence_coverage_score", score_id)
        return _cast_optional(EvidenceCoverageScore, contract)

    def list_evidence_coverage_scores(self) -> list[EvidenceCoverageScore]:
        return _cast_list(
            EvidenceCoverageScore,
            self.list_contracts("craik.evidence_coverage_score"),
        )

    def put_exit_discipline_check(self, check: ExitDisciplineCheck) -> None:
        self.put_contract(check)

    def get_exit_discipline_check(self, check_id: str) -> ExitDisciplineCheck | None:
        contract = self.get_contract("craik.exit_discipline_check", check_id)
        return _cast_optional(ExitDisciplineCheck, contract)

    def list_exit_discipline_checks(self) -> list[ExitDisciplineCheck]:
        return _cast_list(
            ExitDisciplineCheck,
            self.list_contracts("craik.exit_discipline_check"),
        )

    def put_graph_event(self, event: WorkGraphEvent) -> None:
        self.put_contract(event)

    def get_graph_event(self, event_id: str) -> WorkGraphEvent | None:
        contract = self.get_contract("craik.work_graph_event", event_id)
        return _cast_optional(WorkGraphEvent, contract)

    def list_graph_events(self) -> list[WorkGraphEvent]:
        return _cast_list(WorkGraphEvent, self.list_contracts("craik.work_graph_event"))
