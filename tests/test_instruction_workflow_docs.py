import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"
WORKFLOW_DOC = Path("docs/reference/instruction-distillation-workflow.md")


def test_v050_instruction_workflow_fixture_coverage() -> None:
    fixtures = json.loads(FIXTURE_PATH.read_text())

    required = {
        "craik.instruction_source",
        "craik.instruction_source_registry",
        "craik.instruction_source_snapshot",
        "craik.instruction_provenance",
        "craik.distilled_instruction_proposal",
        "craik.instruction_promotion_review",
        "craik.promoted_instruction_constraint",
        "craik.contradiction_report",
    }

    assert required <= set(fixtures)


def test_instruction_workflow_docs_cover_operator_steps() -> None:
    body = WORKFLOW_DOC.read_text()

    for phrase in (
        "Register declared sources",
        "Capture source identity",
        "Create reviewable",
        "Invalidate proposals",
        "Open <code>craik.contradiction_report</code>",
        "Record <code>craik.instruction_promotion_review</code>",
        "Consume active constraints",
    ):
        assert phrase in body
