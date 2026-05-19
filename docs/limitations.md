# Limitations

<p className="craik-meta"><span>4 min read</span><span>For everyone</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What's in this doc**

The honest scope boundary for the `0.1.0` MVP release. What's
end-to-end production-ready today, what exists as contract/helper
scaffolding, what's deliberately deferred, and how the v0.1 release
posture is framed.

</div>

<div className="craik-keypoint">

**End-to-end versus contract.**

The repository has broad contract, helper, CLI, and documentation
coverage through the v0.12 roadmap — but several surfaces are not yet
end-to-end production workflows. This doc draws the line.

</div>

## Current end-to-end surfaces

The pieces below ship as user-facing workflows with persistence, docs,
tests, and CI coverage.

<div className="craik-grid">

<div><h4>Local home &amp; store</h4><p>Initialization, layout, override via <code>CRAIK_HOME</code>.</p></div>
<div><h4>Project registration</h4><p>Add, list, inspect projects. Task creation.</p></div>
<div><h4>Case-file assembly</h4><p>From local repo state plus optional read-only GitHub context.</p></div>
<div><h4>Local artifacts</h4><p>Receipts, handoffs, memory proposals, contradictions, work-graph inspection.</p></div>
<div><h4>Policy</h4><p>Profile generation, capability-grant checks, regression tests.</p></div>
<div><h4>Stigmem reads</h4><p>Compatibility detection and policy-gated direct fact write helpers.</p></div>
<div><h4>Fixture loop</h4><p>Deterministic fixture loop and runner preview contracts.</p></div>
<div><h4>Provider paths</h4><p>Fixture-backed and live opt-in OpenAI Responses, Anthropic Messages, and OAI-compatible Chat Completions.</p></div>
<div><h4>OIDC login</h4><p>Device-code and loopback+PKCE flows.</p></div>
<div><h4>Credential sources</h4><p>Env-var API keys, local-CLI OAuth fallback, vendor-CLI bridges, secret references, markers, Stigmem-backed references.</p></div>
<div><h4>Credential pools</h4><p>Failover and per-profile health tracking.</p></div>
<div><h4>Identity on receipts</h4><p>Operator and credential identity on every provider receipt.</p></div>
<div><h4>Policy-bound credentials</h4><p>Operators and credentials constrained by policy.</p></div>
<div><h4>Approval-gated first use</h4><p>First live use of a credential requires explicit approval.</p></div>
<div><h4>Stigmem docs demo</h4><p>The accepted release-acceptance workflow.</p></div>

</div>

## Contract or helper surfaces

These surfaces ship as typed contracts, evaluators, formatters, or
fixtures — useful, but **not yet operational workflows**.

<div className="craik-fields">

<div>
<dt>Surface</dt>
<dt><span className="craik-fields__type">Status</span></dt>
<dd>What's missing</dd>
</div>

<div>
<dt>Live provider execution</dt>
<dt><span className="craik-fields__type">opt-in only</span></dt>
<dd>Fixture-backed by default. Live HTTP requires <code>live_enabled=true</code> on <code>ProviderRuntimeConfig</code> plus a resolved credential. CI does not exercise paid live providers.</dd>
</div>

<div>
<dt>Runner adapters</dt>
<dt><span className="craik-fields__type">preview</span></dt>
<dd>Outside governed provider-backed paths, runner adapters remain preview, fixture, or prompt-handoff oriented.</dd>
</div>

<div>
<dt>Execution backends</dt>
<dt><span className="craik-fields__type">boundary-only</span></dt>
<dd>Evaluate boundaries and policy requirements but do not execute shell, start containers, open remote shells, or drive browsers.</dd>
</div>

<div>
<dt>Gateway / channels</dt>
<dt><span className="craik-fields__type">contracts only</span></dt>
<dd>Gateway, webhook, messaging, channel, and scheduled-automation surfaces ship contracts and helpers. No production daemon or dispatch loop yet.</dd>
</div>

<div>
<dt>Operator UI</dt>
<dt><span className="craik-fields__type">view-contract</span></dt>
<dd>Formatter and view-contract level. A full TUI or dashboard is post-MVP unless explicitly pulled into the proof workflow.</dd>
</div>

