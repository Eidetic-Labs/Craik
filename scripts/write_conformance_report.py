"""Write a contract conformance report for CI artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from craik.contracts.models import SCHEMA_VERSION
from craik.contracts.registry import CONTRACT_REGISTRY, schema_names

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "v0_1" / "contracts.json"
REPORT_DIR = ROOT / "reports" / "conformance"


def main() -> int:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    validated: list[dict[str, str]] = []
    for name in schema_names():
        model = CONTRACT_REGISTRY[name]
        parsed = model.model_validate(fixtures[name])
        reparsed = model.model_validate_json(parsed.model_dump_json(by_alias=True))
        if reparsed != parsed:
            raise RuntimeError(f"{name} failed JSON round trip")
        validated.append({"schema": name, "version": SCHEMA_VERSION})

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "fixture_path": str(FIXTURE_PATH.relative_to(ROOT)),
        "validated_contracts": validated,
        "validated_count": len(validated),
    }
    (REPORT_DIR / "contracts.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPORT_DIR / "contracts.md").write_text(_markdown(payload), encoding="utf-8")
    print(f"Wrote {REPORT_DIR.relative_to(ROOT)}")
    return 0


def _markdown(payload: dict[str, object]) -> str:
    rows = [
        "# Contract Conformance Report",
        "",
        f"- Schema version: `{payload['schema_version']}`",
        f"- Fixture path: `{payload['fixture_path']}`",
        f"- Validated contracts: `{payload['validated_count']}`",
        "",
        "| Schema | Version |",
        "| --- | --- |",
    ]
    for item in payload["validated_contracts"]:
        assert isinstance(item, dict)
        rows.append(f"| `{item['schema']}` | `{item['version']}` |")
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
