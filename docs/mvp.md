# MVP Plan

<p className="craik-meta"><span>6 min read</span><span>For contributors</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What's in this doc**

The accepted v0.x.0 MVP scope: the single workflow Craik proves
end-to-end, the components that ship, the build order, the non-goals
held off until later, and the success criteria the MVP is measured
against.

</div>

<div className="craik-keypoint">

**Prove one workflow — not a broad platform shell.**

Given a real software repository, Craik should assemble a task-specific
project model, guide an agent through governed work, record capability
receipts, and produce a durable handoff backed by memory.

</div>

## Accepted primary demo

The accepted first demo target is **Stigmem documentation and state
reconciliation**. It exercises the problems Craik is designed to solve:
stale documentation · public/internal documentation boundaries ·
immutable ADR constraints · live GitHub state · Stigmem facts ·
operator and credential identity · multi-agent handoff continuity ·
verifiable tool use.

<ol className="craik-steps">
<li>Connect Craik to a GitHub repository.</li>
<li>Register the Stigmem repository as the project.</li>
<li>Connect to a local Stigmem node.</li>
<li>Authenticate the operator via OIDC and configure a provider credential profile.</li>
<li>Ingest repo state, docs, ADRs, issues, PRs, branch status, prior handoffs, and recent Stigmem facts.</li>
<li>Ask Craik to review whether documentation matches implementation state.</li>
<li>Craik assembles a case file.</li>
<li>An agent performs the review with scoped read/write capabilities.</li>
<li>Craik records key tool-use receipts.</li>
<li>The agent proposes doc updates and facts.</li>
<li>Craik surfaces any contradictions or stale assumptions.</li>
<li>The user approves changes.</li>
<li>Craik creates a structured handoff, updates memory, and exports the work graph.</li>
</ol>

## MVP components

The MVP ships as a CLI-first runtime with real persisted state and
typed schemas. A UI waits until the CLI workflow proves the runtime
contracts are correct.

### CLI

**Full command surface:** `craik home init` · `craik connect stigmem` ·
`craik login` · `craik logout` · `craik whoami` · `craik auth list` ·
`craik auth add` · `craik auth remove` · `craik auth test` ·
`craik auth status` · `craik auth approve` · `craik auth grant` ·
`craik project add` · `craik task create` · `craik case build` ·
`craik run execute` · `craik handoff show` · `craik handoff create` ·
`craik memory propose` · `craik memory diff` · `craik receipts list`.

**Implementation priority order:**

<ol className="craik-steps">
<li><code>craik home init</code></li>
<li><code>craik project add</code></li>
<li><code>craik login</code> and <code>craik auth add</code></li>
<li><code>craik task create</code></li>
<li><code>craik case build</code></li>
<li><code>craik run execute</code></li>
<li><code>craik receipts list</code></li>
<li><code>craik handoff create</code></li>
<li><code>craik memory diff</code></li>
</ol>

### Runtime schemas

**Required:** task request · project profile · case file · capability
grant · capability receipt · handoff · memory proposal · contradiction
report · verification result.

### Memory backends

<div className="craik-grid">

<div>
<h4>In-memory</h4>
<p>For tests and demos. Resets between calls.</p>
</div>

<div>
<h4>Local file</h4>
<p>SQLite-backed development backend. Persists between CLI calls.</p>
</div>

<div>
<h4>Stigmem</h4>
<p>Full product behavior. Reference durable substrate.</p>
</div>

</div>

### Authentication

**Required:** typed credential profiles in `auth-profiles.json` ·
credential source kinds (env-var API key · local-CLI OAuth fallback ·
vendor-CLI bridge · external secret reference · Stigmem-backed
credential reference · marker identity for local no-secret providers) ·
credential pool with rotation, failover, and per-profile health
tracking · OIDC operator login with session persistence · workload
identity providers (CI · Kubernetes · generic file tokens · env-var
tokens) · RFC 8693 token exchange for short-lived federated provider
credentials · credential-scoped receipts · operator-scoped receipts ·
policy-bound operators and credentials · approval-gated first live
credential use.

### GitHub adapter

<div className="craik-decision">