<div>
<dt>Companion surfaces</dt>
<dt><span className="craik-fields__type">decisions</span></dt>
<dd>Companion, mobile, visual, and multimodal surfaces ship as posture decisions and adapter contracts — not shipped product applications.</dd>
</div>

<div>
<dt>Marketplace</dt>
<dt><span className="craik-fields__type">docs-only</span></dt>
<dd>Marketplace and broad community-ecosystem docs describe future contribution mechanics — not MVP operational support.</dd>
</div>

</div>

## Known MVP gaps

Scheduled milestones with explicit version targets.

<div className="craik-fields">

<div>
<dt>Gap</dt>
<dt><span className="craik-fields__type">Target</span></dt>
<dd>Why it's deferred</dd>
</div>

<div>
<dt>Resumable runs across crashes</dt>
<dt><span className="craik-fields__type">v0.2.0</span></dt>
<dd>Recovery contract ships in MVP; crash-resume coverage waits.</dd>
</div>

<div>
<dt>Real sandbox tool execution</dt>
<dt><span className="craik-fields__type">v0.2.0</span></dt>
<dd>Policy-gated today; isolating sandbox boundary scheduled for v0.2.</dd>
</div>

<div>
<dt>Provider budget enforcement</dt>
<dt><span className="craik-fields__type">v0.2.0</span></dt>
<dd>Call-site enforcement waits on budget runtime hooks.</dd>
</div>

<div>
<dt>Schema migration framework</dt>
<dt><span className="craik-fields__type">v0.2.0</span></dt>
<dd>MVP includes ad-hoc migrations; framework promotes them to first-class.</dd>
</div>

<div>
<dt>Multi-agent runtime</dt>
<dt><span className="craik-fields__type">v0.3.0</span></dt>
<dd>Handoff consumption, role-based dispatch, debate.</dd>
</div>

<div>
<dt>Runtime instruction distillation</dt>
<dt><span className="craik-fields__type">v0.4.0</span></dt>
<dd>Pipeline that promotes declared instruction files to runtime proposals.</dd>
</div>

<div>
<dt>Operator UI / TUI</dt>
<dt><span className="craik-fields__type">v0.7.0</span></dt>
<dd>Operator surfaces ship as view contracts in MVP.</dd>
</div>

<div>
<dt>Always-on gateway daemon</dt>
<dt><span className="craik-fields__type">v0.8.0</span></dt>
<dd>Channels and webhook contracts ship in MVP; live daemon waits.</dd>
</div>

<div>
<dt>MCP client/server</dt>
<dt><span className="craik-fields__type">v0.9.0</span></dt>
<dd>Boundary and metadata contracts ship in MVP; live MCP execution waits.</dd>
</div>

</div>

**Other near-term deferrals:** remote Stigmem write promotion after
proposal review · god-file cleanup and runtime sub-packaging before
the MVP freeze · ADR-backed design decisions for runner scope, release
posture, and package boundaries · nightly reliability and artifact
depth beyond the current PR gates · full post-MVP surfaces tracked in
[Post-MVP Scope](reference/post-mvp-scope.md).

## Write authority

<div className="craik-keypoint">

**No ambient write authority.**

Direct durable memory writes, GitHub writes, shell commands, file
writes, and external side effects must be policy-gated, redacted, and
receipt-backed before they are considered MVP-ready. Local memory
proposals remain the default unprivileged path.

</div>

## Release posture

The first release target is `0.1.0`. The release is honest about
limits and strong enough for a credible MVP — but it is not a `1.0.0`
stability guarantee.

Package version `0.1.0` marks **the first governed agent-runtime
substrate** with live opt-in providers, typed credentials, and operator
identity. Roadmap milestones such as v0.12 remain implementation gates
rather than published-package compatibility guarantees.

## What's next

<div className="craik-next">

<a href="reference/post-mvp-scope.md">
<strong>Reference</strong>
<span>Post-MVP scope</span>
<small>The full list of surfaces deliberately outside MVP, with the gates that move them forward.</small>
</a>

<a href="mvp-roadmap.md">
<strong>Read</strong>
<span>MVP roadmap</span>
<small>The release-readiness checklist driving v0.x.</small>
</a>

<a href="roadmap.md">
<strong>Read</strong>
<span>Roadmap</span>
<small>The broader trajectory through v0.12 and beyond.</small>
</a>

</div>
