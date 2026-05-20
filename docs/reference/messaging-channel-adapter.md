# Messaging channel adapter

<p className="craik-meta"><span>3 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The first messaging channel adapter — a fixture for controlled gateway
ingress. It does not connect to Slack, Discord, email, SMS, or any
external service. It defines the normalized behavior every future
messaging adapter must keep.

</div>

<div className="craik-keypoint">

**Fixture, not delivery.**

Inbound normalization · paired identity context · policy envelope
linkage · redacted receipts · outbound payload construction —
**without delivery**.

</div>

## Setup

No provider setup is required. Runtime callers use
`craik.runtime.channels.messaging` to build the default
`craik.channel_adapter_contract`, normalize a message, and produce a
`craik.capability_receipt`.

```python
from craik.runtime.channels.messaging import (
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

## Inbound normalization

Normalized inbound messages include:

<div className="craik-grid">

<div><h4><code>event_id</code></h4></div>
<div><h4><code>channel</code></h4><p>Set to <code>messaging</code>.</p></div>
<div><h4><code>received_at</code></h4></div>
<div><h4><code>sender.external_id</code></h4></div>
<div><h4>Paired <code>sender.identity_id</code></h4><p>Optional.</p></div>
<div><h4><code>sender.policy_envelope_id</code></h4><p>Optional.</p></div>
<div><h4>Message <code>text</code></h4></div>
<div><h4><code>thread_id</code></h4><p>Optional.</p></div>
<div><h4>Adapter metadata</h4></div>

</div>

The message text is part of the inbound event so downstream policy and
task creation can inspect it. **Receipts redact message text.**

## Receipts

`inbound_message_receipt` emits a `craik.capability_receipt` for
`channel.message.receive`. Receipt metadata preserves the policy
envelope id, event id, sender external id, paired identity id,
channel, and redaction fields.

## Limitations

<div className="craik-grid">

<div><h4>No external messaging provider contacted</h4></div>
<div><h4>No channel credentials stored</h4></div>
<div><h4>No outbound response delivered</h4></div>
<div><h4>Identity pairing &amp; allowlists</h4><p>Enforced by later gateway layers.</p></div>
<div><h4>Policy envelopes &amp; grants</h4><p>Required before privileged action.</p></div>

</div>

## What's next

<div className="craik-next">

<a href="../channel-identity-pairing/">
<strong>Reference</strong>
<span>Channel identity pairing</span>
<small>Paired, unpaired, and revoked sender authority states.</small>
</a>

<a href="../channel-allowlists/">
<strong>Reference</strong>
<span>Channel allowlists</span>
<small>Deny-by-default ingress filtering after normalization.</small>
</a>

<a href="../channel-adapter-contract/">
<strong>Reference</strong>
<span>Channel adapter contract</span>
<small>The shared contract.</small>
</a>

</div>
