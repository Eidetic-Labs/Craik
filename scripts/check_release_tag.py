#!/usr/bin/env python3
"""Ensure release publication runs from the expected immutable tag."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["version"])


def _package_version() -> str:
    init_file = (ROOT / "src" / "craik" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', init_file, re.MULTILINE)
    if not match:
        raise ValueError("src/craik/__init__.py does not define __version__")
    return match.group(1)


def _changelog_version() -> str:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## (\d+\.\d+\.\d+)", changelog, re.MULTILINE)
    if not match:
        raise ValueError("CHANGELOG.md does not contain a versioned release heading")
    return match.group(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Git tag ref name, for example v0.1.0")
    parser.add_argument(
        "--expected-version",
        required=True,
        help="Expected semantic version without the leading v, for example 0.1.0",
    )
    args = parser.parse_args(argv)

    expected_tag = f"v{args.expected_version}"
    versions = {
        "pyproject": _project_version(),
        "package": _package_version(),
        "changelog": _changelog_version(),
    }

    if args.tag != expected_tag:
        print(f"Release tag mismatch: tag={args.tag}, expected={expected_tag}")
        return 1

    mismatched = {
        name: version
        for name, version in versions.items()
        if version != args.expected_version
    }
    if mismatched:
        details = ", ".join(f"{name}={version}" for name, version in sorted(mismatched.items()))
        print(f"Release version mismatch: expected={args.expected_version}, {details}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
