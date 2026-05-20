# Governance Model

<p className="craik-meta"><span>7 min read</span><span>For policy operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The runtime contracts that make governance native — not an enterprise
  add-on.
- The default security posture and the three named policy profiles.
- How capability grants, receipts, redaction, immutable paths, memory
  policy, and contradictions all compose.
- How Craik degrades transparently when Stigmem isn't available.

</div>

<div className="craik-keypoint">

**Governance-native runtime.**

Policy is not an enterprise add-on; it is part of the runtime contract.
Every governed action — file write, shell command, GitHub write, memory
write, sandbox decision — runs inside a typed envelope and emits a
receipt.

</div>

## Policy envelope

Every task runs inside a policy envelope. The envelope is a typed
runtime record that travels with the task and defines authority.

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>actor</dt>
<dt><span className="craik-fields__type">operator_uri</span></dt>
<dd>OIDC operator identity driving the task.</dd>
</div>

<div>
<dt>task_scope</dt>
<dt><span className="craik-fields__type">scope</span></dt>
<dd>Which tasks this envelope authorizes.</dd>
</div>

<div>
<dt>repository_scope</dt>
<dt><span className="craik-fields__type">scope</span></dt>
<dd>Which repositories the actions may touch.</dd>
</div>

<div>
<dt>memory_scope</dt>
<dt><span className="craik-fields__type">scope</span></dt>
<dd>Which memory scopes the run can read or propose into.</dd>
</div>

<div>
<dt>allowed_capabilities</dt>
<dt><span className="craik-fields__type">capability[]</span></dt>
<dd>The explicit allowed actions for this envelope.</dd>
</div>

<div>
<dt>write_boundaries</dt>
<dt><span className="craik-fields__type">paths</span></dt>
<dd>Where writes may land — immutable paths excluded.</dd>
</div>

<div>
<dt>required_approvals</dt>
<dt><span className="craik-fields__type">capability[]</span></dt>
<dd>Actions that require explicit approval before execution.</dd>
</div>

<div>
<dt>required_verification</dt>
<dt><span className="craik-fields__type">command[]</span></dt>
<dd>Validation steps that must run before completion.</dd>
</div>

<div>
<dt>documentation_obligations</dt>
<dt><span className="craik-fields__type">obligation[]</span></dt>
<dd>Doc updates the run must produce or propose.</dd>
</div>

<div>
<dt>handoff_obligations</dt>
<dt><span className="craik-fields__type">obligation[]</span></dt>
<dd>Required handoff fields and self-audit items.</dd>
</div>

</div>

## Default security posture

<div className="craik-keypoint">

**Secure by default. Fail-open by named policy only.**

Fail-open behavior is allowed only through named policy profiles. It
should never happen as an accidental fallback. Every fail-open
decision is visible in the envelope, the case file, the receipts, and
the handoff.

</div>

**Default behavior:** task execution starts read-only · file writes
require grants · shell commands require grants · GitHub writes require
grants · memory writes default to proposals · immutable paths denied
by default · runner adapters cannot bypass Craik grants · plugins
start probationary · important actions create receipts.

The v0.1 policy profile implementation generates the envelope directly
and provides a mandatory fail-open receipt shape for trusted-local
opt-ins. Case files and handoffs preserve those fields when assembled
and written.

## Policy profiles

Craik ships three conservative named profiles. Switching between them
is a policy decision — never an agent decision.

### Strict

The default profile for normal tasks.

```yaml title="strict.yaml"
policy:
  mode: strict
  fail_open: false
```

**Expected behavior:** read-only by default · explicit grants for all
writes · memory writes become proposals unless direct write is granted
· shell commands require grant · GitHub writes require grant ·
immutable path writes denied.

### Trusted-local

Opt-in profile for tightly-scoped local development.

```yaml title="trusted-local.yaml"
policy:
  mode: trusted-local
  fail_open: true
  require_receipts: true
```

**Expected behavior:** broader local file and shell access may be
allowed · receipts remain mandatory · secrets still redacted ·
immutable path writes still require explicit override · direct memory
writes still require a `memory.write` grant.

### Automation

Profile for CI and unattended workflows.

```yaml title="automation.yaml"
policy:
  mode: automation
  fail_open: false
```

