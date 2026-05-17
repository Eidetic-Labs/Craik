import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from craik.contracts.models import SCHEMA_VERSION
from craik.contracts.registry import CONTRACT_REGISTRY, schema_names

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text())


def test_all_registered_contracts_have_valid_fixtures(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    assert set(fixtures) == set(schema_names())

    for name, model in CONTRACT_REGISTRY.items():
        parsed = model.model_validate(fixtures[name])
        assert parsed.model_dump(mode="json", by_alias=True)["schema"] == name


def test_contract_fixtures_round_trip_json(fixtures: dict[str, dict[str, Any]]) -> None:
    for name, model in CONTRACT_REGISTRY.items():
        parsed = model.model_validate(fixtures[name])
        reparsed = model.model_validate_json(parsed.model_dump_json(by_alias=True))
        assert reparsed == parsed


def test_contract_fixtures_pin_schema_version(fixtures: dict[str, dict[str, Any]]) -> None:
    for payload in fixtures.values():
        assert payload["version"] == SCHEMA_VERSION


def test_runner_contract_models_keep_legacy_import_surface() -> None:
    from craik.contracts import models
    from craik.contracts.runner_models import RunnerMetadata

    assert models.RunnerMetadata is RunnerMetadata


@pytest.mark.parametrize("name", sorted(CONTRACT_REGISTRY))
def test_wrong_schema_name_is_rejected(
    fixtures: dict[str, dict[str, Any]],
    name: str,
) -> None:
    payload = dict(fixtures[name])
    payload["schema"] = "craik.wrong_schema"

    with pytest.raises(ValidationError):
        CONTRACT_REGISTRY[name].model_validate(payload)


@pytest.mark.parametrize("name", sorted(CONTRACT_REGISTRY))
def test_wrong_schema_version_is_rejected(
    fixtures: dict[str, dict[str, Any]],
    name: str,
) -> None:
    payload = dict(fixtures[name])
    payload["version"] = "9.9.9"

    with pytest.raises(ValidationError):
        CONTRACT_REGISTRY[name].model_validate(payload)


@pytest.mark.parametrize("name", sorted(CONTRACT_REGISTRY))
def test_extra_fields_are_rejected(
    fixtures: dict[str, dict[str, Any]],
    name: str,
) -> None:
    payload = dict(fixtures[name])
    payload["unexpected"] = "not allowed"

    with pytest.raises(ValidationError):
        CONTRACT_REGISTRY[name].model_validate(payload)
