# Channel policy envelopes

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How channel ingress uses normal `craik.policy_envelope` records but
selects a narrower envelope than local operator authority — and what
denial behavior looks like.

</div>

<div className="craik-keypoint">

**Narrower than local authority.**

`craik.runtime.channels.policy` binds a normalized inbound event to a
channel policy only when the sender is paired, the allowlist allows,
the policy is fail-closed, and receipts + redaction are required.

</div>

## Default channel authority

<div className="craik-decision">

<div>
<h4>Default channel policy allows</h4>
<ul>
<li><code>channel.message.receive</code></li>
<li><code>channel.message.respond</code></li>
<li><code>receipt.write</code></li>
</ul>
</div>

<div>
<h4>Channel policy denies (local-only capabilities)</h4>
<ul>
<li>Repository writes</li>
<li>Immutable path writes</li>
<li>Shell execution</li>
<li>Memory writes</li>
<li>GitHub writes</li>
<li>Gateway administration</li>
</ul>
</div>

</div>

## Denial handling

Unpaired identities and allowlist rejections do not produce a policy
envelope. Requested capabilities outside the channel policy can emit
redacted `craik.capability_receipt` records with status `denied`.

**Denial receipts preserve:**

<div className="craik-grid">

<div><h4>Policy envelope id</h4><p>When one was selected.</p></div>
<div><h4>Event id</h4></div>
<div><h4>Requested capability</h4></div>
<div><h4>Channel</h4></div>
<div><h4>Redaction fields</h4></div>

</div>

Message text is **not** stored in policy denial receipt metadata.

## Boundary

<div className="craik-keypoint">

**Ingress-scoped only.**

Channel policy envelopes do not expand local operator authority,
bypass allowlists, pair external identities, or grant tool access by
themselves.

</div>

## What's next

<div className="craik-next">

<a href="policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The base profiles channel envelopes specialize.</small>
</a>

<a href="channel-identity-pairing/">
<strong>Reference</strong>
<span>Channel identity pairing</span>
<small>The pre-policy gate.</small>
</a>

<a href="gateway-receipts/">
<strong>Reference</strong>
<span>Gateway receipts</span>
<small>How denials persist.</small>
</a>

</div>
