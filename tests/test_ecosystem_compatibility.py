from craik.runtime.adjacent_runtime_bridge import (
    AdjacentRuntimeBridgeSurface,
    adjacent_runtime_bridge_decision,
)
from craik.runtime.import_dry_run import (
    ImportCandidateRecord,
    ImportDryRunReport,
    ImportMappedRecord,
)
from craik.runtime.locale_i18n import (
    LocalePreference,
    TranslatableDocMetadata,
    resolve_doc_locale,
)
from craik.runtime.migration_maps import MigrationFieldMap, MigrationMap
from craik.runtime.multi_agent_workflow_bridge import (
    MultiAgentWorkflowBridgeSurface,
    multi_agent_workflow_bridge_decision,
)
from craik.runtime.secret_migration import (
    SecretMigrationPolicy,
    SecretMigrationPolicyRule,
    evaluate_secret_migration,
)


def test_ecosystem_import_path_preserves_policy_receipts_and_redaction() -> None:
    migration_map = MigrationMap(
        id="migration_map_memory",
        surface="memory",
        source_name="Adjacent Memory Store",
        field_maps=[
            MigrationFieldMap(
                source_field="subject",
                target_field="entity",
                support="supported",
                transform_notes="Use the source subject as the memory entity.",
            ),
            MigrationFieldMap(
                source_field="api_token",
                target_field=None,
                support="unsupported",
                transform_notes="Secret values are reconfigured, not imported.",
                unsupported_reason="secret material is not portable",
            ),
        ],
        compatibility_notes=["Secret-bearing fields require dry-run warnings."],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_migration_map"],
        receipt_ids=["receipt_migration_map"],
    )
    secret_policy = SecretMigrationPolicy(
        id="secret_policy",
        source_name="Adjacent Memory Store",
        rules=[
            SecretMigrationPolicyRule(
                source_field="api_token",
                handling="reconfigure",
                reason="Operators must create target runtime tokens.",
                dry_run_warning="api_token will not be copied.",
                requires_operator_action=True,
            )
        ],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_secret_policy"],
        receipt_ids=["receipt_secret_policy"],
    )
    secret_decision = evaluate_secret_migration(
        source_field="api_token",
        contains_secret=True,
        policy=secret_policy,
    )
    dry_run = ImportDryRunReport(
        id="import_dry_run_memory",
        source_name="Adjacent Memory Store",
        source_kind="memory",
        candidates=[
            ImportCandidateRecord(
                source_id="memory_1",
                source_type="memory",
                summary="Migrates one redacted memory record.",
            )
        ],
        mapped_records=[
            ImportMappedRecord(
                source_id="memory_1",
                target_schema="craik.memory_fact",
                target_id="fact_1",
                status="warning",
                warnings=[secret_decision.warning or "secret field requires operator review"],
            )
        ],
        warnings=[secret_decision.warning or "secret field requires operator review"],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_import_source"],
        receipt_ids=["receipt_import_dry_run"],
    )

    assert migration_map.policy_envelope_id == dry_run.policy_envelope_id
    assert migration_map.field_maps[1].support == "unsupported"
    assert secret_decision.status == "operator_reconfiguration_required"
    assert secret_decision.copied_secret_value is False
    assert dry_run.mutated_state is False
    assert dry_run.redacted is True
    assert dry_run.mapped_records[0].warnings == ["api_token will not be copied."]


def test_ecosystem_bridges_share_required_policy_receipt_and_redaction_boundaries() -> None:
    adjacent = adjacent_runtime_bridge_decision(
        AdjacentRuntimeBridgeSurface(
            id="local_runner_bridge",
            runtime_name="Local Runner",
            support_level="supported",
            policy_envelope_id="policy_bridge",
        )
    )
    workflow = multi_agent_workflow_bridge_decision(
        MultiAgentWorkflowBridgeSurface(
            id="review_queue_bridge",
            workflow_name="Review Queue",
            support_level="supported",
            policy_envelope_id="policy_bridge",
        )
    )

    assert adjacent.allowed is True
    assert workflow.allowed is True
    for decision in (adjacent, workflow):
        assert "policy_envelope" in decision.required_controls
        assert "evidence_links" in decision.required_controls
        assert "receipts" in decision.required_controls


def test_ecosystem_bridges_block_prohibited_cross_runtime_behavior() -> None:
    adjacent = adjacent_runtime_bridge_decision(
        AdjacentRuntimeBridgeSurface(
            id="unsafe_adjacent_bridge",
            runtime_name="Adjacent Runtime",
            support_level="supported",
            policy_envelope_id="policy_bridge",
            grants_unbounded_tool_access=True,
        )
    )
    workflow = multi_agent_workflow_bridge_decision(
        MultiAgentWorkflowBridgeSurface(
            id="unsafe_workflow_bridge",
            workflow_name="External Workflow",
            support_level="supported",
            policy_envelope_id="policy_bridge",
            allows_unbounded_dispatch=True,
        )
    )

    assert adjacent.allowed is False
    assert adjacent.status == "blocked"
    assert workflow.allowed is False
    assert workflow.status == "blocked"


def test_ecosystem_locale_resolution_preserves_translation_metadata_boundaries() -> None:
    metadata = TranslatableDocMetadata(
        stable_id="guide.translated_docs",
        source_path="docs/guides/translated-docs.md",
        source_locale="en-US",
        available_locales=["en-US", "es"],
        translated_paths={"es": "docs/es/guides/translated-docs.md"},
        policy_envelope_id="policy_i18n",
        evidence_ids=["evidence_translated_docs_source"],
        receipt_ids=["receipt_translation_review"],
    )
    preference = LocalePreference(
        id="project_locale",
        preferred_locale="es-MX",
    )

    resolution = resolve_doc_locale(metadata=metadata, preference=preference)

    assert resolution.status == "fallback"
    assert resolution.resolved_locale == "es"
    assert resolution.fallback_chain == ["es-MX", "es"]
    assert resolution.stable_id == "guide.translated_docs"
    assert resolution.policy_envelope_id == "policy_i18n"
    assert resolution.evidence_ids == ["evidence_translated_docs_source"]
    assert resolution.receipt_ids == ["receipt_translation_review"]
    assert resolution.redaction_required is True


def test_ecosystem_docs_expectations_reference_public_compatibility_guides() -> None:
    docs = [
        "docs/guides/mcp-ecosystem-compatibility.md",
        "docs/guides/translated-docs.md",
        "docs/reference/adjacent-runtime-bridge.md",
        "docs/reference/multi-agent-workflow-bridge.md",
        "docs/reference/locale-i18n-framework.md",
        "docs/reference/secret-migration-policy.md",
    ]

    for path in docs:
        assert not path.startswith("/")
        assert ".." not in path
        assert path.endswith(".md")
