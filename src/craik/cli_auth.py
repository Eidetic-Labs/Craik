"""Authentication profile CLI commands."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Annotated, Any, cast

import typer
from pydantic import ValidationError

from craik.cli import app, auth_app
from craik.runtime.auth import (
    AuthProfile,
    AuthProfileNotFoundError,
    AuthProfileStore,
    CredentialKind,
    CredentialStatus,
)
from craik.runtime.auth.operator import (
    OIDCAuthenticator,
    OIDCConfig,
    OperatorSessionNotFoundError,
    OperatorSessionStore,
)
from craik.runtime.auth.sources import source_for_auth_profile
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
        str | None,
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


@auth_app.command("approve")
def auth_approve(
    profile_id: str,
    run_id: Annotated[
        str,
        typer.Option("--run", help="Run id requesting first credential use."),
    ],
    approved_by: Annotated[
        str,
        typer.Option("--approved-by", help="Operator or approver recording approval."),
    ] = "operator:local",
) -> None:
    """Approve first live use of an auth profile for a run."""
    try:
        profile = AuthProfileStore.from_env().approve(
            profile_id,
            run_id=run_id,
            approved_by=approved_by,
        )
    except AuthProfileNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    typer.echo(json.dumps(_profile_payload(profile), indent=2, sort_keys=True))


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


@app.command("login")
def login(
    issuer: Annotated[
        str | None,
        typer.Option("--issuer", help="OIDC issuer URL. Defaults to CRAIK_OIDC_ISSUER."),
    ] = None,
    client_id: Annotated[
        str,
        typer.Option("--client-id", help="OIDC client id. Defaults to CRAIK_OIDC_CLIENT_ID."),
    ] = "",
    audience: Annotated[
        str | None,
        typer.Option("--audience", help="Optional OIDC audience value."),
    ] = None,
    max_wait_seconds: Annotated[
        int,
        typer.Option("--max-wait-seconds", help="Maximum device-code polling duration."),
    ] = 600,
) -> None:
    """Authenticate the local operator with OIDC device-code flow."""
    resolved_issuer = issuer or os.environ.get("CRAIK_OIDC_ISSUER")
    if not resolved_issuer:
        raise typer.BadParameter("--issuer or CRAIK_OIDC_ISSUER is required")
    resolved_client_id = client_id or os.environ.get("CRAIK_OIDC_CLIENT_ID", "craik-cli")
    authenticator = OIDCAuthenticator(
        OIDCConfig(
            issuer=resolved_issuer.rstrip("/"),
            client_id=resolved_client_id,
            audience=audience,
        )
    )
    authorization = authenticator.device_authorization()
    user_code = authorization.get("user_code")
    verification_uri = authorization.get("verification_uri") or authorization.get(
        "verification_uri_complete"
    )
    typer.echo(
        json.dumps(
            {
                "status": "authorization_pending",
                "verification_uri": verification_uri,
                "user_code": user_code,
            },
            indent=2,
            sort_keys=True,
        )
    )
    session, refresh_token = authenticator.session_and_refresh_from_token_response(
        authenticator.poll_device_token_response(
            str(authorization["device_code"]),
            interval_seconds=int(authorization.get("interval", 5) or 5),
            max_wait_seconds=max_wait_seconds,
        )
    )
    OperatorSessionStore.from_env().put(session, refresh_token=refresh_token)
    typer.echo(json.dumps(_operator_session_payload(session), indent=2, sort_keys=True))


@app.command("logout")
def logout(
    issuer: Annotated[
        str | None,
        typer.Option("--issuer", help="OIDC issuer URL for best-effort revocation."),
    ] = None,
    client_id: Annotated[
        str,
        typer.Option("--client-id", help="OIDC client id for best-effort revocation."),
    ] = "",
) -> None:
    """Clear the active operator session."""
    authenticator = None
    resolved_issuer = issuer or os.environ.get("CRAIK_OIDC_ISSUER")
    if resolved_issuer:
        authenticator = OIDCAuthenticator(
            OIDCConfig(
                issuer=resolved_issuer.rstrip("/"),
                client_id=client_id or os.environ.get("CRAIK_OIDC_CLIENT_ID", "craik-cli"),
            )
        )
    revoked = OperatorSessionStore.from_env().delete(authenticator=authenticator)
    typer.echo(json.dumps({"logged_out": True, "revoked": revoked}, indent=2, sort_keys=True))


@app.command("whoami")
def whoami() -> None:
    """Print the active operator identity."""
    try:
        session = OperatorSessionStore.from_env().get()
    except OperatorSessionNotFoundError as error:
        raise typer.BadParameter(str(error)) from None
    typer.echo(json.dumps(_operator_session_payload(session), indent=2, sort_keys=True))


def _source_status(profile: AuthProfile) -> CredentialStatus:
    try:
        return source_for_auth_profile(profile).status()
    except ValueError as exc:
        return CredentialStatus(status="unknown", detail=str(exc))


def _test_profile_status(profile: AuthProfile) -> CredentialStatus:
    try:
        source = source_for_auth_profile(profile)
        source.headers_for(profile.provider_family)
    except (RuntimeError, ValueError) as exc:
        return CredentialStatus(status="rejected", detail=str(exc))
    return source.status()


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


def _operator_session_payload(session: Any) -> dict[str, Any]:
    return {
        "subject": session.subject,
        "email": session.email,
        "display_name": session.display_name,
        "groups": session.groups,
        "issuer": session.issuer,
        "id_token_jti": session.id_token_jti,
        "expires_at": session.expires_at.isoformat(),
        "refresh_token_ref": session.refresh_token_ref,
    }