**Expected behavior:** deterministic grants · no interactive approval
requirement · no broad shell access unless granted · no direct memory
writes unless granted · failures stop execution instead of widening
permissions.

## Capability grants

Agents do not receive ambient authority. A capability grant is a
typed, narrow, time-bound permission.

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>capability</dt>
<dt><span className="craik-fields__type">capability_name</span></dt>
<dd>The specific authority being granted (e.g. <code>repo.write.docs</code>).</dd>
</div>

<div>
<dt>target_scope</dt>
<dt><span className="craik-fields__type">scope</span></dt>
<dd>What this grant applies to — path globs, remote URIs, memory scope.</dd>
</div>

<div>
<dt>allowed_operations</dt>
<dt><span className="craik-fields__type">operation[]</span></dt>
<dd><code>read</code> · <code>write</code> · <code>execute</code> · <code>propose</code>.</dd>
</div>

<div>
<dt>reason</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>Short, human-readable justification.</dd>
</div>

<div>
<dt>expiration</dt>
<dt><span className="craik-fields__type">timestamp</span></dt>
<dd>When the grant stops being valid.</dd>
</div>

<div>
<dt>approval_requirement</dt>
<dt><span className="craik-fields__type">approver_uri</span></dt>
<dd>Who approved the grant.</dd>
</div>

<div>
<dt>receipt_requirement</dt>
<dt><span className="craik-fields__type">bool</span></dt>
<dd>Whether actions under this grant must produce receipts.</dd>
</div>

</div>

**Grant examples:** read repository files · write docs only · run
tests · inspect GitHub PRs · create GitHub comments · write Stigmem
facts in a specific scope.

## Secret handling and redaction

<div className="craik-keypoint">

**Secrets are toxic runtime data.**

They are referenced, not copied. The redaction guard runs before every
persistence boundary — and redaction failures are treated as security
bugs.

</div>

**Secret storage:** local secrets under `~/.craik/secrets/` by default
· environment variables for CI and agent-runner workflows · owner-only
file permissions where supported · no secrets in project-local state.

**Redaction requirements:** centralized in
`craik.runtime.policy.redaction` · scrubs known tokens, API keys,
bearer headers, auth URLs, and configured patterns · applied before
writing logs, receipts, handoffs, case files, memory proposals,
errors, and work-graph events · preserves enough shape to debug
without exposing raw values · local persistence rejects payloads that
still appear to contain unredacted secret material.

**Secrets must not be written to Stigmem facts.**

## Capability-gated actions

The following actions require explicit grants:

<div className="craik-grid">

<div><h4>File writes</h4></div>
<div><h4>File deletion</h4></div>
<div><h4>Shell execution</h4></div>
<div><h4>Git branch mutation</h4></div>
<div><h4>Git commit</h4></div>
<div><h4>Git push</h4></div>
<div><h4>GitHub issue / PR / comment</h4></div>
<div><h4>Stigmem direct fact writes</h4></div>
<div><h4>Contradiction resolution that invalidates facts</h4></div>
<div><h4>Plugin execution with side effects</h4></div>
<div><h4>Runner actions that invoke non-read-only tools</h4></div>

</div>

Read-only actions may still require grants when they could expose
sensitive data.

## Immutable path protection

Project profiles can declare immutable paths — ADR directories, signed
release artifacts, generated audit records, historical migration
records. **Immutable paths are denied by default.**

A write to an immutable path requires **all** of:

<ol className="craik-steps">
<li>Explicit immutable-path override metadata.</li>
<li>User or maintainer approval (recorded in the override).</li>
<li>A capability receipt sealed at the action site.</li>
<li>A handoff note explaining why the override was used.</li>
</ol>

In v0.1 grant checks, override metadata must include who approved the
override and why. **The override is still denied unless a matching
`repo.write.immutable` grant is present.**

## Capability receipts

Important actions produce receipts. Receipts are not log lines —
they're concise accountability records for actions that matter.

**Receipt fields:** receipt id · actor · task id · capability · target
· reason · input summary · result summary · timestamp · policy
envelope id · links to artifacts.

Receipts must record when a task runs under a fail-open policy profile
or when a capability grant widens access beyond strict defaults.

The v0.1 receipt store persists validated `craik.capability_receipt`
records and exposes local lookup through `craik receipts list` and
`craik receipts show`. Receipts link directly to tasks and can link to
policy envelopes and handoffs through redacted result metadata.

