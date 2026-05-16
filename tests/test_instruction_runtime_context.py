import subprocess
from pathlib import Path

from craik.contracts.models import (
    DistilledInstructionProposal,
    PromotedInstructionConstraint,
)
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.handoffs import HandoffWriter
from craik.runtime.instruction_sources import active_instruction_context
from craik.runtime.onboarding import AgentOnboardingBuilder
from craik.runtime.paths import ensure_craik_home
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.prompts import PromptCompiler
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def test_approved_distillations_reach_case_file_prompt_onboarding_and_handoff(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    try:
        repo = _repo(tmp_path)
        project = ProjectRegistry(store).add_project(repo, name="Docs")
        task = create_task(
            store,
            title="Apply instructions",
            objective="Use approved instructions.",
            project_id=project.id,
        )
        _approved_constraint(store, project.id)

        case_file = CaseFileAssembler(store).build(task.id)
        prompt = PromptCompiler(store).compile(task.id, runner_id="codex")
        onboarding = AgentOnboardingBuilder(store).build(project.id)
        handoff = HandoffWriter(store).create(
            task_id=task.id,
            agent="agent:test",
            summary="Applied instruction context.",
            tests_run=["pytest"],
        )

        active = active_instruction_context(store, project.id)
        assert active[0]["statement"] == "Run tests before merge."
        assert case_file.context_budget["active_instruction_constraints"] == active
        assert "Run tests before merge." in prompt.prompt
        assert onboarding.project_model["active_instruction_constraints"] == active
        assert any("constraint_distilled_instruction" in item for item in handoff.context_debt)
    finally:
        store.close()


def test_unapproved_stale_or_contradicted_distillations_are_inactive(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        repo = _repo(tmp_path)
        project = ProjectRegistry(store).add_project(repo, name="Docs")
        task = create_task(
            store,
            title="Ignore inactive",
            objective="Ignore inactive instructions.",
            project_id=project.id,
        )
        store.put_distilled_instruction_proposal(
            _proposal(project.id, status="proposed", contradiction_ids=["contradiction_one"])
        )
        store.put_distilled_instruction_proposal(_proposal(project.id, status="deferred"))
        CaseFileAssembler(store).build(task.id)

        assert active_instruction_context(store, project.id) == []
    finally:
        store.close()


def _approved_constraint(store: LocalStore, project_id: str) -> None:
    proposal = _proposal(
        project_id,
        status="approved",
        promoted_constraint_id="constraint_distilled_instruction",
    )
    store.put_distilled_instruction_proposal(proposal)
    store.put_promoted_instruction_constraint(
        PromotedInstructionConstraint(
            id="constraint_distilled_instruction",
            project_id=project_id,
            proposal_id=proposal.id,
            source_id=proposal.source_id,
            snapshot_id=proposal.snapshot_id,
            category=proposal.category,
            statement=proposal.statement,
            provenance_ids=proposal.provenance_ids,
            evidence_ids=proposal.evidence_ids,
            active=True,
            created_at="2026-05-15T22:31:00Z",
        )
    )


def _proposal(
    project_id: str,
    *,
    status: str,
    promoted_constraint_id: str | None = None,
    contradiction_ids: list[str] | None = None,
) -> DistilledInstructionProposal:
    return DistilledInstructionProposal(
        id="distilled_instruction",
        project_id=project_id,
        source_id="instruction_source_agents_md",
        snapshot_id="snapshot_agents",
        category="command",
        statement="Run tests before merge.",
        rationale="Extracted from AGENTS.md.",
        confidence=0.9,
        provenance_ids=["provenance_agents_rule"],
        evidence_ids=["evidence_agents_rule"],
        contradiction_ids=contradiction_ids or [],
        promotion_status=status,
        promoted_constraint_id=promoted_constraint_id,
        decided_by="user:maintainer" if status != "proposed" else None,
        decided_at="2026-05-15T22:31:00Z" if status != "proposed" else None,
        created_at="2026-05-15T22:30:00Z",
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Example\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "docs" / "adr" / "0001.md").write_text("# ADR\n")
    (repo / "pyproject.toml").write_text("[project]\nname = \"example\"\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs", "pyproject.toml")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        env={
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_AUTHOR_NAME": "Craik Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Craik Test",
        },
    )
