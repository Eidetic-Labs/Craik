from pathlib import Path

import pytest

from craik.runtime.secrets import SecretNotFoundError, SecretRef, SecretResolver


def test_secret_resolver_prefers_environment_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRAIK_TEST_SECRET", "env-secret")

    value = SecretResolver().resolve(SecretRef(env_var="CRAIK_TEST_SECRET"))

    assert value == "env-secret"


def test_secret_resolver_reads_dotenv_when_environment_is_missing(tmp_path: Path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("CRAIK_TEST_SECRET='dotenv-secret'\n", encoding="utf-8")

    value = SecretResolver().resolve(
        SecretRef(env_var="CRAIK_TEST_SECRET", dotenv_path=dotenv)
    )

    assert value == "dotenv-secret"


def test_secret_resolver_missing_error_hides_reference_and_secret(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CRAIK_SENSITIVE_PURPOSE_API_KEY", raising=False)
    dotenv = tmp_path / ".env"
    dotenv.write_text("OTHER_SECRET=secret-value\n", encoding="utf-8")

    with pytest.raises(SecretNotFoundError) as exc_info:
        SecretResolver().resolve(
            SecretRef(env_var="CRAIK_SENSITIVE_PURPOSE_API_KEY", dotenv_path=dotenv)
        )

    message = str(exc_info.value)
    assert "CRAIK_SENSITIVE_PURPOSE_API_KEY" not in message
    assert "secret-value" not in message
    assert message == "secret reference could not be resolved"
