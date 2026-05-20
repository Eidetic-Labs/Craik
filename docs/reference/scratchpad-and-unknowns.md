# Scratchpad and unknowns

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

Two contracts that preserve incompleteness instead of forcing
agents to guess — `craik.scratchpad_record` for expiring working
notes, and `craik.unknown_record` for explicit gaps.

</div>

<div className="craik-keypoint">

**Expire by default; promote explicitly.**

Scratchpad records must expire. They become durable context only
through an explicit review path.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Stores</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.scratchpad_record</code></dt>
<dt><span className="craik-fields__type">working notes</span></dt>
<dd>Owner · note text · evidence links · status · creation time · expiry. Expired records are filtered from active runtime context.</dd>
</div>

<div>
<dt><code>craik.unknown_record</code></dt>
<dt><span className="craik-fields__type">explicit gap</span></dt>
<dd>Question · owner · what is needed to resolve it · next action · evidence · resolution details when available.</dd>
</div>

</div>

<div className="craik-keypoint">

**Visible incompleteness.**

Unresolved unknowns are surfaced in case-file stale risks and handoff
context debt so future agents see what remains unknown before
continuing.

</div>

## What's next

<div className="craik-next">

<a href="context-debt/">
<strong>Reference</strong>
<span>Context debt</span>
<small>How unknowns flow into the durable debt record.</small>
</a>

<a href="exit-discipline/">
<strong>Reference</strong>
<span>Exit discipline</span>
<small>The exit checklist that surfaces unresolved unknowns.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>scratchpad_record</code> and <code>unknown_record</code> shapes.</small>
</a>

</div>
