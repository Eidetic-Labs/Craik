"""Public documentation boundary and provenance helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from craik.contracts.models import EvidenceReference

WorkProductBoundary = Literal["public", "internal", "private"]
PublicDocsFindingSeverity = Literal["error", "warning"]


@dataclass(frozen=True)
class WorkProductClassification:
    """Boundary classification for one work product path."""

    path: str
    boundary: WorkProductBoundary
    reason: str


@dataclass(frozen=True)
class PublicDocsFinding:
    """One public documentation boundary finding."""

    path: str
    line: int
    kind: str
    severity: PublicDocsFindingSeverity
    summary: str


@dataclass(frozen=True)
class GeneratedDocProvenance:
    """Evidence links for generated or synthesized documentation."""

    doc_path: str
    evidence: list[EvidenceReference] = field(default_factory=list)


@dataclass(frozen=True)
class StaleDocumentationFinding:
    """A generated doc that is older than one of its source artifacts."""

    doc_path: str
    source_path: str
    summary: str


PUBLIC_DOC_ROOTS = ("README.md", "CHANGELOG.md", "docs/")
INTERNAL_ROOTS = ("src/", "tests/", "scripts/", ".github/")
PRIVATE_ROOTS = (".codex/", ".craik/", ".env", "secrets/")
PUBLIC_DOC_SUFFIXES = {".md", ".mdx", ".js", ".css"}
EXCLUDED_PUBLIC_DOC_PARTS = {".docusaurus", "build", "node_modules", "package-lock.json"}

PUBLIC_DOC_PATTERNS: dict[str, re.Pattern[str]] = {
    "developer home path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "macos private temp path": re.compile(r"/private/(?:tmp|var)/"),
    "raw bearer token": re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{16,}"),
    "api key assignment": re.compile(
        r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
    "private issue note": re.compile(r"(?i)\b(private|internal)-only task\b"),
    "local stigmem secret file": re.compile(r"stigmem-[0-9]+-api-key"),
}


def classify_work_product(path: str | Path) -> WorkProductClassification:
    """Classify whether a path belongs to the public, internal, or private surface."""
    normalized = _normalize(path)
    if any(normalized == root.rstrip("/") or normalized.startswith(root) for root in PRIVATE_ROOTS):
        return WorkProductClassification(normalized, "private", "private state or secret path")
    if any(
        normalized == root.rstrip("/") or normalized.startswith(root) for root in PUBLIC_DOC_ROOTS
    ):
        return WorkProductClassification(normalized, "public", "public documentation surface")
    if any(
        normalized == root.rstrip("/") or normalized.startswith(root) for root in INTERNAL_ROOTS
    ):
        return WorkProductClassification(normalized, "internal", "implementation or CI surface")
    return WorkProductClassification(normalized, "internal", "unclassified repo work product")


def public_doc_files(root: Path) -> list[Path]:
    """Return public documentation files that should be scanned."""
    files: list[Path] = []
    for relative_root in PUBLIC_DOC_ROOTS:
        path = root / relative_root
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            continue
        for candidate in path.rglob("*"):
            if candidate.is_file() and candidate.suffix in PUBLIC_DOC_SUFFIXES:
                if not EXCLUDED_PUBLIC_DOC_PARTS.intersection(candidate.parts):
                    files.append(candidate)
    return sorted(files)


def public_docs_findings(root: Path) -> list[PublicDocsFinding]:
    """Scan public docs for obvious private-boundary leaks."""
    findings: list[PublicDocsFinding] = []
    for path in public_doc_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for kind, pattern in PUBLIC_DOC_PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(
                    PublicDocsFinding(
                        path=relative,
                        line=line_no,
                        kind=kind,
                        severity="error",
                        summary=f"{relative}:{line_no}: {kind}",
                    )
                )
    return findings


def generated_doc_provenance(
    *,
    doc_path: str | Path,
    source_paths: list[str | Path],
) -> GeneratedDocProvenance:
    """Build evidence links for generated documentation."""
    normalized_doc = _normalize(doc_path)
    evidence = [
        EvidenceReference(
            id=f"evidence_{_slug(normalized_doc)}_{index}",
            source=_normalize(source_path),
            kind="file",
            locator=_normalize(source_path),
            summary=f"Source evidence for generated doc {normalized_doc}.",
            metadata={"generated_doc": normalized_doc},
        )
        for index, source_path in enumerate(source_paths, start=1)
    ]
    return GeneratedDocProvenance(doc_path=normalized_doc, evidence=evidence)


def stale_documentation_findings(
    *,
    root: Path,
    doc_path: str | Path,
    source_paths: list[str | Path],
) -> list[StaleDocumentationFinding]:
    """Return sources newer than a generated documentation artifact."""
    doc = root / doc_path
    if not doc.exists():
        return [
            StaleDocumentationFinding(
                doc_path=_normalize(doc_path),
                source_path=_normalize(source),
                summary=f"generated doc {_normalize(doc_path)} is missing",
            )
            for source in source_paths
        ]
    doc_mtime = doc.stat().st_mtime
    findings: list[StaleDocumentationFinding] = []
    for source_path in source_paths:
        source = root / source_path
        if source.exists() and source.stat().st_mtime > doc_mtime:
            findings.append(
                StaleDocumentationFinding(
                    doc_path=_normalize(doc_path),
                    source_path=_normalize(source_path),
                    summary=f"{_normalize(doc_path)} is older than {_normalize(source_path)}",
                )
            )
    return findings


def decision_record_suggestions(findings: list[PublicDocsFinding]) -> list[str]:
    """Suggest decision records for repeated or policy-shaped public-boundary findings."""
    kinds = sorted({finding.kind for finding in findings})
    suggestions: list[str] = []
    if any("path" in kind for kind in kinds):
        suggestions.append("Record a public documentation path-redaction decision.")
    if any("token" in kind or "key" in kind or "secret" in kind for kind in kinds):
        suggestions.append("Record a public documentation secret-handling decision.")
    if any("task" in kind or "issue note" in kind for kind in kinds):
        suggestions.append("Record a public/private task naming decision.")
    return suggestions


def _normalize(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
