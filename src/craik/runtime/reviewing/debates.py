"""Structured debate capture and contradiction escalation."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import DebateOutcome, DebateSummary, DebateTurn
from craik.runtime.memory.contradictions import ContradictionManager
from craik.runtime.store import LocalStore


class DebateManager:
    """Persist debate turns and produce deterministic debate summaries."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store
        self._contradictions = ContradictionManager(store)

    def record_turn(self, turn: DebateTurn) -> DebateTurn:
        """Persist one debate turn."""
        self._store.put_debate_turn(turn)
        return turn

    def summarize(
        self,
        *,
        task_id: str,
        debate_id: str,
        topic: str,
        turns: list[DebateTurn] | None = None,
        open_contradictions: bool = True,
        next_steps: list[str] | None = None,
    ) -> DebateSummary:
        """Summarize a debate, optionally opening contradictions for conflicting outputs."""
        debate_turns = sorted(
            turns if turns is not None else self._turns_for_debate(debate_id),
            key=lambda turn: (turn.created_at, turn.id),
        )
        for turn in debate_turns:
            self._store.put_debate_turn(turn)

        supports = [turn for turn in debate_turns if turn.position == "supports"]
        oppositions = [turn for turn in debate_turns if turn.position in {"opposes", "blocks"}]
        evidence_ids = sorted(
            {evidence_id for turn in debate_turns for evidence_id in turn.evidence_ids}
        )
        contradiction_ids = sorted(
            {
                contradiction_id
                for turn in debate_turns
                for contradiction_id in turn.contradiction_ids
            }
        )
        worker_result_ids = sorted(
            {turn.worker_result_id for turn in debate_turns if turn.worker_result_id is not None}
        )

        unresolved = _unresolved_disagreements(supports, oppositions)
        agreements = sorted({turn.claim for turn in supports}) if not unresolved else []
        outcome: DebateOutcome = "agreement"
        if unresolved and open_contradictions:
            report = self._contradictions.open_report(
                task_id=task_id,
                facts=[turn.claim for turn in [*supports, *oppositions]],
                summary=f"Debate disagreement: {topic}",
                affected_artifacts=worker_result_ids,
                evidence_ids=evidence_ids,
                proposed_resolution="Adjudicate the conflicting specialist outputs.",
            )
            contradiction_ids = sorted({*contradiction_ids, report.id})
            outcome = "contradiction_opened"
        elif unresolved:
            outcome = "unresolved_disagreement"

        summary = DebateSummary(
            id=f"debate_summary_{debate_id}",
            task_id=task_id,
            debate_id=debate_id,
            topic=topic,
            turn_ids=[turn.id for turn in debate_turns],
            outcome=outcome,
            summary=_summary_text(topic=topic, outcome=outcome, turn_count=len(debate_turns)),
            agreements=agreements,
            unresolved_disagreements=unresolved,
            contradiction_ids=contradiction_ids,
            evidence_ids=evidence_ids,
            next_steps=sorted(next_steps or []),
            created_at=datetime.now(UTC),
        )
        self._store.put_debate_summary(summary)
        return summary

    def _turns_for_debate(self, debate_id: str) -> list[DebateTurn]:
        return [turn for turn in self._store.list_debate_turns() if turn.debate_id == debate_id]


def render_debate_markdown(summary: DebateSummary, turns: list[DebateTurn]) -> str:
    """Render a deterministic Markdown view of a debate summary and its turns."""
    turn_by_id = {turn.id: turn for turn in turns}
    ordered_turns = [turn_by_id[turn_id] for turn_id in summary.turn_ids if turn_id in turn_by_id]
    lines = [
        f"# Debate: {summary.topic}",
        "",
        f"- Outcome: {summary.outcome}",
        f"- Summary: {summary.summary}",
        "",
        "## Agreements",
        *_bullet_lines(summary.agreements),
        "",
        "## Unresolved Disagreements",
        *_bullet_lines(summary.unresolved_disagreements),
        "",
        "## Contradictions",
        *_bullet_lines(summary.contradiction_ids),
        "",
        "## Turns",
    ]
    for turn in ordered_turns:
        evidence = ", ".join(sorted(turn.evidence_ids)) or "none"
        assumptions = ", ".join(sorted(turn.assumption_ids)) or "none"
        lines.extend(
            [
                f"- {turn.id} ({turn.role_kind}/{turn.position})",
                f"  - Claim: {turn.claim}",
                f"  - Rationale: {turn.rationale}",
                f"  - Evidence: {evidence}",
                f"  - Assumptions: {assumptions}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_debate_json(summary: DebateSummary) -> str:
    """Render a deterministic JSON representation of a debate summary."""
    return summary.model_dump_json(by_alias=True, exclude_none=True, indent=2) + "\n"


def _unresolved_disagreements(
    supports: list[DebateTurn],
    oppositions: list[DebateTurn],
) -> list[str]:
    if not supports or not oppositions:
        return []
    return sorted(
        {
            f"{support.role_id} claims {support.claim!r}; "
            f"{opposition.role_id} disputes with {opposition.claim!r}"
            for support in supports
            for opposition in oppositions
        }
    )


def _summary_text(*, topic: str, outcome: DebateOutcome, turn_count: int) -> str:
    if outcome == "agreement":
        return f"{turn_count} debate turn(s) reached agreement on {topic}."
    if outcome == "contradiction_opened":
        return f"{turn_count} debate turn(s) produced a contradiction report for {topic}."
    return f"{turn_count} debate turn(s) preserved unresolved disagreement on {topic}."


def _bullet_lines(values: list[str]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]
