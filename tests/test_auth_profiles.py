from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.auth import AuthProfile, CredentialKind, CredentialStatus


def test_auth_profile_round_trips_through_json() -> None:
    profile = AuthProfile(
        id="anthropic:work",
        kind=CredentialKind.API_KEY,
        provider_family="anthropic",
        metadata={"env_var": "ANTHROPIC_API_KEY"},
        created_at=datetime(2026, 5, 17, tzinfo=UTC),
        last_status="ok",
    )

    restored = AuthProfile.model_validate_json(profile.model_dump_json())

    assert restored == profile
    assert restored.kind is CredentialKind.API_KEY
    assert restored.metadata["env_var"] == "ANTHROPIC_API_KEY"


def test_auth_profile_rejects_id_without_profile_name() -> None:
    with pytest.raises(ValidationError, match="<provider_family>:<name>"):
        AuthProfile(
            id="anthropic",
            kind=CredentialKind.API_KEY,
            provider_family="anthropic",
            created_at=datetime(2026, 5, 17, tzinfo=UTC),
        )


def test_auth_profile_rejects_mismatched_provider_family() -> None:
    with pytest.raises(ValidationError, match="provider family must match"):
        AuthProfile(
            id="openai:work",
            kind=CredentialKind.OAUTH_TOKEN,
            provider_family="anthropic",
            created_at=datetime(2026, 5, 17, tzinfo=UTC),
        )


def test_credential_status_defaults_to_unknown() -> None:
    status = CredentialStatus()

    assert status.status == "unknown"
    assert status.detail is None
    assert status.expires_at is None
