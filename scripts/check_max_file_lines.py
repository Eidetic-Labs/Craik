#!/usr/bin/env python3
"""Fail if any tracked source file exceeds the maximum line budget."""

from __future__ import annotations

import sys
from pathlib import Path

MAX_LINES = 500
EXEMPT = {
    # Pure Pydantic schema modules may legitimately exceed the cap.
    "src/craik/contracts/models/memory.py",
    "src/craik/contracts/models/skills.py",
    "src/craik/contracts/models/review.py",
    # Existing implementation debt being split in follow-up Task 5 PRs.
    "src/craik/runtime/providers/provider_runtime.py",
    "src/craik/cli_project.py",
    "src/craik/runtime/memory/memory.py",
    "src/craik/cli_operations.py",
}


def main(paths: list[str]) -> int:
    failures: list[tuple[str, int]] = []
    for p in paths:
        if not p.endswith(".py"):
            continue
        if p in EXEMPT:
            continue
        n = sum(1 for _ in Path(p).open(encoding="utf-8"))
        if n > MAX_LINES:
            failures.append((p, n))
    if failures:
        print(f"Files exceeding {MAX_LINES} lines:")
        for path, n in failures:
            print(f"  {path}: {n} lines")
        print("Split the file or add a justified exemption in scripts/check_max_file_lines.py.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
