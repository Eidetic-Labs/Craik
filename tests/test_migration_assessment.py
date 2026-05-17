import pytest
from pydantic import ValidationError

from craik.runtime.migration_assessment import (
    AdjacentToolMapping,
    AdjacentToolMigrationAssessment,
    MultiAgentWorkflowMapping,
    MultiAgentWorkflowMigrationAssessment,
)


def test_adjacent_tool_migration_assessment_records_supported_mappings() -> None:
    assessment = AdjacentToolMigrationAssessment(
        id="migration_assessment_editor_tasks",
        tool_name="Editor Task Tool",
        support="supported",
        mappings=[
            AdjacentToolMapping(
                source_concept="workspace",
                target_concept="project",
                support="supported",
                notes="Workspace maps to Craik project profile.",
                required_controls=["redaction"],
            ),
            AdjacentToolMapping(
                source_concept="todo",
                target_concept="task",
                support="supported",
                notes="Todo maps to task request.",
                required_controls=["receipts"],
            ),
        ],
        security_notes=["Secrets must be reconfigured, not imported."],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_tool_docs"],
        receipt_ids=["receipt_migration_assessment"],
    )

    assert assessment.support == "supported"
    assert assessment.redaction_required is True
    assert assessment.mappings[0].target_concept == "project"
    assert assessment.evidence_ids == ["evidence_tool_docs"]


def test_adjacent_tool_migration_assessment_allows_partial_mappings() -> None:
    assessment = AdjacentToolMigrationAssessment(
        id="migration_assessment_editor_tasks",
        tool_name="Editor Task Tool",
        support="partial",
        mappings=[
            AdjacentToolMapping(
                source_concept="workspace",
                target_concept="project",
                support="supported",
                notes="Workspace maps to Craik project profile.",
            ),
            AdjacentToolMapping(
                source_concept="inline credential",
                target_concept="config",
                support="unsupported",
                notes="Secrets are not imported.",
                unsupported_fields=["secret_value"],
                required_controls=["secret_reconfiguration"],
            ),
        ],
        security_notes=["Inline credentials must not be copied."],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_tool_docs"],
        receipt_ids=["receipt_migration_assessment"],
    )

    assert assessment.support == "partial"
    assert assessment.mappings[1].unsupported_fields == ["secret_value"]


def test_adjacent_tool_mapping_requires_unsupported_fields_for_incomplete_support() -> None:
    with pytest.raises(ValidationError, match="unsupported_fields"):
        AdjacentToolMapping(
            source_concept="inline credential",
            target_concept="config",
            support="unsupported",
            notes="Secrets are not imported.",
        )


def test_adjacent_tool_migration_assessment_validates_support_consistency() -> None:
    with pytest.raises(ValidationError, match="assessment support"):
        AdjacentToolMigrationAssessment(
            id="migration_assessment_editor_tasks",
            tool_name="Editor Task Tool",
            support="supported",
            mappings=[
                AdjacentToolMapping(
                    source_concept="inline credential",
                    target_concept="config",
                    support="unsupported",
                    notes="Secrets are not imported.",
                    unsupported_fields=["secret_value"],
                )
            ],
            policy_envelope_id="policy_migration",
            evidence_ids=["evidence_tool_docs"],
            receipt_ids=["receipt_migration_assessment"],
        )


def test_adjacent_tool_migration_assessment_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        AdjacentToolMigrationAssessment(
            id="migration_assessment_editor_tasks",
            tool_name="Editor Task Tool",
            support="supported",
            mappings=[
                AdjacentToolMapping(
                    source_concept="workspace",
                    target_concept="project",
                    support="supported",
                    notes="Workspace maps to project.",
                )
            ],
            policy_envelope_id="",
            evidence_ids=["evidence_tool_docs"],
            receipt_ids=["receipt_migration_assessment"],
        )


def test_multi_agent_workflow_migration_assessment_records_mappings() -> None:
    assessment = MultiAgentWorkflowMigrationAssessment(
        id="workflow_migration_assessment_review_swarm",
        workflow_name="Review Swarm",
        support="supported",
        mappings=[
            MultiAgentWorkflowMapping(
                source_concept="reviewer agent",
                target_concept="agent",
                target_craik_surface="agent role",
                support="supported",
                notes="Reviewer maps to Craik reviewer role.",
                required_controls=["policy_envelope"],
            ),
            MultiAgentWorkflowMapping(
                source_concept="approval step",
                target_concept="approval",
                target_craik_surface="human delegation",
                support="supported",
                notes="Approval maps to reviewable delegation.",
                required_controls=["receipt"],
            ),
        ],
        policy_notes=["External queue actions require receipts."],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_workflow_docs"],
        receipt_ids=["receipt_workflow_migration_assessment"],
    )

    assert assessment.support == "supported"
    assert assessment.mappings[0].target_concept == "agent"
    assert assessment.policy_notes == ["External queue actions require receipts."]


def test_multi_agent_workflow_migration_assessment_allows_partial_mappings() -> None:
    assessment = MultiAgentWorkflowMigrationAssessment(
        id="workflow_migration_assessment_review_swarm",
        workflow_name="Review Swarm",
        support="partial",
        mappings=[
            MultiAgentWorkflowMapping(
                source_concept="reviewer agent",
                target_concept="agent",
                target_craik_surface="agent role",
                support="supported",
                notes="Reviewer maps to Craik reviewer role.",
            ),
            MultiAgentWorkflowMapping(
                source_concept="unbounded autonomous queue",
                target_concept="queue",
                target_craik_surface="delegation queue",
                support="unsupported",
                notes="Unbounded queues require explicit policy and receipts.",
                unsupported_fields=["unbounded_auto_dispatch"],
            ),
        ],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_workflow_docs"],
        receipt_ids=["receipt_workflow_migration_assessment"],
    )

    assert assessment.support == "partial"
    assert assessment.mappings[1].unsupported_fields == ["unbounded_auto_dispatch"]


def test_multi_agent_workflow_mapping_requires_unsupported_fields_for_incomplete_support() -> None:
    with pytest.raises(ValidationError, match="unsupported_fields"):
        MultiAgentWorkflowMapping(
            source_concept="unbounded autonomous queue",
            target_concept="queue",
            target_craik_surface="delegation queue",
            support="partial",
            notes="Needs explicit bounds.",
        )


def test_multi_agent_workflow_assessment_validates_support_consistency() -> None:
    with pytest.raises(ValidationError, match="workflow mappings"):
        MultiAgentWorkflowMigrationAssessment(
            id="workflow_migration_assessment_review_swarm",
            workflow_name="Review Swarm",
            support="supported",
            mappings=[
                MultiAgentWorkflowMapping(
                    source_concept="unbounded autonomous queue",
                    target_concept="queue",
                    target_craik_surface="delegation queue",
                    support="unsupported",
                    notes="Needs explicit bounds.",
                    unsupported_fields=["unbounded_auto_dispatch"],
                )
            ],
            policy_envelope_id="policy_migration",
            evidence_ids=["evidence_workflow_docs"],
            receipt_ids=["receipt_workflow_migration_assessment"],
        )
