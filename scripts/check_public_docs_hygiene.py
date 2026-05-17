"""Check public documentation for private paths, obvious secrets, and task-only text."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOC_ROOTS = [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "docs"]
EXCLUDED_PARTS = {
    ".docusaurus",
    "build",
    "node_modules",
    "package-lock.json",
}

PATTERNS = {
    "developer home path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "macos private temp path": re.compile(r"/private/(?:tmp|var)/"),
    "raw bearer token": re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{16,}"),
    "api key assignment": re.compile(
        r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
    "private issue note": re.compile(r"(?i)\b(private|internal)-only task\b"),
    "local stigmem secret file": re.compile(r"stigmem-[0-9]+-api-key"),
}


def main() -> int:
    failures: list[str] = []
    for path in _public_doc_files():
        text = path.read_text(encoding="utf-8")
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT)}:{line_no}: {name}")

    if failures:
        print("Public documentation hygiene checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Public documentation hygiene checks passed.")
    return 0


def _public_doc_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLIC_DOC_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".mdx", ".js", ".css"}:
                if not EXCLUDED_PARTS.intersection(path.parts):
                    files.append(path)
    return sorted(files)


if __name__ == "__main__":
    raise SystemExit(main())
