import os
from pathlib import Path

from craik.runtime.projects.public_docs import (
    classify_work_product,
    decision_record_suggestions,
    generated_doc_provenance,
    public_docs_findings,
    stale_documentation_findings,
)


def test_work_product_classifier_separates_public_internal_and_private_paths() -> None:
    assert classify_work_product("docs/reference/cli.md").boundary == "public"
    assert classify_work_product("README.md").boundary == "public"
    assert classify_work_product("src/craik/runtime/public_docs.py").boundary == "internal"
    assert classify_work_product(".github/workflows/ci.yml").boundary == "internal"
    assert classify_work_product(".craik/secrets/stigmem-18765-api-key").boundary == "private"


def test_public_docs_findings_catch_obvious_private_leaks(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(
        "Secret path: /Users/bjones/.craik\n"
        "Token: bearer abcdefghijklmnopqrstuvwxyz\n"
        "This is an internal-only task.\n"
    )

    findings = public_docs_findings(tmp_path)

    assert [finding.kind for finding in findings] == [
        "developer home path",
        "raw bearer token",
        "private issue note",
    ]
    assert decision_record_suggestions(findings) == [
        "Record a public documentation path-redaction decision.",
        "Record a public documentation secret-handling decision.",
        "Record a public/private task naming decision.",
    ]


def test_generated_doc_provenance_builds_evidence_links() -> None:
    provenance = generated_doc_provenance(
        doc_path="docs/reference/generated/api.md",
        source_paths=["src/craik/cli.py", "tests/test_cli.py"],
    )

    assert provenance.doc_path == "docs/reference/generated/api.md"
    assert [item.locator for item in provenance.evidence] == [
        "src/craik/cli.py",
        "tests/test_cli.py",
    ]
    assert provenance.evidence[0].metadata["generated_doc"] == provenance.doc_path


def test_stale_documentation_detection_compares_source_mtimes(tmp_path: Path) -> None:
    doc = tmp_path / "docs" / "reference.md"
    source = tmp_path / "src" / "runtime.py"
    doc.parent.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    doc.write_text("old docs")
    source.write_text("new source")
    os.utime(doc, (10, 10))
    os.utime(source, (20, 20))

    findings = stale_documentation_findings(
        root=tmp_path,
        doc_path="docs/reference.md",
        source_paths=["src/runtime.py"],
    )

    assert findings[0].summary == "docs/reference.md is older than src/runtime.py"
