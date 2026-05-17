from craik.runtime.sandbox.mcp_export import MCPExportSurface, mcp_export_decision


def test_mcp_export_allows_stable_documented_surface() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_case_file_read",
            name="Case file read tools",
            stability="stable",
            capabilities=["file.read", "memory.read"],
            docs_ref="docs/reference/mcp-export-boundary.md",
        )
    )

    assert decision.allowed is True
    assert decision.status == "exportable"
    assert decision.reason == (
        "stable MCP surface preserves capability, receipt, and secret boundaries"
    )
    assert decision.required_controls == [
        "redaction",
        "capability_grants",
        "documented_contract",
    ]


def test_mcp_export_blocks_secret_values() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_secret_dump",
            name="Secret dump",
            stability="stable",
            exposes_secret_values=True,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "MCP exports must not expose secret values"


def test_mcp_export_blocks_internal_surfaces() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_store_debug",
            name="Store debug internals",
            stability="internal",
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "MCP exports must not expose unstable internal surfaces"


def test_mcp_export_blocks_capabilities_without_grants() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_repo_write",
            name="Repository write tools",
            stability="stable",
            capabilities=["file.write"],
            requires_capability_grant=False,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "MCP capability surfaces require explicit grants"
    assert decision.required_controls == ["redaction", "capability_grants", "receipts"]


def test_mcp_export_blocks_side_effects_without_receipts() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_shell",
            name="Shell tools",
            stability="stable",
            capabilities=["shell.execute"],
            requires_receipts=False,
        )
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.reason == "MCP side-effect surfaces require receipts"
    assert decision.required_controls == ["redaction", "capability_grants", "receipts"]


def test_mcp_export_requires_review_for_experimental_surface() -> None:
    decision = mcp_export_decision(
        MCPExportSurface(
            id="mcp_sandbox_preview",
            name="Sandbox preview",
            stability="experimental",
            capabilities=["network.access"],
            docs_ref="docs/reference/mcp-export-boundary.md",
        )
    )

    assert decision.allowed is False
    assert decision.status == "review_required"
    assert decision.reason == "experimental MCP surfaces require compatibility review"
    assert decision.required_controls == [
        "redaction",
        "capability_grants",
        "receipts",
        "documented_contract",
    ]
