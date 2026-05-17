#!/usr/bin/env python3
"""Ensure pyproject version matches the latest CHANGELOG release heading."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## (\d+\.\d+\.\d+)", changelog, re.MULTILINE)
    if not match:
        print("No versioned heading found in CHANGELOG.md")
        return 1
    changelog_version = match.group(1)
    if project_version != changelog_version:
        print(
            f"Version mismatch: pyproject={project_version}, "
            f"CHANGELOG top={changelog_version}"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
