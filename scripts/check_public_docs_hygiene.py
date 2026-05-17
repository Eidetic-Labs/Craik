"""Check public documentation for private paths, obvious secrets, and task-only text."""

from __future__ import annotations

import sys
from pathlib import Path

from craik.runtime.public_docs import public_docs_findings

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = [finding.summary for finding in public_docs_findings(ROOT)]

    if failures:
        print("Public documentation hygiene checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Public documentation hygiene checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
