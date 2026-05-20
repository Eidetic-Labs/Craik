# Case Files

<p className="craik-meta"><span>6 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a case file is (and what it deliberately isn't).
- The shape of the contract: objective, policy, evidence, assumptions, stale-risk, verification plan.
- How the local assembler builds one, and what gets recorded when context is unavailable.
- How to inspect, replay, and seal a case file.

</div>

<div className="craik-keypoint">

**Case file**

A task-specific context package assembled *before* an agent acts. It is the
bounded work packet that makes the starting point of a task explicit and
reviewable.

A case file is **not** a memory store, and it is **not** a transcript. It
is a sealed, durable snapshot of what the runtime believed at the moment
the task began.

</div>

Every case file gives the next runtime step a single typed object to read
from. That payload covers:

- The task objective.
- The policy envelope id that will gate execution.
- The intent lock id that defines scope.
- Current repository state (branch, head, clean/dirty, default branch).
- The mutable docs the agent may edit.
- The immutable docs it may only cite.
- Evidence references for everything the runtime loaded.
- Assumptions that remain unresolved.
- Stale-risk markers calling out context that may have moved.
- A list of missing context the runtime would have liked to have.
- Deterministic context-budget metadata so the runner doesn't blow past
  its token budget.

## Anatomy of a case file

The on-disk schema is `craik.case_file`. Conceptually:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>task_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The task this case file belongs to. One-to-one.</dd>
</div>

<div>
<dt>objective</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The plain-language objective the agent is being asked to act on.</dd>
</div>

<div>
<dt>policy_envelope_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>Reference to the policy that will gate this run.</dd>
</div>

<div>
<dt>intent_lock_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>Reference to the scope boundaries (in-scope / out-of-scope declarations).</dd>
</div>

<div>
<dt>repo_state</dt>
<dt><span className="craik-fields__type">snapshot</span></dt>
<dd>Branch, head, clean/dirty, default branch, remote URL, immutable path configuration.</dd>
</div>

<div>
<dt>docs</dt>
<dt><span className="craik-fields__type">doc_ref[]</span></dt>
<dd>Mutable documentation files discovered via the project profile.</dd>
</div>

<div>
<dt>immutable_docs</dt>
<dt><span className="craik-fields__type">doc_ref[]</span></dt>
<dd>ADR-style evidence, labeled separately so the runner can't accidentally edit them.</dd>
</div>

<div>
<dt>evidence</dt>
<dt><span className="craik-fields__type">evidence_reference[]</span></dt>
<dd>Provenance for every piece of context — repo file, GitHub issue, memory fact, prior handoff.</dd>
</div>

<div>
<dt>assumptions</dt>
<dt><span className="craik-fields__type">assumption[]</span></dt>
<dd>Things the runtime had to guess because the source was unavailable.</dd>
</div>

<div>
<dt>stale_risk_markers</dt>
<dt><span className="craik-fields__type">marker[]</span></dt>
<dd>Pieces of context the runtime believes may have moved since indexing.</dd>
</div>

<div>
<dt>missing_context</dt>
<dt><span className="craik-fields__type">item[]</span></dt>
<dd>Sources the runtime knows it didn't get to (no GitHub adapter, no memory backend, etc.).</dd>
</div>

<div>
<dt>context_budget</dt>
<dt><span className="craik-fields__type">budget</span></dt>
<dd>Deterministic per-section token allocations so the prompt compiler can keep totals predictable.</dd>
</div>

<div>
<dt>verification_plan</dt>
<dt><span className="craik-fields__type">plan</span></dt>
<dd>Concrete validation steps the runner is expected to execute before declaring success.</dd>
</div>

</div>

## Build a case file

```bash title="Assemble a case file from local state"
craik case build task_docs_reconcile
craik case show task_docs_reconcile
```

`craik case show` dumps the full JSON. Pipe it through `jq` or your editor of
choice — it's designed to be read and reviewed by humans, not just consumed
by runners.

The local assembler can read:

- **Repo state** — Git branch, head, clean/dirty, default branch, remote
  identity, and immutable path configuration from the project profile.
- **Docs and ADRs** — mutable doc roots and immutable evidence roots.
- **GitHub state** — issues and PRs in read-only mode when a GitHub remote
  is configured (skipped under `--no-github`).
- **Memory facts** — only when a memory backend is configured. Otherwise
  the case file records "no memory backend" as an open assumption.
- **Recent handoffs** — the last few handoffs for this project, so the run
  can pick up where prior runs left off.
- **Local contradiction reports** — surfaces unresolved contradictions
  alongside the evidence that proposed them.

## Evidence and assumptions

Every case file is honest about where its context came from — and where it
didn't come from.

### Evidence

Local evidence references use `craik.evidence_reference` records embedded
in the case file. Immutable documentation is marked explicitly so the
runner can't promote it to a mutable doc by mistake:

```json
{
  "kind": "doc",
  "path": "docs/adr/0004-policy-envelope-shape.md",
  "metadata": {
    "immutable": true,
    "indexed_at": "2026-05-19T12:14:08Z"
  }
}
```

### Assumptions

Unsupported conclusions stay assumptions. The assembler records open
assumptions when configured context is unavailable — for example, when no
memory backend is provided, the case file gets an assumption like:

```json
{
  "id": "no-memory-backend",
  "claim": "No project-scoped memory facts were loaded.",
  "reason": "Project has no memory backend configured.",
  "remediation": "Connect Stigmem or set CRAIK_MEMORY_BACKEND.",
  "promoted_to_fact": false
}
```

**Agents should review assumptions before acting** and must not promote
them to facts without evidence. The next handoff is the natural place to
document what was promoted and why.

## Storage and replay

Case files persist as `craik.case_file` records in the local SQLite store
(`$CRAIK_HOME/state/`). Once built, a case file is sealed — Craik never
silently rewrites it. To refresh the context for a re-run, build a *new*
case file. The old one stays addressable for audit.

## Current scope

The local assembler today supports repository files, read-only GitHub
issues and pull requests, memory facts (when a backend is wired in),
recent local handoffs, and local contradiction reports. Anything optional
that's missing is recorded as an open assumption so prompts and reviewers
can tell known project state from unavailable context.

## What's next

<div className="craik-next">

<a href="../receipts/">
<strong>Read next</strong>
<span>Receipts</span>
<small>How Craik makes important actions accountable — every provider call, credential use, side effect.</small>
</a>

<a href="../handoffs/">
<strong>Read next</strong>
<span>Handoffs</span>
<small>The continuity record that ends every run.</small>
</a>

<a href="../../guides/using-case-files/">
<strong>Do</strong>
<span>Use case files in practice</span>
<small>Practical patterns for building, inspecting, and refreshing case files day-to-day.</small>
</a>

</div>
