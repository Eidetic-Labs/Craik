"""Runtime critic and red-team finding helpers."""

from __future__ import annotations

from craik.contracts.models import RedTeamFinding, RuntimeCriticFinding
from craik.runtime.store import LocalStore


def reviewable_critic_findings(
    store: LocalStore,
    *,
    task_id: str,
) -> list[RuntimeCriticFinding]:
    """Return non-authoritative critic findings that still need review."""
    return sorted(
        (
            finding
            for finding in store.list_runtime_critic_findings()
            if finding.task_id == task_id
            and finding.review_status == "reviewable"
            and not finding.authoritative
        ),
        key=lambda finding: (finding.severity, finding.id),
    )


def blocking_red_team_findings(
    store: LocalStore,
    *,
    task_id: str,
) -> list[RedTeamFinding]:
    """Return non-authoritative red-team blockers for a task."""
    return sorted(
        (
            finding
            for finding in store.list_red_team_findings()
            if finding.task_id == task_id
            and finding.blocking
            and finding.review_status == "reviewable"
            and not finding.authoritative
        ),
        key=lambda finding: (finding.severity, finding.id),
    )


def render_critic_finding_markdown(finding: RuntimeCriticFinding) -> str:
    """Render a deterministic Markdown critic finding."""
    lines = [
        f"# Runtime Critic Finding: {finding.id}",
        "",
        f"- Type: {finding.finding_type}",
        f"- Severity: {finding.severity}",
        f"- Review Status: {finding.review_status}",
        f"- Authoritative: {str(finding.authoritative).lower()}",
        "",
        "## Summary",
        "",
        finding.summary,
        "",
        "## Proposed Actions",
        "",
        *_bullets(finding.proposed_actions),
    ]
    return "\n".join(lines) + "\n"


def render_red_team_finding_markdown(finding: RedTeamFinding) -> str:
    """Render a deterministic Markdown red-team finding."""
    lines = [
        f"# Red-Team Finding: {finding.id}",
        "",
        f"- Type: {finding.finding_type}",
        f"- Severity: {finding.severity}",
        f"- Blocking: {str(finding.blocking).lower()}",
        f"- Review Status: {finding.review_status}",
        f"- Authoritative: {str(finding.authoritative).lower()}",
        "",
        "## Summary",
        "",
        finding.summary,
        "",
        "## Proposed Actions",
        "",
        *_bullets(finding.proposed_actions),
    ]
    return "\n".join(lines) + "\n"


def _bullets(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]
