"""Validate raw-HTML <a href> links in Docusaurus markdown.

Docusaurus's `onBrokenLinks: throw` only checks markdown-syntax links
(`[text](url)`). Raw HTML `<a href="...">` tags inside markdown — used
heavily for card grids in this repo — slip past that check, which has
caused large families of silent 404s in the past.

This script audits the markdown source statically (no Docusaurus build
required) so it runs in pre-commit and CI before the build step.

Resolution rules mirror Docusaurus defaults:

* `docs/<name>.md`        -> `/docs/<name>/`
* `docs/<dir>/<name>.md`  -> `/docs/<dir>/<name>/`
* `docs/<dir>/index.md`   -> `/docs/<dir>/`
* Numeric-prefix path segments (`0007-foo`) have the `0007-` stripped.

Exits non-zero on any broken raw-HTML href.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXCLUDE_DIRS = {"node_modules", "build", ".docusaurus", "src", "static"}

HREF_ATTR_RE = re.compile(r'<a\b[^>]*\bhref="([^"]+)"', re.IGNORECASE)
NUM_PREFIX_RE = re.compile(r"^\d+-")


def md_files() -> list[Path]:
    out: list[Path] = []
    for p in DOCS.rglob("*"):
        if not p.is_file() or p.suffix not in (".md", ".mdx"):
            continue
        if EXCLUDE_DIRS & set(p.relative_to(DOCS).parts):
            continue
        out.append(p)
    return out


def slug_for(md_path: Path) -> str:
    """Map a source markdown file to its deployed URL path (under /docs/)."""
    rel = md_path.relative_to(DOCS).as_posix()
    rel = re.sub(r"\.(mdx?|md)$", "", rel)
    if rel.endswith("/index"):
        rel = rel[: -len("/index")]
    elif rel == "index":
        rel = ""
    parts = [NUM_PREFIX_RE.sub("", seg) for seg in rel.split("/") if seg]
    if not parts:
        return "/docs/"
    return "/docs/" + "/".join(parts) + "/"


def normalize_target(raw: str) -> tuple[str, str]:
    """Return (path_with_trailing_slash, fragment_with_leading_hash)."""
    u = urlparse(raw)
    path = u.path
    frag = ("#" + u.fragment) if u.fragment else ""
    if path.endswith(".md") or path.endswith(".mdx"):
        path = re.sub(r"\.(mdx?|md)$", "", path)
    if path and not path.endswith("/"):
        path += "/"
    return path, frag


def main() -> int:
    valid = {slug_for(p) for p in md_files()}

    broken: dict[Path, list[tuple[str, str]]] = defaultdict(list)
    total = 0

    for md in md_files():
        try:
            text = md.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARN: could not read {md}: {exc}", file=sys.stderr)
            continue
        if 'href="' not in text:
            continue
        source = slug_for(md)
        for href in HREF_ATTR_RE.findall(text):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "#")):
                continue
            path, _frag = normalize_target(href)
            if not path:
                continue
            # Resolve relative to the source page's URL.
            resolved = urlparse(urljoin("http://x" + source, path)).path
            if resolved in valid:
                continue
            # Tolerate links to static assets under /docs/ (img/, file downloads).
            # Anything ending in a non-slash extension is treated as a static
            # asset and not validated here.
            broken[md].append((href, resolved))
            total += 1

    if not broken:
        print(f"OK: {len(valid)} doc routes, no broken raw-HTML hrefs.")
        return 0

    print(
        f"FAIL: {total} broken raw-HTML href(s) across {len(broken)} file(s).",
        file=sys.stderr,
    )
    print(
        "Docusaurus's onBrokenLinks check does NOT cover raw HTML <a href>; "
        "fix the source markdown or update the link.",
        file=sys.stderr,
    )
    print(file=sys.stderr)
    for md, items in sorted(broken.items()):
        rel = md.relative_to(ROOT).as_posix()
        for href, resolved in items:
            print(f"{rel}:  href={href}", file=sys.stderr)
            print(f"      resolves to {resolved} (no such page)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
