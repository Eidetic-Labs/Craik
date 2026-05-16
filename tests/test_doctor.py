import json

from typer.testing import CliRunner

from craik.cli import app
from craik.runtime.doctor import run_doctor
from craik.runtime.gateway import default_gateway_config
from craik.runtime.paths import ensure_craik_home, resolve_craik_paths
from craik.runtime.store import LocalStore

runner = CliRunner()


def test_doctor_reports_missing_home_without_creating_it(tmp_path) -> None:
    home = tmp_path / "missing-home"

    payload = run_doctor(resolve_craik_paths({"CRAIK_HOME": str(home)}), env={})

    assert payload["status"] == "fail"
    checks = {item["name"]: item for item in payload["checks"]}
    assert checks["local_home"]["status"] == "fail"
    assert checks["local_store"]["status"] == "fail"
    assert checks["memory_backend"]["status"] == "warning"
    assert not home.exists()


def test_doctor_reports_pass_with_setup_and_memory_config(tmp_path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    try:
        store.initialize()
        store.put_gateway_config(
            default_gateway_config(
                project_id="project_gateway",
                policy_envelope_id="policy_gateway",
            ).model_copy(update={"enabled": True})
        )
        payload = run_doctor(paths, env={"CRAIK_STIGMEM_URL": "http://127.0.0.1:18765"})
    finally:
        store.close()

    assert payload["status"] == "pass"
    checks = {item["name"]: item for item in payload["checks"]}
    assert checks["local_home"]["status"] == "pass"
    assert checks["local_store"]["status"] == "pass"
    assert checks["memory_backend"]["status"] == "pass"
    assert checks["gateway_config"]["status"] == "pass"
    assert checks["gateway_prerequisites"]["status"] == "pass"
    assert checks["policy"]["status"] == "pass"


def test_doctor_cli_outputs_json(tmp_path) -> None:
    home = tmp_path / "home"
    setup = runner.invoke(app, ["setup"], env={"CRAIK_HOME": str(home)})

    result = runner.invoke(app, ["doctor"], env={"CRAIK_HOME": str(home)})

    assert setup.exit_code == 0
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "warning"
    assert any(item["name"] == "memory_backend" for item in payload["checks"])
