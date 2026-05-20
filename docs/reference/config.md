# Config reference

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How Craik v0.1.0 is configured — environment variables, the local
home, the setup / doctor / update commands, project-level context
discovery rules, Stigmem and GitHub env vars, and pre-publication
validation.

</div>

<div className="craik-keypoint">

**Env-var-driven, with a structured local home.**

Configuration lives in the environment and in <code>CRAIK_HOME</code>.
Project-local <code>.craik/</code> directories are opt-in only.

</div>

## Local state

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>CRAIK_HOME</code></dt>
<dt><span className="craik-fields__type"><code>~/.craik</code></span></dt>
<dd>Overrides the default state directory.</dd>
</div>

</div>

Craik stores runtime state in a SQLite database under
`CRAIK_HOME/state/`. Project-local `.craik/` directories are opt-in
only and are not created by the current CLI.

## Setup commands

<div className="craik-fields">

<div>
<dt>Command</dt>
<dt><span className="craik-fields__type">Mutates?</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>craik setup</code></dt>
<dt><span className="craik-fields__type">yes</span></dt>
<dd>Creates the local home layout, initializes the local store, writes a default <code>craik.gateway_config</code>. Prints <code>secrets_written = false</code> and does not collect API keys, channel tokens, webhook secrets, or bearer credentials.</dd>
</div>

<div>
<dt><code>craik doctor</code></dt>
<dt><span className="craik-fields__type">no</span></dt>
<dd>Reports pass / warning / failure diagnostics for local home, local store, memory backend, gateway prerequisites, and gateway policy readiness. Does not create files or contact external services.</dd>
</div>

<div>
<dt><code>craik update</code></dt>
<dt><span className="craik-fields__type">no</span></dt>
<dd>Read-only update guidance — installed version, supported Python range, contract compatibility, local-store migration compatibility, manual update steps, and non-mutating boundaries. Does not fetch release metadata, rewrite the install, or migrate local state.</dd>
</div>

</div>

## Context discovery

Project profiles can store documentation discovery overrides through
`craik project add`.

<div className="craik-fields">

<div>
<dt>Option</dt>
<dt><span className="craik-fields__type">Scope</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>--discovery-exclude &lt;glob&gt;</code></dt>
<dt><span className="craik-fields__type">project</span></dt>
<dd>Adds a project-level context exclusion rule.</dd>
</div>

<div>
<dt><code>--discovery-include &lt;glob&gt;</code></dt>
<dt><span className="craik-fields__type">project</span></dt>
<dd>Adds a project-level include rule that can restore a default-excluded path.</dd>
</div>

</div>

`craik case build` accepts the same options as one-off user overrides
for a single case-file build. Craik always starts from conservative
defaults that skip generated, dependency, build, cache, and
archive-heavy paths. The resulting case file records active rules and
skipped paths in `context_budget`.

## Stigmem

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_URL</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Base URL for the Stigmem node.</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_API_KEY</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Bearer token for authenticated Stigmem nodes.</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_TIMEOUT</code></dt>
<dt><span className="craik-fields__type"><code>5.0</code></span></dt>
<dd>Request timeout in seconds.</dd>
</div>

</div>

<div className="craik-keypoint">

**Never commit API keys.**

Craik redacts token-shaped values from persisted payloads and command
output, but the discipline starts with you.

</div>

## GitHub

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_TOKEN</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Preferred bearer token for GitHub API reads.</dd>
</div>

<div>
<dt><code>GITHUB_TOKEN</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Fallback bearer token.</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_API_URL</code></dt>
<dt><span className="craik-fields__type"><code>https://api.github.com</code></span></dt>
<dd>GitHub API base URL.</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_TIMEOUT</code></dt>
<dt><span className="craik-fields__type"><code>5.0</code></span></dt>
<dd>Request timeout in seconds.</dd>
</div>

</div>

The GitHub adapter is **read-only in v0.1.0**.

## Validation

Run before publishing changes:

```sh
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev craik policy test
```

## What's next

<div className="craik-next">

<a href="cli/">
<strong>Reference</strong>
<span>CLI</span>
<small>The auto-generated command reference.</small>
</a>

<a href="../guides/configuring-craik-home/">
<strong>Guide</strong>
<span>Configuring Craik home</span>
<small>Relocation rules, multi-host shares, and CI conventions.</small>
</a>

<a href="../guides/development/">
<strong>Guide</strong>
<span>Development checks</span>
<small>Pre-publication validation in detail.</small>
</a>

</div>
