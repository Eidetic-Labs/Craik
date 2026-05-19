# ADR 0006 · Package and runtime layout

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-05-02</span></p>

<div className="craik-lead">

**What this ADR decides**

That Craik groups implementation files by concern under
`runtime.providers`, `runtime.memory`, `runtime.policy`, `runtime.work`,
`runtime.runners`, `runtime.channels`, `runtime.sandbox`, and
companion packages — while keeping `craik.contracts.models` and common
`craik.runtime.*` imports as compatibility surfaces.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

Ownership and review scope live in the package layout, not in a flat
runtime namespace.

</div>

## Context

Craik started with broad runtime and contract modules because early
milestones were contract-heavy and issue-driven. That made discovery
easy at first, but it created god files and a flat runtime namespace
that hid ownership boundaries. The runtime now contains providers,
memory, policy, work execution, companions, channels, voice,
sandboxing, and project workflows with different change rates and risk
profiles.

## Decision

<div className="craik-grid">

<div><h4><code>runtime.providers</code></h4></div>
<div><h4><code>runtime.memory</code></h4></div>
<div><h4><code>runtime.policy</code></h4></div>
<div><h4><code>runtime.work</code></h4></div>
<div><h4><code>runtime.runners</code></h4></div>
<div><h4><code>runtime.channels</code></h4></div>
<div><h4><code>runtime.sandbox</code></h4></div>
<div><h4>Companion packages</h4></div>

</div>

<div className="craik-keypoint">

**Compatibility surface preserved.**

The root runtime package maintains lazy legacy module aliases for
moved public modules. No runtime package should grow beyond 15 sibling
Python modules without a new layout decision or a deeper package split.

</div>

## Consequences

This makes ownership and review scope clearer while preserving
existing imports. It also adds a compatibility layer that must be
tested whenever modules move. New work should choose the package that
matches the runtime concern rather than creating one module per issue
at the root.

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>Leave compatibility shim files at the runtime root</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Would preserve the flat sibling-module problem.</dd>
</div>

<div>
<dt>Break legacy imports and update every caller</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>The public import surface is already used by tests, docs, and downstream automation.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik adopts a generated API layer or a plugin
loader that replaces direct runtime package imports.

</div>

## What's next

<div className="craik-next">

<a href="../../architecture/">
<strong>Read</strong>
<span>Architecture</span>
<small>The seven runtime layers this layout backs.</small>
</a>

<a href="../record-mvp-runner-scope/">
<strong>ADR</strong>
<span>0001 · Record MVP runner scope</span>
<small>The framing decision that shaped the runtime cleanup.</small>
</a>

<a href="../../implementation-plan/">
<strong>Read</strong>
<span>Implementation plan</span>
<small>The repo-shape recommendation that aligns with this ADR.</small>
</a>

</div>
