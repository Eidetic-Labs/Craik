# Project Model

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a *project profile* is and why Craik builds one for every repository it touches.
- The boundary distinction between **mutable docs** and **immutable evidence**.
- What `craik onboard` emits and how runners consume it.
- How project state changes propagate to case files and handoffs.

</div>

<div className="craik-keypoint">

**Project profile**

The runner-readable view Craik builds from a registered repository.
It combines local configuration, repository state, documentation
boundaries, memory backend posture, policy posture, and known continuity
records into a single typed object every Craik component speaks.

</div>

The project profile is **operational**, not descriptive. It tells an
agent — human or model — concrete things it can act on:

- Which repository is being entered.
- Which docs are mutable.
- Which paths are immutable evidence.
- Which memory backend is configured.
- Which tasks and handoffs already exist.
- Which contradictions still need review.
- Which validation commands are expected.
- Which next actions are currently allowed.

When Craik builds a case file or a runner prompt, the project profile is the
substrate every other layer is drawn against.

## Mutable docs vs immutable evidence

Project profiles draw a clear line between documentation an agent may edit
and evidence that should never be overwritten.

<div className="craik-decision">

<div>
<h4>Mutable docs</h4>
<ul>
<li><code>README.md</code>, files under <code>docs/</code>, and other configured doc roots.</li>
<li>Loaded into the case file as <em>context</em>.</li>
<li>Edits are allowed when the policy envelope grants write authority.</li>
<li>Touched by agents producing PRs, drafts, or reconciliations.</li>
</ul>
</div>

<div>
<h4>Immutable evidence</h4>
<ul>
<li>ADR directories (<code>docs/adr/</code>) and any path explicitly marked immutable in the project profile.</li>
<li>Loaded into the case file as <em>evidence</em>.</li>
<li>Edits require a separate, explicit policy grant.</li>
<li>Used by agents to justify decisions, not to mutate them.</li>
</ul>
</div>

</div>

This is the line that keeps a "doc reconciliation agent" from silently
overwriting an ADR while updating the surrounding guides.

## What `craik onboard` emits

`craik onboard --project <project-id-or-name>` prints a
`craik.agent_onboarding` payload — the canonical, machine-readable
introduction a runner sees on every task.

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Description</dd>
</div>

<div>
<dt>project</dt>
<dt><span className="craik-fields__type">project_profile</span></dt>
<dd>The full project profile — repo, branches, docs, immutable paths, validation commands.</dd>
</div>

<div>
<dt>policy_envelope</dt>
<dt><span className="craik-fields__type">policy.envelope</span></dt>
<dd>Active policy posture: write authority, review gates, credential bindings, redaction settings.</dd>
</div>

<div>
<dt>docs_boundaries</dt>
<dt><span className="craik-fields__type">boundary_set</span></dt>
<dd>Concrete lists of mutable doc roots and immutable evidence roots.</dd>
</div>

<div>
<dt>recent_handoffs</dt>
<dt><span className="craik-fields__type">handoff[]</span></dt>
<dd>The last <em>n</em> handoffs for the project, so agents resume from real state.</dd>
</div>

<div>
<dt>unresolved_contradictions</dt>
<dt><span className="craik-fields__type">contradiction[]</span></dt>
<dd>Open contradictions surfaced from memory or previous runs.</dd>
</div>

<div>
<dt>stale_risk_warnings</dt>
<dt><span className="craik-fields__type">marker[]</span></dt>
<dd>Pieces of context the runtime believes may be out of date.</dd>
</div>

<div>
<dt>validation_commands</dt>
<dt><span className="craik-fields__type">command[]</span></dt>
<dd>The verification harness the runner is expected to use (tests, linters, type-checkers).</dd>
</div>

<div>
<dt>stigmem_backend</dt>
<dt><span className="craik-fields__type">backend_status</span></dt>
<dd>Whether Stigmem is configured and whether connection env vars are present. No credentials in payload.</dd>
</div>

<div>
<dt>known_traps</dt>
<dt><span className="craik-fields__type">trap[]</span></dt>
<dd>Negative knowledge from previous runs — what <em>not</em> to do, with reasons.</dd>
</div>

<div>
<dt>allowed_next_actions</dt>
<dt><span className="craik-fields__type">action[]</span></dt>
<dd>The actions policy + intent lock currently permit. The agent's menu.</dd>
</div>

</div>

`craik onboard` does **not** probe external services by default. Stigmem
status reports whether the project is configured for Stigmem and whether
connection environment variables are present — it never prints credentials.

## Inspecting a project

<div className="craik-cmd">
<code>craik project list</code>
<p>List all registered projects with their ids, names, and Git heads.</p>
</div>

<div className="craik-cmd">
<code>craik project show &lt;name-or-id&gt;</code>
<p>Print the full <code>project_profile</code> JSON.</p>
</div>

<div className="craik-cmd">
<code>craik onboard --project &lt;name-or-id&gt;</code>
<p>Print the <code>craik.agent_onboarding</code> payload — what a runner sees first.</p>
</div>

## How updates propagate

The project profile is the canonical source for case files, intent locks,
and onboarding payloads. When you change a project — register a new immutable
path, configure a memory backend, add validation commands — the next case
file build reflects it. Existing handoffs aren't rewritten; they stay
faithful to the project state at the time the run ended.

## What's next

<div className="craik-next">

<a href="../case-files/">
<strong>Read next</strong>
<span>Case files</span>
<small>The per-task pre-run brief Craik assembles from the project model.</small>
</a>

<a href="../governance/">
<strong>Read</strong>
<span>Governance</span>
<small>The policy envelope, capability grants, and review gates that ride on top of the project model.</small>
</a>

<a href="../../guides/project-registry/">
<strong>Do</strong>
<span>Register a project</span>
<small>Step-by-step: hook a Git repo into Craik and inspect what the runtime sees.</small>
</a>

</div>
