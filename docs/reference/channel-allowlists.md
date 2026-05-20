# Channel allowlists

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The deny-by-default filter that decides which normalized inbound
channel events continue past gateway ingress.

</div>

<div className="craik-keypoint">

**Deny by default.**

A channel event is allowed only when it matches an enabled rule for
the configured channel. Denied events produce explicit decision
reasons that can be recorded in redacted capability receipts.

</div>

## Rule selectors

Rules can match:

<div className="craik-grid">

<div><h4>Channel kind</h4></div>
<div><h4>Provider / fixture service name</h4></div>
<div><h4>External sender ids</h4></div>
<div><h4>Workspace ids</h4></div>
<div><h4>Thread ids</h4></div>
<div><h4>String metadata keys</h4></div>

</div>

<div className="craik-keypoint">

**At least one selector required.**

Broad, selector-free allow rules are rejected.

</div>

## Decisions

The evaluator returns an inspectable decision with:

<div className="craik-grid">

<div><h4>Allowed or denied status</h4></div>
<div><h4>Reason</h4></div>
<div><h4>Matched rule id</h4><p>When allowed.</p></div>
<div><h4>Event id</h4></div>
<div><h4>Channel</h4></div>
<div><h4>Sender external id</h4></div>

</div>

Events from the wrong channel are denied before rule matching. Events
with no matching enabled rule are denied with `no enabled allowlist
rule matched`.

## Denial receipts

Denied inbound events can emit a `craik.capability_receipt` with the
`channel.ingress.denied` capability. Receipt metadata preserves the
allowlist id, event id, channel, sender external id, policy envelope
id, and redaction fields — without storing message text.

## Boundary

<div className="craik-keypoint">

**Filter only, not authorization.**

Channel allowlists do not pair identities, grant tool authority, or
bypass policy envelopes. They only decide whether a normalized
external event can continue to later gateway stages.

</div>

## What's next

<div className="craik-next">

<a href="channel-policy-envelopes/">
<strong>Reference</strong>
<span>Channel policy envelopes</span>
<small>The scoped policy selected after pairing and allowlist checks pass.</small>
</a>

<a href="channel-identity-pairing/">
<strong>Reference</strong>
<span>Channel identity pairing</span>
<small>The other half of the pre-policy gate.</small>
</a>

<a href="gateway-receipts/">
<strong>Reference</strong>
<span>Gateway receipts</span>
<small>How denial decisions persist.</small>
</a>

</div>
