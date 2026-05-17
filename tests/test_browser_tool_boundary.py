from craik.contracts.models import SandboxBackend, SandboxBackendCapability
from craik.runtime.sandbox.browser_tool_boundary import (
    BrowserToolRequest,
    browser_tool_decision,
)


def _backend(**overrides: object) -> SandboxBackend:
    payload = {
        "id": "sandbox_backend_browser_fixture",
        "name": "Fixture Browser Tool Backend",
        "kind": "browser_tool",
        "isolation_mode": "browser",
        "capabilities": [
            SandboxBackendCapability(
                name="browser.open",
                operations=["navigate", "inspect"],
                description="Open and inspect browser targets under policy.",
            )
        ],
        "docs": ["docs/reference/browser-tool-boundary.md"],
        "created_at": "2026-05-16T20:35:00Z",
    }
    payload.update(overrides)
    return SandboxBackend.model_validate(payload)


def _request(**overrides: object) -> BrowserToolRequest:
    payload = {
        "id": "browser_tool_request_fixture",
        "backend_id": "sandbox_backend_browser_fixture",
        "tool_name": "browser.open",
        "capability": "browser.open",
        "action_ref": "open_fixture_page",
        "policy_envelope_id": "policy_browser_tool_fixture",
        "capability_grant_id": "grant_browser_tool_fixture",
        "receipt_id": "receipt_browser_tool_fixture",
        "result_metadata": {"status_code": 200},
    }
    payload.update(overrides)
    return BrowserToolRequest.model_validate(payload)


def test_browser_tool_decision_allows_policy_bound_tool_action() -> None:
    decision = browser_tool_decision(backend=_backend(), request=_request())

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == (
        "browser/tool request is policy-, grant-, receipt-, and redaction-bound"
    )
    assert decision.redacted_result_metadata == {"status_code": 200}
    assert decision.required_controls == [
        "policy_envelope",
        "capability_grant",
        "receipt",
        "redaction",
    ]


def test_browser_tool_decision_denies_wrong_backend() -> None:
    decision = browser_tool_decision(
        backend=_backend(kind="local_process", isolation_mode="process"),
        request=_request(),
    )

    assert decision.allowed is False
    assert decision.reason == (
        "browser/tool requests require a browser_tool backend with browser isolation"
    )


def test_browser_tool_decision_denies_missing_capability() -> None:
    decision = browser_tool_decision(
        backend=_backend(
            capabilities=[
                SandboxBackendCapability(
                    name="file.read",
                    operations=["read"],
                    description="Read files.",
                )
            ]
        ),
        request=_request(),
    )

    assert decision.allowed is False
    assert decision.reason == "backend does not declare browser.open support"


def test_browser_tool_decision_denies_missing_policy_grant_or_receipt() -> None:
    assert (
        browser_tool_decision(
            backend=_backend(),
            request=_request(policy_envelope_id=None),
        ).reason
        == "browser/tool execution requires a policy envelope"
    )
    assert (
        browser_tool_decision(
            backend=_backend(),
            request=_request(capability_grant_id=None),
        ).reason
        == "browser/tool execution requires a capability grant"
    )
    assert (
        browser_tool_decision(
            backend=_backend(),
            request=_request(receipt_id=None),
        ).reason
        == "browser/tool execution requires a receipt"
    )


def test_browser_tool_decision_redacts_tool_results_on_allowed_and_denied_paths() -> None:
    metadata = {
        "html": "<input value='secret'>",
        "text": "secret text",
        "cookies": {"session": "secret"},
        "api_token": "secret",
        "status_code": 200,
    }

    allowed = browser_tool_decision(
        backend=_backend(),
        request=_request(result_metadata=metadata),
    )
    denied = browser_tool_decision(
        backend=_backend(),
        request=_request(policy_envelope_id=None, result_metadata=metadata),
    )

    assert allowed.redacted_result_metadata == {"status_code": 200}
    assert denied.redacted_result_metadata == {"status_code": 200}
