import pytest
from pydantic import ValidationError

from craik.runtime.mcp_client import (
    MCPClientConfig,
    MCPClientRoute,
    mcp_client_compatibility,
)


def _client(**overrides: object) -> MCPClientConfig:
    payload = {
        "id": "mcp_client_fixture",
        "name": "Fixture MCP Client",
        "transport": "http",
        "server_ref": "mcp_server_fixture",
        "endpoint_ref": "MCP_FIXTURE_ENDPOINT",
        "secret_ref_names": ["MCP_FIXTURE_TOKEN"],
        "policy_envelope_id": "policy_mcp_fixture",
        "docs": ["docs/reference/mcp-client.md"],
    }
    payload.update(overrides)
    return MCPClientConfig.model_validate(payload)


def _route(**overrides: object) -> MCPClientRoute:
    payload = {
        "id": "mcp_route_provider_fixture",
        "client_id": "mcp_client_fixture",
        "kind": "provider",
        "target_ref": "provider_fixture_local",
        "capability": "model.chat",
        "audit_label": "provider route fixture",
    }
    payload.update(overrides)
    return MCPClientRoute.model_validate(payload)


def test_mcp_client_config_is_non_secret_and_policy_bound() -> None:
    client = _client()

    assert client.secret_ref_names == ["MCP_FIXTURE_TOKEN"]
    assert client.grant_required is True
    assert client.receipt_required is True
    assert client.redaction_required is True


def test_mcp_client_config_validates_transport_references() -> None:
    with pytest.raises(ValidationError, match="http MCP clients require endpoint_ref"):
        _client(endpoint_ref=None)

    stdio = _client(
        transport="stdio",
        endpoint_ref=None,
        command_ref="MCP_FIXTURE_COMMAND",
    )

    assert stdio.command_ref == "MCP_FIXTURE_COMMAND"

    with pytest.raises(ValidationError, match="stdio MCP clients require command_ref"):
        _client(transport="stdio", endpoint_ref=None)


def test_mcp_client_config_rejects_secret_like_inline_values() -> None:
    with pytest.raises(ValidationError, match="endpoint_ref must not contain credentials"):
        _client(endpoint_ref="https://user:pass@example.invalid/mcp")

    with pytest.raises(ValidationError, match="server_ref must not contain secret-like"):
        _client(server_ref="mcp_server_fixture?token=raw")

    with pytest.raises(ValidationError, match="metadata must not contain secret-like"):
        _client(metadata={"api_key": "not allowed"})


def test_mcp_client_compatibility_allows_provider_and_tool_routes() -> None:
    client = _client()
    provider_route = _route()
    tool_route = _route(
        id="mcp_route_tool_fixture",
        kind="tool",
        target_ref="tool_fixture_browser",
        capability="browser.open",
    )

    compatibility = mcp_client_compatibility(client, [provider_route, tool_route])

    assert compatibility.compatible is True
    assert compatibility.status == "compatible"
    assert compatibility.route_ids == ["mcp_route_provider_fixture", "mcp_route_tool_fixture"]
    assert compatibility.required_controls == [
        "redaction",
        "capability_grants",
        "receipts",
        "external_secret_refs",
        "policy_envelope",
    ]


def test_mcp_client_compatibility_blocks_unroutable_or_unaudited_routes() -> None:
    compatibility = mcp_client_compatibility(
        _client(),
        [
            _route(client_id="other_client"),
            _route(id="mcp_route_ungranted", grant_required=False),
            _route(id="mcp_route_unreceipted", receipt_required=False),
        ],
    )

    assert compatibility.compatible is False
    assert compatibility.status == "blocked"
    assert compatibility.reasons == [
        "route mcp_route_provider_fixture belongs to other_client, not mcp_client_fixture",
        "route mcp_route_ungranted does not require a capability grant",
        "route mcp_route_unreceipted does not require receipts",
    ]


def test_mcp_client_compatibility_blocks_missing_routes() -> None:
    compatibility = mcp_client_compatibility(_client(), [])

    assert compatibility.compatible is False
    assert compatibility.status == "blocked"
    assert compatibility.reasons == [
        "MCP clients require at least one provider or tool route"
    ]