<div>
<h4>Required reads</h4>
<ul>
<li>Repository metadata</li>
<li>Branches</li>
<li>Issues</li>
<li>Pull requests</li>
<li>Changed files</li>
<li>Comments</li>
<li>CI status</li>
</ul>
</div>

<div>
<h4>Initial writes</h4>
<ul>
<li>Create issue</li>
<li>Create PR</li>
<li>Comment on issue or PR</li>
</ul>
</div>

</div>

### Repository adapter

**Required:** read file tree · read files · inspect branch status ·
inspect diffs · run configured validation commands · write patches
through an explicit grant.

### Handoff writer

**Required sections:** task summary · completed actions · artifacts
created · files changed · commands run · tests run · facts learned ·
facts invalidated · unresolved questions · risks · next steps · links
to receipts.

### Case file assembler

**Required sections:** task objective · policy envelope · relevant
facts · relevant docs · relevant ADRs · current branch state · open
issues and PRs · recent handoffs · stale-risk notes · contradiction
notes · verification expectations.

<div className="craik-keypoint">

**The case file is the most important MVP artifact.**

If a future agent cannot use it to understand why the current task is
safe, relevant, and bounded, the MVP is not complete.

</div>

## MVP build order

<ol className="craik-steps">
<li>Define schemas and fixtures.</li>
<li>Build local project registry.</li>
<li>Build case-file assembly from local repo state.</li>
<li>Add local receipt and handoff storage.</li>
<li>Add policy envelope enforcement for write boundaries.</li>
<li>Add Stigmem memory read/propose/write.</li>
<li>Add GitHub read-only context.</li>
<li>Add guarded GitHub writes.</li>
<li>Add work graph export.</li>
<li>Add contradiction reports and memory diff.</li>
</ol>

## Non-goals for MVP

Explicitly out of scope. Listed here so they don't sneak back in.

<div className="craik-grid">

<div><h4>Full UI</h4><p>CLI proves the runtime contracts first.</p></div>
<div><h4>Plugin marketplace</h4><p>Contracts ship; distribution is later.</p></div>
<div><h4>Multi-tenant SaaS</h4><p>Single-operator workflows are the proof point.</p></div>
<div><h4>Autonomous background execution</h4><p>Operator-initiated runs only.</p></div>
<div><h4>Broad provider abstraction</h4><p>OpenAI + Anthropic + OAI-compatible is the bar.</p></div>
<div><h4>Complex scheduling</h4><p>Cron-style schedules are gateway territory, not MVP.</p></div>
<div><h4>Enterprise policy editor</h4><p>YAML profiles and CI policy tests are enough.</p></div>
<div><h4>Federated memory</h4><p>Single Stigmem node is the MVP target.</p></div>

</div>

## MVP success criteria

The MVP succeeds if a new agent can:

<ol className="craik-steps">
<li>Understand the current state of a repository faster.</li>
<li>Avoid repeating already-resolved investigation.</li>
<li>Identify stale documentation.</li>
<li>Leave a useful handoff.</li>
<li>Create memory updates that future agents can use.</li>
</ol>

The MVP is evaluated on real project workflows, not toy examples.

For the accepted Stigmem docs reconciliation demo, success also
requires:

<ol className="craik-steps">
<li>The case file clearly identifies ADR constraints and public/internal documentation boundaries.</li>
<li>Stale documentation findings include evidence.</li>
<li>Proposed updates avoid immutable ADR edits.</li>
<li>Receipts capture meaningful file, shell, GitHub, and memory actions.</li>
<li>The handoff is useful to a later agent without relying on chat history.</li>
<li>Stigmem receives appropriate fact proposals or fact writes.</li>
</ol>

## What's next

<div className="craik-next">

<a href="../mvp-roadmap/">
<strong>Read next</strong>
<span>MVP roadmap</span>
<small>The release-readiness work that must land before v0.1 ships.</small>
</a>

<a href="../features/">
<strong>Read</strong>
<span>Features</span>
<small>Per-feature acceptance criteria that compose into the MVP.</small>
</a>

<a href="../implementation-plan/">
<strong>Read</strong>
<span>Implementation plan</span>
<small>The buildable sequence under the chosen stack.</small>
</a>

</div>
