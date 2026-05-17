import importlib
from datetime import UTC, datetime

from craik.contracts.models import ChannelAllowlist
from craik.runtime.channels.allowlist import evaluate_channel_allowlist
from craik.runtime.channels.identity import pair_channel_identity, unpaired_channel_identity
from craik.runtime.channels.messaging import normalize_inbound_message
from craik.runtime.channels.policy import (
    channel_capability_allowed,
    channel_policy_denial_receipt,
    select_channel_policy,
)

NOW = datetime(2026, 5, 16, 19, 5, tzinfo=UTC)


def test_channel_runtime_package_preserves_legacy_imports() -> None:
    legacy_policy = importlib.import_module("craik.runtime.channel_policy")
    legacy_messaging = importlib.import_module("craik.runtime.messaging_channel")
    legacy_allowlist = importlib.import_module("craik.runtime.channel_allowlist")
    legacy_identity = importlib.import_module("craik.runtime.channel_identity")

    assert legacy_policy.select_channel_policy is select_channel_policy
    assert legacy_messaging.normalize_inbound_message is normalize_inbound_message
    assert legacy_allowlist.evaluate_channel_allowlist is evaluate_channel_allowlist
    assert legacy_identity.pair_channel_identity is pair_channel_identity


def _allowlist() -> ChannelAllowlist:
    return ChannelAllowlist.model_validate(
        {
            "schema": "craik.channel_allowlist",
            "version": "0.1.0",
            "id": "allowlist_messaging_ops",
            "channel": "messaging",
            "default_action": "deny",
            "rules": [
                {
                    "id": "ops_alice",
                    "description": "Allow Alice in ops workspace.",
                    "channel": "messaging",
                    "sender_external_ids": ["external:alice"],
                    "workspace_ids": ["ops"],
                    "enabled": True,
                }
            ],
            "audit_required": True,
            "denial_capability": "channel.ingress.denied",
            "created_at": NOW,
            "updated_at": NOW,
        }
    )


def _paired_identity():
    return pair_channel_identity(
        unpaired_channel_identity(
            pairing_id="channel_identity_alice",
            channel="messaging",
            external_id="external:alice",
            created_at=NOW,
        ),
        subject="user:alice",
        policy_envelope_id="policy_gateway",
        paired_by="user:maintainer",
        audit_id="receipt_pair_alice",
        paired_at=NOW,
    )


def _allowed_event():
    event = normalize_inbound_message(
        event_id="message_1",
        sender_id="external:alice",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )
    return event, evaluate_channel_allowlist(_allowlist(), event)


def test_channel_policy_selection_requires_pairing_and_allowlist() -> None:
    event, decision = _allowed_event()

    selection = select_channel_policy(
        event=event,
        pairing=_paired_identity(),
        allowlist_decision=decision,
        policy_id="policy_channel_message_1",
        task_id="task_gateway",
    )

    assert selection.allowed is True
    assert selection.policy is not None
    assert selection.policy.actor == "user:alice"
    assert selection.policy.fail_open is False
    assert selection.policy.allowed_capabilities == [
        "channel.message.receive",
        "channel.message.respond",
        "receipt.write",
    ]
    assert "shell.execute" in selection.policy.denied_capabilities
    assert selection.policy.receipt_required is True
    assert selection.policy.redaction_required is True


def test_channel_policy_denies_unpaired_identity() -> None:
    event, decision = _allowed_event()
    unpaired = unpaired_channel_identity(
        pairing_id="channel_identity_alice",
        channel="messaging",
        external_id="external:alice",
        created_at=NOW,
    )

    selection = select_channel_policy(
        event=event,
        pairing=unpaired,
        allowlist_decision=decision,
        policy_id="policy_channel_message_1",
        task_id="task_gateway",
    )

    assert selection.allowed is False
    assert selection.policy is None
    assert selection.reason == "channel identity channel_identity_alice is not paired"


def test_channel_policy_denies_allowlist_rejection() -> None:
    event = normalize_inbound_message(
        event_id="message_2",
        sender_id="external:bob",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )
    decision = evaluate_channel_allowlist(_allowlist(), event)

    selection = select_channel_policy(
        event=event,
        pairing=_paired_identity(),
        allowlist_decision=decision,
        policy_id="policy_channel_message_2",
        task_id="task_gateway",
    )

    assert selection.allowed is False
    assert selection.policy is None
    assert selection.reason == "no enabled allowlist rule matched"


def test_channel_policy_keeps_channel_authority_narrower_than_local_operator() -> None:
    event, decision = _allowed_event()
    selection = select_channel_policy(
        event=event,
        pairing=_paired_identity(),
        allowlist_decision=decision,
        policy_id="policy_channel_message_1",
        task_id="task_gateway",
    )
    assert selection.policy is not None

    assert channel_capability_allowed(selection.policy, "channel.message.receive") is True
    assert channel_capability_allowed(selection.policy, "shell.execute") is False
    assert channel_capability_allowed(selection.policy, "repo.write") is False


def test_channel_policy_denial_receipt_redacts_payload() -> None:
    event, decision = _allowed_event()
    selection = select_channel_policy(
        event=event,
        pairing=_paired_identity(),
        allowlist_decision=decision,
        policy_id="policy_channel_message_1",
        task_id="task_gateway",
    )

    receipt = channel_policy_denial_receipt(
        event=event,
        policy=selection.policy,
        capability="shell.execute",
        reason="shell.execute is not available to channel ingress",
        task_id="task_gateway",
        actor="user:alice",
        policy_profile="strict",
        created_at=NOW,
    )

    assert receipt.result.status == "denied"
    assert receipt.capability == "shell.execute"
    assert receipt.result.metadata["policy_envelope_id"] == "policy_channel_message_1"
    assert receipt.result.metadata["requested_capability"] == "shell.execute"
    assert "text" not in receipt.result.metadata
