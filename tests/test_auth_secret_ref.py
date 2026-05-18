from pathlib import Path

import pytest

from craik.runtime.auth.sources import (
    EnvVarSecretManager,
    FileSecretManager,
    SecretManager,
    SecretRefCredentialSource,
)


def test_secret_ref_source_resolves_file_secret(tmp_path: Path) -> None:
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("file-secret\n", encoding="utf-8")
    source = SecretRefCredentialSource(
        ref=str(secret_file),
        manager=FileSecretManager(),
    )

    headers = source.headers_for("anthropic")

    assert headers == {
        "anthropic-version": "2023-06-01",
        "x-api-key": "file-secret",
    }
    assert source.status().status == "ok"
    assert "file-secret" not in str(source.status())


def test_secret_manager_protocol_default_raises_not_implemented() -> None:
    class IncompleteSecretManager(SecretManager):
        pass

    manager = IncompleteSecretManager()

    with pytest.raises(NotImplementedError):
        manager.resolve("secret-ref")


def test_secret_ref_source_resolves_env_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRAIK_PROVIDER_SECRET", "env-secret")
    source = SecretRefCredentialSource(
        ref="CRAIK_PROVIDER_SECRET",
        manager=EnvVarSecretManager(),
    )

    headers = source.headers_for("chat_completions")

    assert headers == {"Authorization": "Bearer env-secret"}
    assert "env-secret" not in str(source.status())


def test_secret_ref_source_status_does_not_leak_missing_reference(tmp_path: Path) -> None:
    missing = tmp_path / "missing-secret.txt"
    source = SecretRefCredentialSource(
        ref=str(missing),
        manager=FileSecretManager(),
    )

    status = source.status()

    assert status.status == "rejected"
    assert status.detail == "secret reference could not be resolved"
    assert str(missing) not in str(status)
