# Agent onboarding

<p className="craik-meta"><span>2 min read</span><span>For agents &amp; operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Run `craik onboard` before starting project work. The command emits a
runner-parseable `craik.agent_onboarding` JSON report covering the
project model, active policy, docs boundaries, recent handoffs,
contradictions, stale-risk warnings, validation commands, Stigmem
status, known traps, and allowed next actions.

</div>

<div className="craik-keypoint">

**Onboarding is read-only.**

The command prints structured JSON. It does not modify state, make
live Stigmem calls, or surface secrets.

</div>

## Run it

```sh
craik onboard --project Example
```

The output is structured JSON safe for runners to parse directly.

## Policy profile

```sh
craik onboard --project Example --policy-profile strict
```

<div className="craik-fields">

<div>
<dt>Profile</dt>
<dt><span className="craik-fields__type">Fail-open</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>strict</code></dt>
<dt><span className="craik-fields__type">closed</span></dt>
<dd>Default. The active policy is included in the output so agents see allowed capabilities, denied capabilities, approval requirements, and verification requirements.</dd>
</div>

<div>
<dt><code>trusted-local</code></dt>
<dt><span className="craik-fields__type">opt-in only</span></dt>
<dd>Requires the explicit fail-open flag: <code>craik onboard --project Example --policy-profile trusted-local --trusted-local-fail-open</code>.</dd>
</div>

</div>

## Documentation boundaries

<div className="craik-keypoint">

**Immutable paths are evidence.**

The `docs_boundaries` section separates mutable docs from immutable
paths. Immutable docs (such as ADRs) are evidence — do not edit them
unless a separate policy approval explicitly allows it.

</div>

## Continuity checks

Onboarding surfaces six continuity fields. Agents must review them
before creating a plan.

<div className="craik-grid">

<div><h4>Recent handoffs</h4><p>For the project.</p></div>
<div><h4>Unresolved contradictions</h4></div>
<div><h4>Stale-risk warnings</h4></div>
<div><h4>Validation commands</h4><p>Configured for the project.</p></div>
<div><h4>Known traps</h4></div>
<div><h4>Allowed next actions</h4></div>

</div>

Missing handoffs, missing docs paths, dirty repository state,
unresolved contradictions, or missing Stigmem environment
configuration are reported as stale-risk warnings.

## Stigmem status

Onboarding does not print secrets or make a live Stigmem request. For
Stigmem projects, it reports whether `CRAIK_STIGMEM_URL` and
`CRAIK_STIGMEM_API_KEY` are configured. Use
`craik connect stigmem` when a live backend compatibility check is
needed.

## What's next

<div className="craik-next">

<a href="../using-case-files/">
<strong>Guide</strong>
<span>Using case files</span>
<small>Read the case file that onboarding hints at.</small>
</a>

<a href="../../reference/known-traps/">
<strong>Reference</strong>
<span>Known traps</span>
<small>The traps registry onboarding surfaces.</small>
</a>

<a href="../connecting-stigmem/">
<strong>Guide</strong>
<span>Connecting Stigmem</span>
<small>Configure the backend before onboarding requires it.</small>
</a>

</div>
