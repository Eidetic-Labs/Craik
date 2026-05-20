# ADR 0001 · Record MVP runner scope

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-04-22</span></p>

<div className="craik-lead">

**What this ADR decides**

That the MVP runner path is a deterministic provider-backed
certification path by default, not a fully autonomous agent loop. Live
model invocation and real side effects ship behind explicit
configuration, grants, redacted receipts, and release-gate coverage.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

Match public framing to the shipped artifact.

</div>

## Context

Craik's public framing must match the shipped artifact. The MVP
already has case-file assembly, policy envelopes, prompt compilation,
receipts, handoffs, work graphs, local memory proposals,
Stigmem-compatible reads, and deterministic OpenAI- and
Anthropic-shaped provider runner paths. It does not yet perform live
model calls, arbitrary tool execution, file edits, or remote Stigmem
writes without an explicit grant flow.

## Decision

<div className="craik-grid">

<div>
<h4>Default runner path</h4>
<p>Deterministic provider-backed certification path. Validates contracts and policy boundaries for OpenAI and Anthropic provider families without live calls in tests or demos.</p>
</div>

<div>
<h4>Live invocation</h4>
<p>Added behind explicit configuration, least-privilege grants, redacted receipts, and release-gate coverage.</p>
</div>

<div>
<h4>Adapter framing</h4>
<p>Codex, Claude, and Gemini adapters documented as prompt-handoff or fixture adapters until they invoke real runners.</p>
</div>

</div>

## Consequences

<div className="craik-grid">

<div><h4>Honest docs</h4><p>README and MVP docs lead with the true current surface, not a promise of full autonomy.</p></div>
<div><h4>Operator command</h4><p><code>craik run execute</code> is the operator command for the deterministic MVP runner workflow.</p></div>
<div><h4>Policy regression</h4><p>Policy tests include a provider-runner grant boundary check instead of a placeholder.</p></div>
<div><h4>Future priorities</h4><p>Live invocation · bounded tool execution · remote Stigmem write promotion · package cleanup. All ahead of broader surface expansion.</p></div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik moves to a different default runner posture
(for example, live calls becoming the default rather than an opt-in).

</div>

## What's next

<div className="craik-next">

<a href="../provider-transport-and-mode-families/">
<strong>ADR</strong>
<span>0002 · Provider transport &amp; mode families</span>
<small>How the runner path actually composes transports and provider families.</small>
</a>

<a href="../../mvp/">
<strong>Read</strong>
<span>MVP plan</span>
<small>The accepted v0.x.0 scope this ADR backs.</small>
</a>

<a href="../../limitations/">
<strong>Read</strong>
<span>Limitations</span>
<small>The honest current-vs-deferred boundary.</small>
</a>

</div>