## Memory write policy

Memory writes are classified by source so policy can decide what may
act directly versus what must propose.

<div className="craik-fields">

<div>
<dt>Class</dt>
<dt><span className="craik-fields__type">Source</span></dt>
<dd>Typical handling</dd>
</div>

<div>
<dt><strong>observed</strong></dt>
<dt><span className="craik-fields__type">direct</span></dt>
<dd>Seen in repo, tool output, API response, or artifact. May be acted on directly under policy.</dd>
</div>

<div>
<dt><strong>reported</strong></dt>
<dt><span className="craik-fields__type">testimonial</span></dt>
<dd>Stated by a user or agent. Treat as a lead until confirmed.</dd>
</div>

<div>
<dt><strong>inferred</strong></dt>
<dt><span className="craik-fields__type">derived</span></dt>
<dd>Reasoned from evidence. Confirmation required before durable action.</dd>
</div>

<div>
<dt><strong>policy</strong></dt>
<dt><span className="craik-fields__type">governance</span></dt>
<dd>Sourced from ADRs, repo rules, or governance docs. Durable; act on.</dd>
</div>

<div>
<dt><strong>external</strong></dt>
<dt><span className="craik-fields__type">third-party</span></dt>
<dd>Web or package-registry sources. Time-sensitive.</dd>
</div>

<div>
<dt><strong>stale-risk</strong></dt>
<dt><span className="craik-fields__type">aging</span></dt>
<dd>Likely to change. Refresh via freshness probe before use.</dd>
</div>

</div>

## Human overrides

Human overrides create durable records. An override captures **what
was overridden · who overrode it · why · what evidence or policy
applies · what downstream facts or tasks are affected.**

## Contradictions

Contradictions are not silently resolved by last-write-wins. Craik
surfaces **conflicting assertions · source and confidence for each ·
affected tasks · affected docs · proposed resolution · required
reviewer or owner.**

## Degraded mode

Craik may run without Stigmem, but governance features should degrade
transparently — and the product is explicit about unavailable
capabilities.

<div className="craik-decision">

<div>
<h4>With Stigmem</h4>
<ul>
<li>Durable facts with provenance.</li>
<li>Cross-scope contradiction tracking.</li>
<li>Federation between Stigmem nodes.</li>
<li>Trust tiers enforced.</li>
</ul>
</div>

<div>
<h4>Without Stigmem</h4>
<ul>
<li>Facts are local or ephemeral.</li>
<li>Contradiction tracking is local only.</li>
<li>Provenance may be limited.</li>
<li>Federation is unavailable.</li>
<li>Trust tiers may be advisory.</li>
</ul>
</div>

</div>

## Local state governance

Craik uses `~/.craik` as the default local home, with `CRAIK_HOME` as
the primary override. Local state keeps data classes separated.

<div className="craik-grid">

<div><h4><code>config/</code></h4><p>User-editable configuration.</p></div>
<div><h4><code>secrets/</code></h4><p>Local credentials and tokens (owner-only).</p></div>
<div><h4><code>state/</code></h4><p>SQLite databases and durable runtime state.</p></div>
<div><h4><code>cache/</code></h4><p>Disposable data.</p></div>
<div><h4><code>logs/</code></h4><p>Runtime logs.</p></div>
<div><h4><code>receipts/</code></h4><p>Capability receipts.</p></div>
<div><h4><code>handoffs/</code></h4><p>Durable handoff artifacts.</p></div>
<div><h4><code>case-files/</code></h4><p>Assembled task context.</p></div>
<div><h4><code>projects/</code></h4><p>Project registry metadata.</p></div>

</div>

**Security expectations:** home and secrets paths should be owner-only
where supported · secret values must not appear in receipts, logs,
handoffs, or case files · path commands make active local paths
inspectable · project-local `.craik/` directories are explicit opt-in
only.

## What's next

<div className="craik-next">

<a href="../concepts/governance/">
<strong>Read</strong>
<span>Governance concept</span>
<small>The same model from the runtime side — how the pieces fit together.</small>
</a>

<a href="../reference/policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The full ruleset for every profile Craik ships.</small>
</a>

<a href="../reference/policy-tests/">
<strong>Reference</strong>
<span>Policy tests</span>
<small>The CI gate that verifies this contract on every PR.</small>
</a>

</div>
