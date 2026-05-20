# MVP failure modes

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The MVP hardening posture and the specific boundaries that hold under
adversarial input — prompt injection, secrets, tool calls, timeouts,
persistence, and recovery.

</div>

<div className="craik-keypoint">

**Fail-closed by default.**

The runtime preserves enough state to recover or review a failed run
without silently promoting uncertain work to durable facts.

</div>

## MVP boundaries

<div className="craik-fields">

<div>
<dt>Supported</dt>
<dt><span className="craik-fields__type">in scope</span></dt>
<dd>One release-acceptance workflow · deterministic provider-backed OpenAI &amp; Anthropic execution · local case files · receipts · handoffs · memory proposals · work graphs.</dd>
</div>

<div>
<dt>Not required</dt>
<dt><span className="craik-fields__type">out of scope</span></dt>
<dd>Live provider calls · broad daemon operation · dashboards · direct durable memory writes.</dd>
</div>

</div>

## Prompt injection

<div className="craik-keypoint">

**Hostile text is input, not authority.**

User text, repository text, documentation, and memory facts can
contain hostile instructions. Prompt compilation keeps those inputs
inside task or context sections and always renders the policy
envelope, denied capabilities, grants, context omissions, and stop
conditions.

</div>

## Secrets

Persisted payloads are validated before writing to the local store.
Secret-shaped values in keys or strings are rejected or redacted at
persistence and receipt boundaries. Public documentation checks also
block secrets, private paths, and private task names from Docusaurus
content.

## Tool calls and side effects

<div className="craik-grid">

<div><h4>Missing grants block side effects</h4></div>
<div><h4>Immutable docs require approval</h4></div>
<div><h4>Unsupported capabilities fail closed</h4></div>
<div><h4>Receipts cover shell · file · memory · GitHub writes</h4></div>

</div>

## Timeouts, retries, budgets

<div className="craik-grid">

<div><h4>Network clients</h4><p>Expose timeout configuration · bounded by default.</p></div>
<div><h4>Provider adapters</h4><p>Classify retryable throttling and transient failures · no hidden live retries.</p></div>
<div><h4>Routing</h4><p>Blocks exhausted or mismatched budget/quota status.</p></div>
<div><h4>Agent loops</h4><p>Enforce max-iteration limits and persist an interrupted run at the limit.</p></div>

</div>

## Persisted payloads

<div className="craik-keypoint">

**Validate twice.**

The SQLite store validates every registered contract payload before
persistence and rejects unknown schemas, wrong versions, extra fields,
and unredacted secret material. CI exercises persisted demo artifacts
by reading them back through the contract registry and revalidating
their JSON payloads.

</div>

## Recovery expectations

When a run blocks or fails:

<ol className="craik-steps">
<li>Review the case file, receipts, handoff, run state, and memory proposals before retrying.</li>
<li>Do not convert assumptions, stale risks, or omitted context into facts without new evidence.</li>
</ol>

## What's next

<div className="craik-next">

<a href="../exit-discipline/">
<strong>Reference</strong>
<span>Exit discipline</span>
<small>The checklist that turns failure into reviewable state.</small>
</a>

<a href="../redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The boundary that keeps secrets out of receipts.</small>
</a>

<a href="../../limitations/">
<strong>Read</strong>
<span>Limitations</span>
<small>The honest current-vs-deferred boundary.</small>
</a>

</div>
