import re

from craik.runtime.redaction import RedactionConfig, contains_unredacted_secret, redact


def test_redacts_bearer_header() -> None:
    result = redact("Authorization: Bearer redactionfixture123")

    assert result.value == "Authorization: Bearer [REDACTED]"
    assert result.redacted is True


def test_redacts_api_key_query_shape() -> None:
    result = redact("call service api_key=redactionfixture123")

    assert result.value == "call service api_key=[REDACTED]"
    assert result.redacted_paths == ("$",)


def test_redacts_auth_url_without_destroying_shape() -> None:
    result = redact("https://user:redactionfixture123@example.com/path")

    assert result.value == "https://[REDACTED]:[REDACTED]@example.com/path"


def test_redacts_secret_key_in_structured_payload() -> None:
    payload = {
        "result": {
            "metadata": {
                "api_token": "redaction-fixture-value",
                "status": "failed",
            }
        }
    }

    result = redact(payload)

    assert result.value["result"]["metadata"]["api_token"] == "[REDACTED]"
    assert result.value["result"]["metadata"]["status"] == "failed"
    assert result.redacted_paths == ("$.result.metadata.api_token",)


def test_preserves_already_redacted_values() -> None:
    result = redact({"api_token": "[REDACTED]"})

    assert result.value == {"api_token": "[REDACTED]"}
    assert result.redacted is False


def test_configurable_secret_patterns() -> None:
    config = RedactionConfig(patterns=(re.compile(r"custom-secret-[0-9]+"),))

    result = redact("value custom-secret-1234", config)

    assert result.value == "value [REDACTED]"


def test_detects_unredacted_secret_material() -> None:
    assert contains_unredacted_secret({"password": "redaction-fixture-value"})
    assert not contains_unredacted_secret({"password": "[REDACTED]"})


def test_context_budget_token_counts_are_not_secret_keys() -> None:
    assert not contains_unredacted_secret({"max_tokens": 24000, "estimated_tokens": 12})


def test_receipt_shape_redaction_regression() -> None:
    payload = {
        "schema": "craik.capability_receipt",
        "result": {
            "summary": "Authorization: Bearer redactionfixture123",
            "metadata": {"request_id": "req_123"},
        },
    }

    result = redact(payload)

    assert result.value["result"]["summary"] == "Authorization: Bearer [REDACTED]"
    assert result.value["result"]["metadata"]["request_id"] == "req_123"


def test_handoff_shape_redaction_regression() -> None:
    payload = {
        "schema": "craik.handoff",
        "commands_run": ["curl https://user:redactionfixture123@example.com/path"],
        "summary": "completed",
    }

    result = redact(payload)

    assert result.value["commands_run"] == [
        "curl https://[REDACTED]:[REDACTED]@example.com/path"
    ]
    assert result.value["summary"] == "completed"


def test_case_file_shape_redaction_regression() -> None:
    payload = {
        "schema": "craik.case_file",
        "repo_state": {"remote": "https://user:redactionfixture123@example.com/repo.git"},
        "docs": ["README.md"],
    }

    result = redact(payload)

    assert result.value["repo_state"]["remote"] == (
        "https://[REDACTED]:[REDACTED]@example.com/repo.git"
    )
    assert result.value["docs"] == ["README.md"]


def test_memory_proposal_shape_redaction_regression() -> None:
    payload = {
        "schema": "craik.memory_proposal",
        "fact": {
            "entity": "repo:demo",
            "relation": "craik:note",
            "value": "token=redactionfixture123",
        },
    }

    result = redact(payload)

    assert result.value["fact"]["value"] == "token=[REDACTED]"
