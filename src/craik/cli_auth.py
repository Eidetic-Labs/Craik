"""Authentication profile CLI commands."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from pydantic import ValidationError

from craik.cli import auth_app
from craik.runtime.auth import (
    AuthProfile,
    AuthProfileNotFoundError,
    AuthProfileStore,
    CredentialKind,
    CredentialStatus,
)
from craik.runtime.auth.sources import (
    DEFAULT_CLAUDE_CREDENTIALS_PATH,
    EnvVarApiKeySource,
    LocalCLICredentialError,
    LocalCLICredentialSource,
)
from craik.runtime.providers.provider_transport import ProviderFamily


@auth_app.command("list")
def auth_list() -> None:
    """List configured auth profiles."""
    store = AuthProfileStore.from_env()
    payload = [_profile_payload(profile) for profile in store.list()]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@auth_app.command("add")
def auth_add(
    profile_id: str,
    kind: Annotated[
        str,
        typer.Option("--kind", help="Credential kind for this profile."),
    ],
    env_var: Annotated[
        str | None,
        typer.Option("--env-var", help="Environment variable containing an API key."),
    ] = None,
    source: Annotated[
        str | None,
        typer.Option("--source", help="Optional source hint for future credential kinds."),
    ] = None,
    credentials_path: Annotated[
        Path | None,
        typer.Option("--credentials-path", help="Local CLI credentials file path."),
    ] = None,
    refresh_endpoint: Annotated[
        str | None,
        typer.Option("--refresh-endpoint", help="OAuth refresh endpoint for local CLI tokens."),
    ] = None,
    client_id: Annotated[
        str | None,
        typer.Option("--client-id", help="OAuth client id for refresh requests."),
    ] = None,
) -> None:
    """Add or replace an auth profile."""
    try:
        credential_kind = CredentialKind(kind)
    except ValueError:
        allowed = ", ".join(item.value for item in CredentialKind)
        message = f"unsupported credential kind; expected one of: {allowed}"
        raise typer.BadParameter(message) from None

    metadata: dict[str, Any] = {}
    if env_var is not None:
        metadata["env_var"] = env_var
    if source is not None:
        metadata["source"] = source
    if credentials_path is not None:
        metadata["credentials_path"] = str(credentials_path)
    if refresh_endpoint is not None:
        metadata["refresh_endpoint"] = refresh_endpoint
    if client_id is not None:
        metadata["client_id"] = client_id
    if credential_kind is CredentialKind.API_KEY and not env_var:
        raise typer.BadParameter("--env-var is required for api-key profiles")
    if credential_kind is CredentialKind.OAUTH_TOKEN and source != "local-cli":
        raise typer.BadParameter("--source=local-cli is required for oauth-token profiles")

    family = profile_id.split(":", 1)[0]
    try:
        profile = AuthProfile(
            id=profile_id,
            kind=credential_kind,
            provider_family=cast(ProviderFamily, family),
            metadata=metadata,
            created_at=datetime.now(UTC),
        )
    except ValidationError as error:
        raise typer.BadParameter(str(error)) from None

    AuthProfileStore.from_env().put(profile)
    typer.echo(json.dumps(_profile_payload(profile), indent=2, sort_keys=True))


@auth_app.command("remove")
def auth_remove(profile_id: str) -> None:
    """Remove an auth profile."""
    AuthProfileStore.from_env().delete(profile_id)
    typer.echo(json.dumps({"removed": profile_id}, indent=2, sort_keys=True))


@auth_app.command("test")
def auth_test(profile_id: str) -> None:
    """Check whether an auth profile can resolve credential material."""
    store = AuthProfileStore.from_env()
    try:
        profile = store.get(profile_id)
    except AuthProfileNotFoundError as error:
        raise typer.BadParameter(str(error)) from None

    status = _test_profile_status(profile)
    store.mark_used(profile.id, status.status)
    payload = {
        "id": profile.id,
        "provider_family": profile.provider_family,
        "status": status.model_dump(mode="json"),
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@auth_app.command("status")
def auth_status() -> None:
    """Show auth profile health and last-use status."""
    store = AuthProfileStore.from_env()
    payload = [
        {
            "id": profile.id,
            "kind": profile.kind,
            "provider_family": profile.provider_family,
            "last_used_at": profile.last_used_at.isoformat()
            if profile.last_used_at is not None
            else None,
            "last_status": profile.last_status,
        }
        for profile in store.list()
    ]
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def _source_status(profile: AuthProfile) -> CredentialStatus:
    if profile.kind is CredentialKind.API_KEY:
        env_var = profile.metadata.get("env_var")
        env_var = env_var if isinstance(env_var, str) else ""
        return EnvVarApiKeySource(env_var).status()
    if profile.kind is CredentialKind.OAUTH_TOKEN and profile.metadata.get("source") == "local-cli":
        return _local_cli_source(profile).status()
    return CredentialStatus(
        status="unknown",
        detail=f"{profile.kind.value} credential tests are not implemented yet",
    )


def _test_profile_status(profile: AuthProfile) -> CredentialStatus:
    if profile.kind is CredentialKind.OAUTH_TOKEN and profile.metadata.get("source") == "local-cli":
        source = _local_cli_source(profile)
        try:
            source.headers_for(profile.provider_family)
        except LocalCLICredentialError as exc:
            return CredentialStatus(status="rejected", detail=str(exc))
        return source.status()
    return _source_status(profile)


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


def _profile_payload(profile: AuthProfile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "kind": profile.kind,
        "provider_family": profile.provider_family,
        "metadata": _masked_metadata(profile.metadata),
        "created_at": profile.created_at.isoformat(),
        "last_used_at": profile.last_used_at.isoformat()
        if profile.last_used_at is not None
        else None,
        "last_status": profile.last_status,
    }


def _masked_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    masked: dict[str, Any] = {}
    for key, value in metadata.items():
        key_lower = key.lower()
        if any(token in key_lower for token in ("token", "secret", "password")):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked
