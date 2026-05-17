from craik.runtime.companions.visual_workspace import (
    VisualWorkspaceSurface,
    visual_workspace_decision,
)


def test_visual_workspace_allows_supported_read_only_surface() -> None:
    decision = visual_workspace_decision(
        VisualWorkspaceSurface(
            id="visual_work_graph_view",
            support_level="supported",
            docs_ref="docs/reference/visual-workspace.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.required_controls == [
        "read_only",
        "visual_state_redaction",
        "accessibility_controls",
        "work_graph_links",
        "evidence_links",
        "receipts",
        "documented_decision",
    ]


def test_visual_workspace_requires_review_for_experimental_surface() -> None:
    decision = visual_workspace_decision(
        VisualWorkspaceSurface(
            id="visual_live_canvas",
            support_level="experimental",
            docs_ref="docs/reference/visual-workspace.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental visual workspace surfaces require explicit review"


def test_visual_workspace_defers_deferred_surface() -> None:
    decision = visual_workspace_decision(
        VisualWorkspaceSurface(
            id="visual_mutating_canvas",
            support_level="deferred",
            docs_ref="docs/reference/visual-workspace.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "deferred"
    assert decision.reason == "visual workspace surface is deferred by product posture"


def test_visual_workspace_blocks_raw_canvas_payloads() -> None:
    decision = visual_workspace_decision(
        VisualWorkspaceSurface(
            id="visual_raw_canvas_store",
            support_level="supported",
            stores_raw_canvas_payloads=True,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "visual workspace surfaces must not persist raw canvas payloads"


def test_visual_workspace_blocks_missing_required_controls() -> None:
    cases = [
        (
            VisualWorkspaceSurface(
                id="visual_mutating",
                support_level="supported",
                read_only=False,
            ),
            "visual workspace mutation requires a later explicit bridge",
        ),
        (
            VisualWorkspaceSurface(
                id="visual_unredacted",
                support_level="supported",
                visual_state_redacted=False,
            ),
            "visual workspace state requires redaction",
        ),
        (
            VisualWorkspaceSurface(
                id="visual_no_accessibility",
                support_level="supported",
                accessibility_controls=False,
            ),
            "visual workspace surfaces require accessibility controls",
        ),
        (
            VisualWorkspaceSurface(
                id="visual_no_graph",
                support_level="supported",
                preserves_work_graph_links=False,
            ),
            "visual workspace surfaces must preserve work graph links",
        ),
        (
            VisualWorkspaceSurface(
                id="visual_no_evidence",
                support_level="supported",
                preserves_evidence_links=False,
            ),
            "visual workspace surfaces must preserve evidence links",
        ),
        (
            VisualWorkspaceSurface(
                id="visual_no_receipts",
                support_level="supported",
                requires_receipts=False,
            ),
            "visual workspace surfaces require receipts",
        ),
    ]

    for surface, reason in cases:
        decision = visual_workspace_decision(surface)

        assert decision.allowed is False
        assert decision.status == "blocked"
        assert decision.reason == reason
