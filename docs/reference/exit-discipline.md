# Context requests and exit discipline

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

Two contracts that bound how agents stop: `craik.context_request` for
structured asks before continuing, and `craik.exit_discipline_check`
for what every agent exit must produce.

</div>

<div className="craik-keypoint">

**Blocked exits must explain why.**

Complete exits require every checklist field and no blockers. Blocked
exits must explain blocking reasons so the next agent can recover
without guessing.

</div>

## Contracts

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.context_request</code></dt>
<dt><span className="craik-fields__type">structured ask</span></dt>
<dd>Requester · kind · status · question · why the context is needed · fulfillment details when available. Can link to handoffs, recovery sessions, and unresolved unknowns.</dd>
</div>

<div>
<dt><code>craik.exit_discipline_check</code></dt>
<dt><span className="craik-fields__type">exit checklist</span></dt>
<dd>Validation · handoff · residual risk state · next steps · context request links · unresolved unknown links.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../guides/writing-handoffs/">
<strong>Guide</strong>
<span>Writing handoffs</span>
<small>The handoff that exit discipline verifies.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The shapes of both contracts.</small>
</a>

<a href="failure-modes/">
<strong>Reference</strong>
<span>Failure modes</span>
<small>How blocked exits compose with the wider failure posture.</small>
</a>

</div>
