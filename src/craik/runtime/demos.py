"""Runnable demo workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityReceipt,
    CapabilityTarget,
    ReceiptResult,
)
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.contradictions import ContradictionManager
from craik.runtime.github import GitHubReadAdapter
from craik.runtime.graph import WorkGraphExporter
from craik.runtime.handoffs import HandoffWriter
from craik.runtime.memory import (
    LocalMemoryStore,
    StigmemClient,
    StigmemConfig,
    StigmemMemoryStore,
    create_proposal,
    evidence_reference,
)
from craik.runtime.memory import (
    MemoryError as CraikMemoryError,
)
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.provider_runner import ProviderBackedRunExecutor
from craik.runtime.receipts import ReceiptStore
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task

DEMO_TASK_TITLE = "Stigmem documentation reconciliation"
DEMO_TASK_ID = "task_stigmem_documentation_reconciliation"
DEMO_PROVIDER_IDS = ("provider_openai", "provider_anthropic")


@dataclass(frozen=True)
class StigmemDocsDemo:
    """Run the Stigmem documentation reconciliation demo."""

    store: LocalStore
    github_adapter: GitHubReadAdapter | None = None

    def run(
        self,
        *,
        repo_path: Path,
        project_name: str = "Stigmem",
        stigmem_url: str | None = None,
        stigmem_api_key: str | None = None,
        github: bool = True,
        provider_ids: tuple[str, ...] | None = None,
        max_tokens: int = 24000,
    ) -> dict[str, Any]:
        selected_provider_ids = provider_ids or DEMO_PROVIDER_IDS
        registry = ProjectRegistry(self.store)
        project = registry.add_project(
            repo_path,
            name=project_name,
            memory_backend="stigmem",
            memory_scope="team",
        )
        task = create_task(
            self.store,
            title=DEMO_TASK_TITLE,
            objective=(
                "Reconcile public Stigmem documentation with implementation state while "
                "preserving immutable ADR and public/internal boundaries."
            ),
            project_id=project.id,
            requested_by="user:demo",
            priority="high",
            mode="review",
            constraints=[
                "Treat ADRs and immutable paths as read-only evidence.",
                "Do not place internal-only labels or private task identifiers in public docs.",
                "Propose memory updates unless explicit policy grants direct writes.",
            ],
            expected_outputs=[
                "case_file",
                "findings",
                "proposed_doc_updates",
                "receipts",
                "handoff",
                "memory_proposal",
                "work_graph",
            ],
        )
        stigmem_status = _stigmem_status(
            url=stigmem_url,
            api_key=stigmem_api_key,
        )
        case_file = CaseFileAssembler(
            self.store,
            github_adapter=self.github_adapter if github else None,
        ).build(task.id, max_tokens=max_tokens)
        for evidence in case_file.evidence:
            self.store.put_evidence(evidence)

        findings = _findings(case_file)
        proposed_updates = _proposed_updates(case_file)
        contradiction = ContradictionManager(self.store).open_report(
            task_id=task.id,
            facts=[
                "Public docs may describe pre-release or planned behavior.",
                (
                    "Current runtime state includes implemented CLI, policy, memory, "
                    "handoff, graph, and onboarding primitives."
                ),
            ],
            summary="Public documentation may be stale relative to current runtime state.",
            affected_artifacts=case_file.docs[:5],
            evidence_ids=[evidence.id for evidence in case_file.evidence[:3]],
            owner="user:maintainer",
            proposed_resolution=(
                "Review proposed documentation updates and apply supported public-safe changes."
            ),
        )
        proposal = LocalMemoryStore(self.store).propose(
            create_proposal(
                task_id=task.id,
                entity=f"repo:{project.name}",
                relation="craik:docs:reconciliation_demo",
                value="Craik can run the Stigmem documentation reconciliation demo workflow.",
                source="craik demo stigmem-docs",
                confidence=0.9,
                scope="team",
                trust_class="observed",
                evidence=[
                    evidence_reference(
                        task_id=task.id,
                        source="craik demo stigmem-docs",
                        locator=case_file.id,
                        summary="Demo assembled a case file and proposed reconciliation state.",
                    )
                ],
            )
        )
        receipt = ReceiptStore(self.store).record_receipt(
            _demo_receipt(
                task_id=task.id,
                policy_id=case_file.policy_envelope_id,
                summary="Stigmem documentation reconciliation demo assembled local artifacts.",
                metadata={
                    "case_file_id": case_file.id,
                    "memory_proposal_ids": [proposal.id],
                    "contradiction_ids": [contradiction.id],
                    "stigmem_status": stigmem_status["status"],
                    "github_status": case_file.github_state.get("status"),
                },
            )
        )
        handoff = HandoffWriter(self.store).create(
            task_id=task.id,
            agent="agent:craik-demo",
            summary=(
                "Stigmem documentation reconciliation demo assembled a case file, "
                "findings, proposed updates, receipts, memory proposal, and work graph."
            ),
            completed_actions=[
                "Registered the Stigmem project in local Craik state.",
                "Built the documentation reconciliation task and case file.",
                "Opened a local contradiction report for stale public documentation risk.",
                "Created a local memory proposal instead of direct Stigmem write.",
                "Recorded a capability receipt and generated this handoff.",
            ],
            artifacts=[case_file.id, contradiction.id, proposal.id],
            commands_run=["craik demo stigmem-docs"],
            tests_run=["craik policy test"],
            contradictions_opened=[contradiction.id],
            risks=findings["risks"],
            next_steps=[
                "Review proposed doc updates against cited evidence.",
                "Apply public-safe documentation updates outside immutable paths.",
                "Approve or reject the generated memory proposal.",
            ],
            memory_proposal_ids=[proposal.id],
            self_audit_notes=[
                "Demo avoids editing repository files and does not write Stigmem facts by default."
            ],
        )
        provider_executions = [
            _provider_execution_payload(execution)
            for execution in (
                ProviderBackedRunExecutor(self.store).execute(
                    task_id=task.id,
                    provider_id=provider_id,
                    grants=[_demo_shell_grant(task.id)],
                )
                for provider_id in selected_provider_ids
            )
        ]
        graph = WorkGraphExporter(self.store).export(task_id=task.id)
        return {
            "schema": "craik.demo.stigmem_docs_reconciliation",
            "version": "0.2.0",
            "status": "runnable",
            "project": project.model_dump(mode="json", by_alias=True),
            "task": task.model_dump(mode="json", by_alias=True),
            "stigmem_backend_status": stigmem_status,
            "case_file_id": case_file.id,
            "github_state": case_file.github_state,
            "findings": findings,
            "proposed_doc_updates": proposed_updates,
            "receipt_ids": [receipt.id],
            "handoff_id": handoff.id,
            "memory_proposal_ids": [proposal.id],
            "memory_write": {
                "status": "proposal_created",
                "proposal_id": proposal.id,
                "direct_write": "not_requested",
            },
            "contradiction_ids": [contradiction.id],
            "provider_executions": provider_executions,
            "work_graph_id": graph.id,
            "next_commands": [
                f"craik case show {task.id}",
                f"craik contradictions show {contradiction.id}",
                f"craik memory show {proposal.id}",
                f"craik handoff show {task.id}",
                f"craik graph export --task-id {task.id}",
            ],
        }


def _stigmem_status(*, url: str | None, api_key: str | None) -> dict[str, Any]:
    if not url:
        return {
            "status": "not_configured",
            "message": "Set CRAIK_STIGMEM_URL to run live compatibility detection.",
        }
    try:
        capabilities = StigmemMemoryStore(
            StigmemClient(StigmemConfig(node_url=url, api_key=api_key))
        ).discover()
    except CraikMemoryError as error:
        return {"status": "error", "message": str(redact(str(error)).value)}
    return {
        "status": "loaded",
        "capabilities": capabilities.model_dump(mode="json", by_alias=True),
    }


def _findings(case_file: Any) -> dict[str, list[str]]:
    risks = list(case_file.stale_risks)
    if case_file.adrs:
        risks.append("ADRs are present and must remain immutable evidence.")
    if case_file.github_state.get("status") in {"not_loaded", "error", "partial"}:
        risks.append("GitHub context is incomplete; review remote issue and PR state manually.")
    if not case_file.facts:
        risks.append("No Stigmem facts were loaded into the case file; use memory proposal review.")
    return {
        "evidence_ids": [evidence.id for evidence in case_file.evidence],
        "risks": sorted(set(str(redact(risk).value) for risk in risks)),
        "public_internal_boundary": [
            "Public docs must describe product state without internal-only labels.",
            (
                "Internal planning labels, private task names, and local paths must stay out "
                "of public docs."
            ),
        ],
    }


def _proposed_updates(case_file: Any) -> list[dict[str, str]]:
    updates: list[dict[str, str]] = []
    for path in case_file.docs[:5]:
        updates.append(
            {
                "path": path,
                "change": (
                    "Review for stale pre-release language and update only when supported by "
                    "case-file evidence."
                ),
            }
        )
    if not updates:
        updates.append(
            {
                "path": "README.md",
                "change": "Add public-safe current-state documentation when evidence supports it.",
            }
        )
    return updates


def _demo_receipt(
    *,
    task_id: str,
    policy_id: str,
    summary: str,
    metadata: dict[str, Any],
) -> CapabilityReceipt:
    return CapabilityReceipt(
        id=f"receipt_demo_{task_id.removeprefix('task_')}",
        task_id=task_id,
        actor="agent:craik-demo",
        capability="demo.stigmem_docs_reconciliation",
        target="local_runtime_state",
        policy_profile="strict",
        fail_open=False,
        reason="Run accepted Stigmem documentation reconciliation demo.",
        result=ReceiptResult(
            status="passed",
            summary=str(redact(summary).value),
            metadata={"policy_envelope_id": policy_id, **redact(metadata).value},
        ),
        redacted=True,
        created_at=datetime.now(UTC),
    )


def _demo_shell_grant(task_id: str) -> CapabilityGrant:
    return CapabilityGrant(
        id=f"grant_{task_id.removeprefix('task_')}_demo_shell",
        task_id=task_id,
        capability="shell.execute",
        target=CapabilityTarget(paths=["fixture-action"]),
        operations=["execute"],
        reason="Allow deterministic provider-backed demo fixture action.",
        approved_by="user:demo",
    )


def _provider_execution_payload(execution: Any) -> dict[str, Any]:
    return {
        "provider_id": execution.compiled_prompt.runner_id,
        "run_id": execution.run.id,
        "run_status": execution.run.status,
        "handoff_id": execution.handoff.id,
        "handoff_status": execution.handoff.status,
        "receipt_ids": execution.run.receipt_ids,
        "provider_result_ids": [result.response_id for result in execution.provider_results],
        "provider_families": sorted(
            {result.provider_family for result in execution.provider_results}
        ),
        "interrupted_error": execution.interrupted_error,
    }
