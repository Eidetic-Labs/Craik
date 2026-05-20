# Project profile

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.project_profile` schema — the project record Craik
registers and later reasons about, plus path detection and immutable
path rules.

</div>

<div className="craik-keypoint">

**Schema: <code>craik.project_profile</code>.**

</div>

## Important fields

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Purpose</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>id</code></dt>
<dt><span className="craik-fields__type">identity</span></dt>
<dd>Stable project id derived from the project name.</dd>
</div>

<div>
<dt><code>name</code></dt>
<dt><span className="craik-fields__type">identity</span></dt>
<dd>Human-readable project name.</dd>
</div>

<div>
<dt><code>repo.local_path</code></dt>
<dt><span className="craik-fields__type">repo</span></dt>
<dd>Absolute path to the Git repository root.</dd>
</div>

<div>
<dt><code>repo.remote</code></dt>
<dt><span className="craik-fields__type">repo</span></dt>
<dd><code>origin</code> remote URL when configured.</dd>
</div>

<div>
<dt><code>repo.default_branch</code></dt>
<dt><span className="craik-fields__type">repo</span></dt>
<dd>Detected default branch.</dd>
</div>

<div>
<dt><code>docs.paths</code></dt>
<dt><span className="craik-fields__type">discovery</span></dt>
<dd>Documentation paths Craik should inspect.</dd>
</div>

<div>
<dt><code>docs.immutable_paths</code></dt>
<dt><span className="craik-fields__type">policy</span></dt>
<dd>Paths that should not be edited by normal workflows.</dd>
</div>

<div>
<dt><code>memory.backend</code></dt>
<dt><span className="craik-fields__type">memory</span></dt>
<dd>Default memory backend for the project.</dd>
</div>

<div>
<dt><code>memory.scope</code></dt>
<dt><span className="craik-fields__type">memory</span></dt>
<dd>Default memory scope for the project.</dd>
</div>

</div>

## Git detection

<div className="craik-keypoint">

**Default branch heuristic.**

<code>craik project add</code> accepts any path inside a Git
repository and stores the repository root. Default branch detection
prefers <code>origin/HEAD</code>, then the current branch, then
<code>main</code>.

</div>

## Default paths

<div className="craik-fields">

<div>
<dt>Kind</dt>
<dt><span className="craik-fields__type">Default detected</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Documentation paths</dt>
<dt><span className="craik-fields__type">conventional</span></dt>
<dd><code>README.md</code> · <code>docs/</code>.</dd>
</div>

<div>
<dt>Immutable paths</dt>
<dt><span className="craik-fields__type">ADR conventions</span></dt>
<dd><code>docs/adr/</code> · <code>docs/adrs/</code>.</dd>
</div>

</div>

## Immutable paths

<div className="craik-keypoint">

**Denied by default.**

Immutable paths are policy inputs for later write protection. Writes
require explicit approval metadata and a matching immutable-write
capability grant.

</div>

Register them explicitly when a project uses a non-standard
decision-record path:

```sh
craik project add /path/to/repo --immutable-path architecture/decisions/
```

## What's next

<div className="craik-next">

<a href="../../guides/project-registry/">
<strong>Guide</strong>
<span>Project registry</span>
<small>How operators add and list projects.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>project_profile</code> shape in the schema catalog.</small>
</a>

<a href="../policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The profiles that consume immutable-path metadata.</small>
</a>

</div>
