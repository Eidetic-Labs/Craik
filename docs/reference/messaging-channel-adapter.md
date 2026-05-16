# Messaging Channel Adapter

The first messaging channel adapter is a fixture adapter for controlled gateway
ingress. It does not connect to Slack, Discord, email, SMS, or any external
service. It defines the normalized behavior future messaging adapters must keep:

- inbound message normalization;
- paired sender identity context;
- policy envelope linkage;
- redacted receipts;
- outbound response payload construction without delivery.

## Setup

No provider setup is required. Runtime callers use
`craik.runtime.messaging_channel` to build the default
`craik.channel_adapter_contract`, normalize a message, and produce a
`craik.capability_receipt`.

```python
from craik.runtime.messaging_channel import (
    default_messaging_channel_contract,
    inbound_message_receipt,
    normalize_inbound_message,
)

contract = default_messaging_channel_contract()
event = normalize_inbound_message(
    event_id="message_1",
    sender_id="external:alice",
    text="run the status check",
    identity_id="channel_identity_alice",
    policy_envelope_id="policy_gateway",
)
receipt = inbound_message_receipt(
    event=event,
    task_id="task_gateway",
    actor="adapter:messaging_fixture",
    policy_profile="strict",
    policy_envelope_id="policy_gateway",
)
```

## Inbound Normalization

Normalized inbound messages include:

- `event_id`;
- `channel` set to `messaging`;
- `received_at`;
- `sender.external_id`;
- optional paired `sender.identity_id`;
- optional `sender.policy_envelope_id`;
- message `text`;
- optional `thread_id`;
- adapter metadata.

The message text is part of the inbound event so downstream policy and task
creation can inspect it. Receipts redact message text.

## Receipts

`inbound_message_receipt` emits a `craik.capability_receipt` for
`channel.message.receive`. Receipt metadata preserves the policy envelope id,
event id, sender external id, paired identity id, channel, and redaction fields.

## Limitations

- No external messaging provider is contacted.
- No channel credentials are stored.
- No outbound response is delivered.
- Sender identity pairing and allowlists are enforced by later gateway layers.
- Policy envelopes and capability grants remain required before privileged
  action can happen.
