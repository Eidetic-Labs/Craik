# Project Registry

<p className="craik-meta"><span>5 min read</span><span>For first-time operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Register Git repositories as Craik *projects* so the runtime can build
case files from them. By the end, you'll have one or more projects in
the local registry, with mutable doc roots and immutable evidence paths
configured.

</div>

<div className="craik-keypoint">

**Project**

A Git repository registered into Craik's local store, with its docs
boundaries, immutable evidence paths, and (optionally) memory backend
configuration declared. Projects are the substrate every task, case file,
and handoff hangs off.

</div>

## Where the registry lives

Project records persist in the local SQLite store at
`$CRAIK_HOME/state/craik.sqlite`. Registration writes **only** to Craik's
home — it never creates a `.craik/` directory inside your repository, and
it doesn't modify Git config.

## Register a project

The shortest form takes a path and infers everything else:

```bash title="Register the current directory"
craik project add .
```

For anything more than a one-off, declare the docs boundaries explicitly so
case files and onboarding payloads carry the right shape:

```bash title="Register with explicit boundaries"
craik project add /path/to/repo \
  --name stigmem \
  --docs-path README.md \
  --docs-path docs/ \
  --immutable-path docs/adr/
```

<div className="craik-fields">

<div>
<dt>Flag</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>--name</code></dt>
<dt><span className="craik-fields__type">string</span></dt>
<dd>Stable name used in CLI lookups and case files. Defaults to the repo directory name.</dd>
</div>

<div>
<dt><code>--docs-path</code></dt>
<dt><span className="craik-fields__type">path (repeatable)</span></dt>
<dd>Mutable documentation roots an agent may edit under policy.</dd>
</div>

<div>
<dt><code>--immutable-path</code></dt>
<dt><span className="craik-fields__type">path (repeatable)</span></dt>
<dd>Evidence paths that should never be normal edit targets — ADRs, decisions, frozen specs.</dd>
</div>

</div>

The mutable/immutable distinction is load-bearing. It's how Craik prevents
a "fix the docs" agent from quietly overwriting an ADR.

## Inspect what got registered

<div className="craik-cmd">
<code>craik project list</code>
<p>Show every registered project with its id, name, and Git head.</p>
</div>

<div className="craik-cmd">
<code>craik project show stigmem</code>
<p>Print the full <code>project_profile</code> JSON — boundaries, paths, memory backend status, validation commands.</p>
</div>

<div className="craik-cmd">
<code>craik onboard --project stigmem</code>
<p>Print what an agent sees on first contact: project profile, policy, recent handoffs, open contradictions, allowed next actions.</p>
</div>

## What gets detected automatically

If you skip explicit flags, Craik scans the repo and recognizes conventional
roots:

<div className="craik-grid">

<div>
<h4>Mutable docs</h4>
<p><code>README.md</code>, files under <code>docs/</code>, and anything else matching the project's declared doc roots.</p>
</div>

<div>
<h4>Immutable evidence</h4>
<p><code>docs/adr/</code> by convention. Add others (<code>specs/</code>, <code>rfcs/</code>, etc.) with <code>--immutable-path</code>.</p>
</div>

<div>
<h4>Validation commands</h4>
<p>Inferred from the project's configured policy posture. Augment them by adding to <code>project.profile</code> in a later step.</p>
</div>

<div>
<h4>Memory backend</h4>
<p>Detected from <code>CRAIK_MEMORY_BACKEND</code> and per-project config. Status is reported by <code>craik onboard</code> without printing credentials.</p>
</div>

</div>

## A multi-project workspace

You can register multiple projects under the same `CRAIK_HOME`. They live
in the same registry and reference the same operator identity but have
independent policy posture and validation commands.

```bash title="Register two projects"
craik project add /work/app --name app
craik project add /work/docs --name docs
craik project list
```

Tasks, case files, receipts, and handoffs are always scoped by project —
nothing leaks across.

## Unregister a project

```bash title="Remove from the registry"
craik project remove stigmem
```

This removes the project record and unbinds its tasks. **It does not
delete receipts or handoffs that already reference the project** — those
stay queryable for audit.

## What's next

<div className="craik-next">

<a href="../quickstart/">
<strong>Do</strong>
<span>Quickstart</span>
<small>Take a freshly registered project and walk it through a full governed task.</small>
</a>

<a href="../../concepts/project-model/">
<strong>Read</strong>
<span>The project model</span>
<small>The typed object Craik builds from a registered repository.</small>
</a>

<a href="../using-case-files/">
<strong>Do</strong>
<span>Use case files</span>
<small>Patterns for assembling, inspecting, and refreshing the per-task case file.</small>
</a>

</div>
