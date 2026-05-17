import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DOC_PARTS = {".docusaurus", "build", "node_modules"}
IGNORED_DOC_PREFIXES = {(Path("docs") / "blog"), (Path("docs") / "docs")}
DOC_PATHS = [
    Path("README.md"),
    *sorted(
        path
        for path in Path("docs").rglob("*.md")
        if not IGNORED_DOC_PARTS.intersection(path.parts)
        and not any(path.is_relative_to(prefix) for prefix in IGNORED_DOC_PREFIXES)
    ),
]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_local_markdown_links_resolve() -> None:
    missing: list[str] = []
    for relative in DOC_PATHS:
        source = ROOT / relative
        for raw_target in LINK_PATTERN.findall(source.read_text()):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            candidate = (source.parent / target).resolve()
            if not candidate.exists():
                missing.append(f"{relative}: {raw_target}")

    assert missing == []


def test_v0_docs_tree_covers_required_areas() -> None:
    required = [
        "docs/index.md",
        "docs/concepts/case-files.md",
        "docs/concepts/governance.md",
        "docs/concepts/handoffs.md",
        "docs/concepts/memory-and-stigmem.md",
        "docs/concepts/receipts.md",
        "docs/concepts/work-graph.md",
        "docs/guides/installation.md",
        "docs/guides/quickstart.md",
        "docs/reference/cli.md",
        "docs/reference/config.md",
        "docs/reference/memory-backends.md",
        "docs/reference/policy-profiles.md",
        "docs/reference/schemas.md",
        "docs/security/secrets.md",
        "docs/limitations.md",
    ]

    assert [path for path in required if not (ROOT / path).exists()] == []
