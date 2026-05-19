# Secrets

<p className="craik-meta"><span>5 min read</span><span>For everyone</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- Where Craik stores secret material and what it never persists.
- The redaction guarantee that applies to every receipt, handoff, and log.
- How policy profiles and capability grants compose with redaction.
- How to extend redaction for project-specific patterns.

</div>

Design rationale: [ADR 0003 · Secret handling](../adr/0003-secret-handling.md).

<div className="craik-keypoint">

**Secrets are runtime-tier data**

Craik treats secrets as sensitive runtime material — not as configuration.
They live in a single, narrow directory; they never leak into receipts,
case files, or handoffs in raw form; and the redaction guard runs on every
persistence path regardless of profile.

</div>

## Where secrets live

<div className="craik-fields">

<div>
<dt>Path</dt>
<dt><span className="craik-fields__type">Scope</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>~/.craik/secrets/</code></dt>
<dt><span className="craik-fields__type">default</span></dt>
<dd>Per-user secret material when <code>CRAIK_HOME</code> is unset.</dd>
</div>

<div>
<dt><code>$CRAIK_HOME/secrets/</code></dt>
<dt><span className="craik-fields__type">override</span></dt>
<dd>When <code>CRAIK_HOME</code> is set, secrets live under that home.</dd>
</div>

</div>

The secrets directory is created with **owner-only permissions** wherever
the platform supports it (POSIX `0700`, restricted ACLs on Windows). Craik
never creates project-local `.craik/secrets/` directories inside
repositories — that would silently widen the secret surface area to
anything in the repo's filesystem.

## What Craik never persists as raw secrets

The redaction guard ensures the following payloads carry redacted summaries
instead of raw secret material:

<div className="craik-grid">

<div>
<h4>Receipts</h4>
<p>Provider call receipts, credential-use receipts, side-effect receipts — all pass through redaction before storage.</p>
</div>

<div>
<h4>Handoffs</h4>
<p>Structured handoffs and their Markdown renderings — both are scrubbed before persistence.</p>
</div>

<div>
<h4>Logs</h4>
<p>Diagnostic logs are scrubbed of bearer tokens, auth URLs, and configured secret patterns.</p>
</div>

<div>
<h4>Case files</h4>
<p>Case files carry references to credentials by profile URI — never by secret value.</p>
</div>

<div>
<h4>Memory proposals</h4>
<p>Proposal payloads are scrubbed; structured fields with secret-like names are explicitly redacted.</p>
</div>

</div>

## The redaction guard

The central redaction utility is
[`craik.runtime.policy.redaction`](../reference/redaction.md). It redacts
several categories of input before any persistence path completes:

<ol className="craik-steps">
<li>

**Bearer tokens.** `Authorization: Bearer …`, `Authorization: Basic …`,
and similar HTTP header shapes.

</li>
<li>

**Common key/value secret shapes.** Pattern-matched secrets like
`AWS_SECRET_ACCESS_KEY=…`, `OPENAI_API_KEY=sk-…`, `password=…`.

</li>
<li>

**Auth URLs.** URLs with credential material in the query string or
userinfo (`https://user:pass@host/…`, `https://host/?token=…`).

</li>
<li>

**Configured secret patterns.** Project-specific regexes the operator has
declared as sensitive.

</li>
<li>

**Structured fields with secret-like names.** Fields named `secret`,
`token`, `password`, `api_key`, etc., regardless of their value's shape.

</li>
</ol>

The legacy import path `craik.runtime.redaction` remains available for
backward compatibility — both refer to the same guard.

## Policy and grants do not override redaction

This is a hard rule:

<div className="craik-grid">

<div>
<h4>Policy profiles</h4>
<p>The <code>trusted-local</code> fail-open profile still requires redacted receipts. There is no profile that permits raw secret persistence.</p>
</div>

<div>
<h4>Capability grants</h4>
<p>A capability grant authorizes an action — it does not authorize storing unredacted secrets even when the action is allowed.</p>
</div>

<div>
<h4>Fail-open paths</h4>
<p>A fail-open run produces a receipt. The receipt is still scrubbed.</p>
</div>

<div>
<h4>Automation runs</h4>
<p>Automation enforces fail-closed defaults; redaction runs on top of that, not instead of it.</p>
</div>

</div>

## How to handle a real credential

The canonical pattern:

```bash title="Reference a credential by env-var name, not value"
craik auth add anthropic:work \
  --kind=api-key \
  --env-var=ANTHROPIC_API_KEY
```

Craik stores the **reference** (`--env-var=ANTHROPIC_API_KEY`) in
`config/`. The actual secret stays in the operator's environment, secret
manager, or local-CLI credential file. When a run needs the credential,
the runtime resolves it at call time, uses it, and never writes the raw
value anywhere.

For local-CLI OAuth flows, secret-manager references, Stigmem-backed
credentials, and workload-identity patterns, see
[Authentication and credentials](../guides/authentication.md).

## Extending redaction

If your project has secrets that don't match the built-in patterns —
internal API tokens with a custom prefix, signed URLs with non-standard
query parameters — extend the redaction guard:

<div className="craik-cmd">
<code>craik policy show</code>
<p>Inspect the active policy envelope's redaction patterns before extending.</p>
</div>

See [Redaction reference](../reference/redaction.md) for the configuration
shape and validation rules.

## A practical checklist

<ol className="craik-steps">
<li>

**Never commit `~/.craik/secrets/` or `$CRAIK_HOME/secrets/`.** They're
local-only by design.

</li>
<li>

**Reference credentials by env-var or profile URI.** Pass the *name*, not
the value, to `craik auth add`.

</li>
<li>

**Run `craik doctor` before live calls.** It reports which credential
profiles resolve cleanly and which are degraded.

</li>
<li>

**Audit receipts periodically.** `craik receipts list` and inspect a
sample — if anything looks like a raw secret slipped through, file an
incident immediately.

</li>
<li>

**Treat the redaction guard as load-bearing.** Don't disable rules, don't
add catch-alls, and don't route receipts around it.

</li>
</ol>

## What's next

<div className="craik-next">

<a href="../../guides/authentication/">
<strong>Do</strong>
<span>Authentication &amp; credentials</span>
<small>OIDC login, credential profiles, pools, workload identity, and approval flow.</small>
</a>

<a href="../../reference/redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The redaction guard's patterns and how to extend it safely.</small>
</a>

<a href="../../adr/secret-handling/">
<strong>ADR</strong>
<span>Secret handling design</span>
<small>The full rationale and tradeoffs that produced this contract.</small>
</a>

</div>
