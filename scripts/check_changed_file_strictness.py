"""Enforce minimal changed-file discipline for CI-sensitive surfaces."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/main", help="Base ref for changed-file checks.")
    args = parser.parse_args()

    changed = _changed_files(args.base)
    failures = _strictness_failures(changed)
    if failures:
        print("Changed-file strictness checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Changed-file strictness checks passed.")
    return 0


def _changed_files(base: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def _strictness_failures(changed: set[str]) -> list[str]:
    failures: list[str] = []
    if _touches(changed, "src/craik/") and not _touches(changed, "tests/"):
        failures.append("src/craik changes require a tests/ change.")
    if _touches(changed, "src/craik/contracts/") and "tests/test_contracts.py" not in changed:
        failures.append("contract model changes require tests/test_contracts.py coverage.")
    if _touches(changed, "docs/") and ".github/workflows/docs.yml" in changed:
        pass
    if _touches(changed, ".github/workflows/") and not any(
        path.startswith("docs/") or path.startswith("scripts/") for path in changed
    ):
        failures.append("workflow-only changes require a docs/ or scripts/ rationale change.")
    return failures


def _touches(changed: set[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in changed)


if __name__ == "__main__":
    raise SystemExit(main())
