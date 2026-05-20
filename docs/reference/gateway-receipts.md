# Gateway receipts

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The redacted `craik.capability_receipt` records always-on service
actions produce — what context they preserve, how they redact, and the
status values they use.

</div>

<div className="craik-keypoint">

**Audit trail, not authority.**

Gateway receipts preserve a trail for decisions already made by
gateway policy, identity, allowlist, and scheduler boundaries.

</div>

## Action coverage

`craik.runtime.gateway_receipts` covers:

<div className="craik-grid">

<div><h4>Inbound event handling</h4></div>
<div><h4>Dispatch decisions</h4></div>
<div><h4>Policy checks</h4></div>
<div><h4>Denials</h4></div>
<div><h4>Scheduled automation actions</h4></div>

</div>

## Context links

Gateway receipt metadata preserves stable links where available:

<div className="craik-grid">

<div><h4>Channel</h4></div>
<div><h4>Event id</h4></div>
<div><h4>Task id</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Channel identity id</h4></div>
<div><h4>Paired subject</h4></div>
<div><h4>Schedule id</h4></div>
<div><h4>Automation id</h4></div>
<div><h4>Related receipt ids</h4></div>

</div>

## Redaction

<div className="craik-keypoint">

**Always redacted.**

Gateway receipts always set <code>redacted = true</code>. Sensitive
metadata keys are removed before receipt construction.

</div>

**Removed keys:** `payload` · `text` · `body` · `signature` · `secret`.

The receipt records these names in `redacted_fields` so operators can
see that payload material was intentionally omitted.

## Status

<div className="craik-fields">

<div>
<dt>Status</dt>
<dt><span className="craik-fields__type">Use for</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>passed</code></dt>
<dt><span className="craik-fields__type">success</span></dt>
<dd>Successful gateway actions.</dd>
</div>

<div>
<dt><code>denied</code></dt>
<dt><span className="craik-fields__type">block</span></dt>
<dd>Denial reason preserved in receipt.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="channel-policy-envelopes/">
<strong>Reference</strong>
<span>Channel policy envelopes</span>
<small>How channel policy produces denial reasons.</small>
</a>

<a href="receipt-viewer/">
<strong>Reference</strong>
<span>Receipt viewer</span>
<small>The operator surface that displays gateway receipts.</small>
</a>

<a href="../guides/gateway-troubleshooting/">
<strong>Guide</strong>
<span>Gateway troubleshooting</span>
<small>Diagnose what a receipt records.</small>
</a>

</div>
