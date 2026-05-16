import json

from typer.testing import CliRunner

from craik.cli import app

runner = CliRunner()


def test_provider_list_prints_redacted_registry() -> None:
    result = runner.invoke(app, ["provider", "list"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload[0]["id"] == "provider_fixture_local"
    assert payload[0]["secret_ref_names"] == ["CRAIK_PROVIDER_FIXTURE_TOKEN"]
    assert "api_key" not in payload[0]["metadata"]


def test_provider_show_prints_one_provider() -> None:
    result = runner.invoke(app, ["provider", "show", "provider_fixture_local"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["id"] == "provider_fixture_local"
    assert payload["trust_boundary"] == "local"


def test_provider_select_prints_policy_and_receipt_context() -> None:
    result = runner.invoke(
        app,
        [
            "provider",
            "select",
            "provider_fixture_local",
            "--mode",
            "runner",
            "--policy-envelope-id",
            "policy_provider",
            "--receipt-id",
            "receipt_provider_select",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["provider_id"] == "provider_fixture_local"
    assert payload["mode"] == "runner"
    assert payload["policy_envelope_id"] == "policy_provider"
    assert payload["receipt_ids"] == ["receipt_provider_select"]
    assert payload["redacted"] is True


def test_provider_select_rejects_unsupported_mode() -> None:
    result = runner.invoke(
        app,
        ["provider", "select", "provider_fixture_local", "--mode", "embedding"],
    )

    assert result.exit_code != 0
    assert "does not support mode" in result.output
