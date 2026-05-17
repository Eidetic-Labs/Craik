"""Memory diff and impact preview helpers."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from craik.contracts.models import (
    FactValue,
    MemoryContradictionPreview,
    MemoryDiff,
    MemoryFactReference,
    MemoryImpactPreview,
    MemoryProposal,
    MemoryScope,
    MemoryWriteFailure,
)
from craik.runtime.policy.redaction import redact


def build_memory_diff(
    *,
    task_id: str,
    proposals: Iterable[MemoryProposal],
    facts_written: Iterable[MemoryFactReference] = (),
    write_failures: Iterable[MemoryWriteFailure] = (),
    facts_read: Iterable[MemoryFactReference] = (),
) -> MemoryDiff:
    """Build a run-scoped memory diff from proposal and fact activity."""
    scoped = [proposal for proposal in proposals if proposal.task_id == task_id]
    return MemoryDiff(
        id=f"memdiff_{task_id}",
        task_id=task_id,
        proposals_created=sorted(proposal.id for proposal in scoped),
        proposals_approved=sorted(
            proposal.id for proposal in scoped if proposal.status == "approved"
        ),
        proposals_rejected=sorted(
            proposal.id for proposal in scoped if proposal.status == "rejected"
        ),
        facts_written=sorted(facts_written, key=_fact_reference_sort_key),
        write_failures=sorted(
            write_failures,
            key=lambda failure: _fact_reference_sort_key(failure.fact),
        ),
        facts_read=sorted(facts_read, key=_fact_reference_sort_key),
        created_at=datetime.now(UTC),
    )


def preview_memory_impact(
    *,
    task_id: str,
    proposals: Iterable[MemoryProposal],
    existing_facts: Iterable[FactValue],
) -> MemoryImpactPreview:
    """Preview memory additions, invalidations, evidence gaps, and likely contradictions."""
    scoped = [proposal for proposal in proposals if proposal.task_id == task_id]
    additions = [
        fact_reference(proposal.fact)
        for proposal in scoped
        if proposal.operation in {"add", "update"}
    ]
    invalidations = [
        fact_reference(proposal.fact) for proposal in scoped if proposal.operation == "invalidate"
    ]
    evidence_missing = sorted(proposal.id for proposal in scoped if not proposal.evidence)
    contradictions = _likely_contradictions(scoped, existing_facts)
    return MemoryImpactPreview(
        id=f"mempreview_{task_id}",
        task_id=task_id,
        facts_to_add=sorted(additions, key=_fact_reference_sort_key),
        facts_to_invalidate=sorted(invalidations, key=_fact_reference_sort_key),
        likely_contradictions=contradictions,
        evidence_missing=evidence_missing,
        scope_summary=_scope_summary(scoped),
        created_at=datetime.now(UTC),
    )


def fact_reference(
    fact: FactValue,
    *,
    fact_id: str | None = None,
    cid: str | None = None,
) -> MemoryFactReference:
    """Create a redacted fact reference for diffs and previews."""
    return MemoryFactReference(
        id=fact_id,
        cid=cid,
        entity=str(redact(fact.entity).value),
        relation=str(redact(fact.relation).value),
        value=str(redact(fact.value).value),
        source=str(redact(fact.source).value),
        scope=fact.scope,
        trust_class=fact.trust_class,
    )


def memory_write_failure(
    *,
    fact: FactValue,
    reason: str,
) -> MemoryWriteFailure:
    """Create a redacted memory write failure record."""
    return MemoryWriteFailure(
        fact=fact_reference(fact),
        reason=str(redact(reason).value),
        attempted_at=datetime.now(UTC),
    )


def _likely_contradictions(
    proposals: Iterable[MemoryProposal],
    existing_facts: Iterable[FactValue],
) -> list[MemoryContradictionPreview]:
    existing_by_key: dict[tuple[str, str], list[FactValue]] = {}
    for fact in existing_facts:
        existing_by_key.setdefault((fact.entity, fact.relation), []).append(fact)

    contradictions: list[MemoryContradictionPreview] = []
    for proposal in proposals:
        if proposal.operation == "invalidate":
            continue
        for existing in existing_by_key.get((proposal.fact.entity, proposal.fact.relation), []):
            if existing.value == proposal.fact.value:
                continue
            contradictions.append(
                MemoryContradictionPreview(
                    entity=proposal.fact.entity,
                    relation=proposal.fact.relation,
                    existing_value=existing.value,
                    proposed_value=proposal.fact.value,
                    reason="same entity and relation with a different value",
                )
            )
    return sorted(
        contradictions,
        key=lambda item: (item.entity, item.relation, item.existing_value, item.proposed_value),
    )


def _scope_summary(proposals: Iterable[MemoryProposal]) -> dict[MemoryScope, int]:
    summary: dict[MemoryScope, int] = {}
    for proposal in proposals:
        summary[proposal.fact.scope] = summary.get(proposal.fact.scope, 0) + 1
    return dict(sorted(summary.items()))


def _fact_reference_sort_key(fact: MemoryFactReference) -> tuple[str, str, str, str]:
    return (fact.entity, fact.relation, fact.value, fact.source)
