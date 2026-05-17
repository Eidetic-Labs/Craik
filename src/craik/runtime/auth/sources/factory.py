"""Factory helpers for auth profile credential sources."""

from __future__ import annotations

from pathlib import Path

from craik.runtime.auth.profile import AuthProfile, CredentialKind, CredentialSource
from craik.runtime.auth.sources.api_key import EnvVarApiKeySource
from craik.runtime.auth.sources.cli_bridge import CLIBridgeCredentialSource
from craik.runtime.auth.sources.local_cli_oauth import (
    DEFAULT_CLAUDE_CREDENTIALS_PATH,
    LocalCLICredentialSource,
)
from craik.runtime.auth.sources.secret_ref import (
    EnvVarSecretManager,
    FileSecretManager,
    SecretRefCredentialSource,
)


class AuthProfileSourceError(ValueError):
    """Raised when an auth profile cannot be mapped to a credential source."""


def source_for_auth_profile(profile: AuthProfile) -> CredentialSource:
    """Build the credential source configured by an auth profile."""
    if profile.kind is CredentialKind.API_KEY:
        env_var = profile.metadata.get("env_var")
        env_var = env_var if isinstance(env_var, str) else ""
        return EnvVarApiKeySource(env_var)
    if profile.kind is CredentialKind.OAUTH_TOKEN and profile.metadata.get("source") == "local-cli":
        return _local_cli_source(profile)
    if profile.kind is CredentialKind.SECRET_REF:
        return _secret_ref_source(profile)
    if profile.kind is CredentialKind.CLI_BRIDGE:
        return _cli_bridge_source(profile)
    raise AuthProfileSourceError(f"unsupported auth profile kind/source: {profile.kind.value}")


def _local_cli_source(profile: AuthProfile) -> LocalCLICredentialSource:
    credentials_path = profile.metadata.get("credentials_path")
    refresh_endpoint = profile.metadata.get("refresh_endpoint")
    client_id = profile.metadata.get("client_id")
    return LocalCLICredentialSource(
        credentials_path=Path(credentials_path)
        if isinstance(credentials_path, str)
        else DEFAULT_CLAUDE_CREDENTIALS_PATH,
        refresh_endpoint=refresh_endpoint if isinstance(refresh_endpoint, str) else None,
        client_id=client_id if isinstance(client_id, str) else None,
    )


def _secret_ref_source(profile: AuthProfile) -> SecretRefCredentialSource:
    ref = profile.metadata.get("ref")
    manager = profile.metadata.get("manager", "env")
    if not isinstance(ref, str):
        raise AuthProfileSourceError("secret-ref auth profile requires metadata.ref")
    secret_manager = FileSecretManager() if manager == "file" else EnvVarSecretManager()
    return SecretRefCredentialSource(ref=ref, manager=secret_manager)


def _cli_bridge_source(profile: AuthProfile) -> CLIBridgeCredentialSource:
    command = profile.metadata.get("command")
    extractor = profile.metadata.get("token_extractor", "stdout_json")
    key_path = profile.metadata.get("key_path", ["token"])
    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        raise AuthProfileSourceError("cli-bridge auth profile requires metadata.command")
    if extractor not in {"stdout_json", "stdout_line", "credentials_file"}:
        raise AuthProfileSourceError("cli-bridge auth profile has unsupported token_extractor")
    path = profile.metadata.get("credentials_file_path")
    return CLIBridgeCredentialSource(
        command=tuple(command),
        token_extractor=extractor,
        key_path=tuple(item for item in key_path if isinstance(item, str))
        if isinstance(key_path, list)
        else ("token",),
        credentials_file_path=Path(path) if isinstance(path, str) else None,
    )
