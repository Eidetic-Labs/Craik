# Runner adapter contract

<p className="craik-meta"><span>7 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The runner-agnostic contract between Craik core and concrete agent
environments. Adapters receive Craik state and return normalized Craik
state without leaking provider-specific details into core contracts.

</div>

<div className="craik-keypoint">

**Adapters translate, they don't grant authority.**

Side effects still require explicit capability grants. Adapter
metadata describes what a runner *can* do; policy decides what it
*may* do.

</div>

## Contracts

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Role</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.runner_metadata</code></dt>
<dt><span className="craik-fields__type">identity</span></dt>
<dd>Runner id &amp; display name · adapter id &amp; version · execution mode (<code>fixture</code> / <code>prompt-handoff</code> / <code>live</code>) · capability names · structured adapter metadata.</dd>
</div>

<div>
<dt><code>craik.runner_adapter_request</code></dt>
<dt><span className="craik-fields__type">input</span></dt>
<dd>Task id · runner metadata · task request id · case file id · policy envelope id · capability grant ids · expected output schemas · bounded context prepared by Craik.</dd>
</div>

<div>
<dt><code>craik.runner_adapter_result</code></dt>
<dt><span className="craik-fields__type">output</span></dt>
<dd>Status (<code>completed</code> / <code>blocked</code> / <code>failed</code> / <code>partial</code>) · summary · structured outputs · receipt ids · optional handoff id · memory proposal ids · artifacts · diagnostics · runner metadata.</dd>
</div>

<div>
<dt><code>craik.runner_step_request</code></dt>
<dt><span className="craik-fields__type">step input</span></dt>
<dd>Run id · task id · phase (<code>plan</code> / <code>act</code> / <code>observe</code> / <code>evaluate</code> / <code>continue</code> / <code>stop</code>) · runner metadata · policy envelope id · optional intent lock id · capability grant ids · expected output schemas · input prompt · bounded context · redaction requirement.</dd>
</div>

<div>
<dt><code>craik.runner_step_result</code></dt>
<dt><span className="craik-fields__type">step output</span></dt>
<dd>Request id · run id · task id · phase · runner metadata · status · summary · observed output · diagnostics · receipt ids · memory proposal ids · artifacts · redaction state.</dd>
</div>

<div>
<dt><code>craik.runner_capability_matrix</code></dt>
<dt><span className="craik-fields__type">capability profile</span></dt>
<dd>Runner metadata · trust level &amp; boundary · default grant posture · whether receipts and redaction are required · normalized capability entries · policy notes.</dd>
</div>

</div>

### Capability support levels

<div className="craik-fields">

<div>
<dt>Support</dt>
<dt><span className="craik-fields__type">Behavior</span></dt>
<dd>When to use</dd>
</div>

<div>
<dt><code>unsupported</code></dt>
<dt><span className="craik-fields__type">block</span></dt>
<dd>The runner should not be asked to perform the action.</dd>
</div>

<div>
<dt><code>prompt-handoff</code></dt>
<dt><span className="craik-fields__type">review</span></dt>
<dd>The runner can reason about or propose the action, but Craik routes side effects through review.</dd>
</div>

<div>
<dt><code>supported</code></dt>
<dt><span className="craik-fields__type">grant-gated</span></dt>
<dd>The runner can perform the action when policy grants allow it.</dd>
</div>

</div>

Side-effect capabilities default to `grant_required: true`. Read-only
context and structured-result capabilities may be marked grant-free
when the runner profile can consume them without widening authority.

## Adapter interface

Python adapters implement the `RunnerAdapter` protocol.

```python
from craik.runtime.runners import RunnerAdapter


def run_task(adapter: RunnerAdapter, request):
    return adapter.run(request)
```

<div className="craik-keypoint">

**Validate · preserve · normalize.**

Adapters validate the request they receive, preserve runner metadata,
and return a <code>craik.runner_adapter_result</code> payload.
Fixture adapters can use <code>FixtureRunnerAdapter</code> for
deterministic contract tests without live runner credentials.

</div>

## Shipped preview adapters

<div className="craik-grid">

