"""Check package version declarations stay in sync."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pyproject_version = _pyproject_version()
    package_version = _package_version()
    docs_version = _docs_package_version()

    versions = {
        "pyproject.toml": pyproject_version,
        "src/craik/__init__.py": package_version,
        "docs/package.json": docs_version,
    }
    mismatches = {
        path: version for path, version in versions.items() if version != pyproject_version
    }
    if mismatches:
        print("Version mismatch detected:", file=sys.stderr)
        for path, version in versions.items():
            print(f"- {path}: {version}", file=sys.stderr)
        return 1

    print(f"Version declarations are consistent: {pyproject_version}")
    return 0


def _pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    return str(data["project"]["version"])


def _package_version() -> str:
    content = (ROOT / "src/craik/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', content, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError("src/craik/__init__.py does not declare __version__")
    return match.group(1)


def _docs_package_version() -> str:
    data = json.loads((ROOT / "docs/package.json").read_text(encoding="utf-8"))
    return str(data["version"])


if __name__ == "__main__":
    raise SystemExit(main())
