import pytest
from pydantic import ValidationError

from craik.runtime.projects.migration_maps import MigrationFieldMap, MigrationMap


def test_migration_map_records_memory_field_mappings() -> None:
    migration_map = MigrationMap(
        id="migration_map_memory",
        surface="memory",
        source_name="Adjacent Memory Store",
        field_maps=[
            MigrationFieldMap(
                source_field="subject",
                target_field="entity",
                support="supported",
                transform_notes="Use source subject as fact entity.",
            ),
            MigrationFieldMap(
                source_field="secret_value",
                target_field=None,
                support="unsupported",
                transform_notes="Secrets are reconfigured, not imported.",
                unsupported_reason="secret material is not portable",
            ),
        ],
        compatibility_notes=["Confidence defaults need operator review."],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_map"],
        receipt_ids=["receipt_map"],
    )

    assert migration_map.surface == "memory"
    assert migration_map.field_maps[0].target_field == "entity"
    assert migration_map.field_maps[1].unsupported_reason == "secret material is not portable"
    assert migration_map.compatibility_notes == ["Confidence defaults need operator review."]


def test_migration_map_covers_skill_and_config_surfaces() -> None:
    for surface in ("skill", "config"):
        migration_map = MigrationMap(
            id=f"migration_map_{surface}",
            surface=surface,
            source_name="Adjacent Tool",
            field_maps=[
                MigrationFieldMap(
                    source_field="name",
                    target_field="id",
                    support="supported",
                    transform_notes="Normalize source name to stable id.",
                )
            ],
            policy_envelope_id="policy_migration",
            evidence_ids=["evidence_map"],
            receipt_ids=["receipt_map"],
        )

        assert migration_map.surface == surface


def test_migration_field_map_validates_supported_and_unsupported_fields() -> None:
    with pytest.raises(ValidationError, match="target_field"):
        MigrationFieldMap(
            source_field="name",
            target_field=None,
            support="supported",
            transform_notes="Missing target.",
        )

    with pytest.raises(ValidationError, match="unsupported_reason"):
        MigrationFieldMap(
            source_field="secret_value",
            target_field=None,
            support="unsupported",
            transform_notes="Secrets are not imported.",
        )


def test_migration_map_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        MigrationMap(
            id="migration_map_memory",
            surface="memory",
            source_name="Adjacent Memory Store",
            field_maps=[
                MigrationFieldMap(
                    source_field="subject",
                    target_field="entity",
                    support="supported",
                    transform_notes="Use source subject as fact entity.",
                )
            ],
            policy_envelope_id="",
            evidence_ids=["evidence_map"],
            receipt_ids=["receipt_map"],
        )

    with pytest.raises(ValidationError):
        MigrationMap(
            id="migration_map_memory",
            surface="memory",
            source_name="Adjacent Memory Store",
            field_maps=[
                MigrationFieldMap(
                    source_field="subject",
                    target_field="entity",
                    support="supported",
                    transform_notes="Use source subject as fact entity.",
                )
            ],
            policy_envelope_id="policy_migration",
            evidence_ids=[],
            receipt_ids=["receipt_map"],
        )