<div><h4><a href="codex-runner-adapter/">Codex</a></h4><p>Codex-compatible prompt handoff and deterministic fixture runs.</p></div>
<div><h4><a href="claude-runner-adapter/">Claude</a></h4><p>Claude-compatible prompt handoff and deterministic fixture runs.</p></div>
<div><h4><a href="gemini-runner-adapter/">Gemini</a></h4><p>Gemini-compatible read/review-oriented prompt handoff and deterministic fixture runs.</p></div>

</div>

## Capability matrix

```sh
craik runners matrix
craik runners matrix --runner codex
```

The v0.1.0 runner profiles are conservative.

<div className="craik-fields">

<div>
<dt>Runner</dt>
<dt><span className="craik-fields__type">Trust</span></dt>
<dd>Posture</dd>
</div>

<div>
<dt><code>codex</code></dt>
<dt><span className="craik-fields__type">medium</span></dt>
<dd>Live local runner. Side effects require explicit grants and receipts.</dd>
</div>

<div>
<dt><code>claude</code></dt>
<dt><span className="craik-fields__type">medium</span></dt>
<dd>Prompt-handoff runner. Side effects return through Craik review and receipt workflows.</dd>
</div>

<div>
<dt><code>gemini</code></dt>
<dt><span className="craik-fields__type">low</span></dt>
<dd>Prompt-handoff runner. Low trust until adapter tests justify broader authority.</dd>
</div>

<div>
<dt><code>fixture</code></dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd>Test runner with no external side effects.</dd>
</div>

</div>

Future prompt compilation and policy decisions consume
`craik.runner_capability_matrix` rather than inferring authority from
a runner name or free-form metadata. The
[prompt compiler](prompt-compiler.md) uses these matrices to include
runner-specific capability notes and policy boundaries in
deterministic prompts.

## Boundaries

<div className="craik-decision">

<div>
<h4>Craik core owns</h4>
<ul>
<li>Task requests</li>
<li>Case files</li>
<li>Policy envelopes</li>
<li>Capability grants</li>
<li>Receipts</li>
<li>Handoffs</li>
<li>Memory proposals</li>
<li>Contract validation</li>
</ul>
</div>

<div>
<h4>Adapters own</h4>
<ul>
<li>Runner invocation or prompt handoff</li>
<li>Runner-specific session details</li>
<li>Runner-specific diagnostics</li>
<li>Mapping runner output back into Craik contracts</li>
</ul>
</div>

</div>

Runner-specific details stay inside the `metadata`, `outputs`, or
`diagnostics` fields unless they become stable cross-runner contract
fields. Adapter-produced receipts and handoff inputs include the
stable [runner metadata](runner-metadata.md) snapshot.

## Provider-backed MVP runner

The MVP provider-backed runner is implemented in
`craik.runtime.provider_runner`. It uses the normal case-file and
prompt compiler flow, then runs deterministic provider-normalized
steps through the governed loop.

**Provider-backed runs must persist:**

<div className="craik-grid">

<div><h4>Compiled prompt</h4></div>
<div><h4>Task run</h4></div>
<div><h4>Normalized run outputs</h4><p>Per executed step.</p></div>
<div><h4>Provider receipts</h4><p>Per model step.</p></div>
<div><h4>Side-effect / denial receipts</h4><p>Emitted by the loop.</p></div>
<div><h4>Handoff</h4><p>For completion · block · failure · interruption.</p></div>

</div>

OpenAI and Anthropic parity is covered by deterministic tests for
`provider_openai` and `provider_anthropic`. **The MVP runner path
does not perform live API calls by default.**

<div className="craik-keypoint">

**Additional live runner adapters are post-MVP.**

Preview adapters may remain useful for prompt handoff, local fixtures,
and contract validation, but they should not be documented as
operational live execution paths until they meet the same
certification, budget, retry, redaction, receipt, and side-effect
requirements as the MVP OpenAI and Anthropic provider paths. See
[Post-MVP Scope](post-mvp-scope.md).

</div>

## What's next

<div className="craik-next">

<a href="runner-metadata/">
<strong>Reference</strong>
<span>Runner metadata</span>
<small>The stable identity snapshot every adapter preserves.</small>
</a>

<a href="../guides/runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>The end-to-end preview path and smoke-test checklist.</small>
</a>

<a href="prompt-compiler/">
<strong>Reference</strong>
<span>Prompt compiler</span>
<small>How matrices flow into compiled prompts.</small>
</a>

</div>
