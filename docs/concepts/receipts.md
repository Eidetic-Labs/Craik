# Receipts

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a capability receipt is, and what kinds of actions produce one.
- The fields every receipt carries and how they bind to operator + credential identity.
- How redaction keeps secrets out of the receipt store.
- How to query receipts by task, policy envelope, or handoff.

</div>

<div className="craik-keypoint">

**Capability receipt**

A concise, durable accountability record for an action that mattered.
Every receipt names *who* acted, *what* they used, *what* they touched,
*why* it happened, and *how* it ended — bound to both an operator identity
and a credential identity.

Receipts are **not** full transcripts. They're the short, queryable record
the next agent, the next operator, and the next auditor can ground their
decisions on.

</div>

## The contract

`craik.capability_receipt` is one of the few public contracts Craik guarantees
across versions. Its shape:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>Stable id, prefixed <code>rcpt_</code>. Used to join across tasks, handoffs, and policy.</dd>
</div>

<div>
<dt>actor</dt>
<dt><span className="craik-fields__type">operator_uri</span></dt>
<dd>OIDC operator identity that initiated the action.</dd>
</div>

<div>
<dt>credential</dt>
<dt><span className="craik-fields__type">credential_uri</span></dt>
<dd>Credential profile or pool member used. Bound at runtime.</dd>
</div>

<div>
<dt>task_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The task this action belongs to. First-class field.</dd>
</div>

<div>
<dt>capability</dt>
<dt><span className="craik-fields__type">capability_name</span></dt>
<dd>Which capability grant authorized the action — e.g., <code>provider.call</code>, <code>fs.write</code>.</dd>
</div>

<div>
<dt>target</dt>
<dt><span className="craik-fields__type">uri</span></dt>
<dd>What the action affected. A file path, provider endpoint, memory scope, etc.</dd>
</div>

<div>
<dt>reason</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The short, human-readable justification.</dd>
</div>

<div>
<dt>policy_envelope_id</dt>
<dt><span className="craik-fields__type">id (in metadata)</span></dt>
<dd>The policy that gated the action. Carried in <code>result.metadata.policy_envelope_id</code>.</dd>
</div>

<div>
<dt>handoff_ids</dt>
<dt><span className="craik-fields__type">id[] (in metadata)</span></dt>
<dd>Handoffs that reference this receipt. Carried in <code>result.metadata.handoff_ids</code>.</dd>
</div>

<div>
<dt>fail_open</dt>
<dt><span className="craik-fields__type">bool</span></dt>
<dd><code>true</code> if the run took a fail-open path; receipts are still written so the choice is auditable.</dd>
</div>

<div>
<dt>result</dt>
<dt><span className="craik-fields__type">result</span></dt>
<dd>Redacted summary — <code>ok</code> / <code>error</code>, redacted payload references, and metadata. Never raw secrets.</dd>
</div>

<div>
<dt>sealed_at</dt>
<dt><span className="craik-fields__type">timestamp</span></dt>
<dd>Wall-clock time the receipt was sealed and persisted.</dd>
</div>

</div>

## What produces a receipt

Today's MVP writes receipts when the runtime is the direct actor: provider
calls, credential use, memory writes, policy decisions, and certain
runtime side-effect wrappers. Tool execution that lives outside the
runtime (an arbitrary shell command the agent runs) does not yet auto-emit
a receipt — that work is on the roadmap as side-effect wrappers extend.

If you need every shell command to be receipted today, route it through the
side-effect wrappers documented in [Side-effect wrappers](../reference/side-effect-wrappers.md).

## Redaction is non-negotiable

Receipts may not contain raw secrets or credentials. Local persistence
validates every stored receipt through the central redaction guard and
rejects payloads that still appear to contain unredacted secret material.

In practice that means receipt authors should:

- Use redacted summaries (`status: ok`, `tokens: 1842`) instead of raw
  request/response payloads.
- Pass file *paths* and content hashes in metadata, not file content.
- Reference credentials by profile URI, never by the secret itself.
- Strip credential-bearing URLs in metadata (`?token=…`) before sealing.

See [Redaction](../reference/redaction.md) for the full ruleset and how to
extend the guard for new redaction patterns.

## Query receipts

```bash title="List all receipts"
craik receipts list
```

```bash title="Filter by linkage"
craik receipts list --task-id task_docs_reconcile
craik receipts list --policy-id policy_docs_reconcile
craik receipts list --handoff-id handoff_docs_reconcile
```

```bash title="Inspect one receipt as JSON"
craik receipts show rcpt_pytest
```

Both `list` and `show` print JSON payloads matching the
`craik.capability_receipt` schema. Pipe to `jq` for ergonomic filtering.

## An example receipt

```json title="rcpt_4f1c · provider call"
{
  "id": "rcpt_4f1c",
  "actor": "oidc://acme.okta.com#alice",
  "credential": "pool:openai-prod#k_77a",
  "task_id": "task_review_docs",
  "capability": "provider.call",
  "target": "anthropic.messages",
  "reason": "Compile migration plan for task_review_docs",
  "fail_open": false,
  "result": {
    "status": "ok",
    "model": "claude-opus-4-7",
    "tokens": 1842,
    "metadata": {
      "policy_envelope_id": "policy_review_docs",
      "handoff_ids": ["handoff_review_docs"],
      "evidence_refs": ["adr/0042", "pr/1188"]
    }
  },
  "sealed_at": "2026-05-19T14:08:21Z"
}
```

## Current scope

The receipt store and query commands are implemented end-to-end. Automatic
receipt-producing wrappers for shell commands, file writes, GitHub writes,
case-file builds, and handoffs are in progress — see
[Roadmap](../roadmap.md) for the current state.

## What's next

<div className="craik-next">

<a href="../handoffs/">
<strong>Read next</strong>
<span>Handoffs</span>
<small>How a run ends and how the next agent picks up.</small>
</a>

<a href="../governance/">
<strong>Read</strong>
<span>Governance</span>
<small>Policy envelopes, capability grants, and the gates that decide which receipts even get a chance to be written.</small>
</a>

<a href="../../reference/redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The redaction guard, its patterns, and how to extend it.</small>
</a>

</div>
