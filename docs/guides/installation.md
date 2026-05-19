# Installation

<p className="craik-meta"><span>3 min read</span><span>For everyone</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Install the Craik CLI on a workstation or CI runner, verify it runs, and
prepare the local state directory. After this guide you'll have `craik` on
your PATH and `~/.craik` ready to hold projects, receipts, handoffs, and
case files.

</div>

## 1 · Check your prerequisites

Craik is a Python CLI. You need a recent Python interpreter and a way to put
the CLI on your PATH.

<div className="craik-grid">

<div>
<h4><code>Python ≥ 3.12</code></h4>
<p>3.12, 3.13, or 3.14. Verify with <code>python3 --version</code>.</p>
</div>

<div>
<h4><code>pip</code> or <code>pipx</code></h4>
<p><code>pipx</code> is recommended for an isolated CLI install; <code>pip</code> works for project-local installs.</p>
</div>

<div>
<h4>Git <em>(optional but expected)</em></h4>
<p>Craik registers Git repositories as projects. Without Git you can still install Craik but the project workflows will be limited.</p>
</div>

</div>

If `python3 --version` reports `3.11.x` or older, install a newer interpreter
first — `pyenv`, `uv python install 3.12`, `brew install python@3.12`, or
your distro package manager all work.

## 2 · Pick an install method

<div className="craik-decision">

<div>
<h4>Use <code>pipx</code> (recommended)</h4>
<ul>
<li>You want a standalone <code>craik</code> command available everywhere.</li>
<li>You don't want Craik mixed into a project's virtualenv.</li>
<li>You'll keep one global version and upgrade with <code>pipx upgrade</code>.</li>
</ul>
</div>

<div>
<h4>Use <code>pip</code> in a venv</h4>
<ul>
<li>You're integrating Craik into a project's own Python environment.</li>
<li>You're packaging Craik into a CI image with pinned dependencies.</li>
<li>You're a contributor working from a local checkout.</li>
</ul>
</div>

</div>

### Install with pipx

```bash title="Install Craik as an isolated CLI"
pipx install craik
craik --version
```

If `pipx` isn't on your machine yet:

```bash title="Install pipx, then Craik"
python3 -m pip install --user pipx
python3 -m pipx ensurepath
# Open a new shell, then:
pipx install craik
```

### Install with pip

```bash title="Install into the current Python environment"
python3 -m pip install craik
craik --version
```

### Install from a local checkout (contributors)

```bash title="Editable install with dev extras"
git clone https://github.com/eidetic-labs/craik.git
cd craik
python3 -m pip install -e ".[dev]"
craik --version
```

For reproducible source-tree commands, [`uv`](https://docs.astral.sh/uv/) is
fully supported:

```bash title="Source-tree commands with uv"
uv run --python 3.12 --extra dev craik --version
```

## 3 · Verify the install

```bash title="Confirm the CLI is on your PATH and responsive"
craik --version
craik --help
```

You should see a semantic version (for example, `0.1.x`) and the subcommand
list. If `craik` is not found, `pipx ensurepath` (or activating your venv)
usually resolves it.

## 4 · Initialize local state

Craik stores project state, receipts, handoffs, and case files under a single
home directory:

<div className="craik-cmd">
<code>craik home init</code>
<p>Creates <code>~/.craik/</code> and the per-data-class subdirectories Craik writes to during a run.</p>
</div>

If you want Craik to store state somewhere else, point `CRAIK_HOME` at any
directory you control before running anything:

```bash title="Use a custom CRAIK_HOME"
export CRAIK_HOME="$HOME/work/craik-home"
craik home init
```

The Craik home layout looks like this once initialized:

```text
~/.craik/
  config/      # user-level config and credential profile definitions
  secrets/     # secret material (never committed)
  state/       # SQLite store: projects, tasks, receipts, handoffs, case files
  cache/       # short-lived caches
  logs/        # diagnostic logs
  receipts/    # exported receipts
  handoffs/    # exported handoffs
  case-files/  # exported case files
  projects/    # per-project artifacts and exports
```

See [Configuring Craik home](configuring-craik-home.md) for relocation rules,
multi-host shares, and CI conventions.

## 5 · (Optional) Authenticate as an operator

Fixture-backed provider execution works without any credentials, so you can
explore Craik end-to-end before connecting a real model. When you're ready for
live provider calls:

```bash title="Operator identity + first credential profile"
craik login
craik auth add anthropic:work --kind=api-key --env-var=ANTHROPIC_API_KEY
craik auth status
```

The full reference — OIDC device-code and loopback flows, credential pools,
workload identity, secret-manager integrations — lives in
[Authentication and credentials](authentication.md).

:::tip
The "live providers cost money" reflex is correct. Craik never makes a live
provider call without you opting in: you supply provider metadata, the policy
envelope must allow live access, and a credential profile must be bound to
the run. Until you do all three, the fixture path is what runs.
:::

## Troubleshooting

<div className="craik-grid">

<div>
<h4><code>craik: command not found</code></h4>
<p>Run <code>pipx ensurepath</code> and open a new shell. If you used <code>pip</code>, confirm the install location with <code>python3 -m pip show -f craik</code> and add the script directory to <code>PATH</code>.</p>
</div>

<div>
<h4><code>Python 3.11 is too old</code></h4>
<p>Install a 3.12+ interpreter and re-run the install. With <code>pipx</code>: <code>pipx install --python python3.12 craik</code>.</p>
</div>

<div>
<h4><code>ModuleNotFoundError: craik</code></h4>
<p>You're likely in the wrong venv. Activate the environment where you installed Craik or run via the absolute install path.</p>
</div>

<div>
<h4>Behind a proxy / offline mirror</h4>
<p>Pip and pipx both honor <code>PIP_INDEX_URL</code>. For air-gapped installs, pre-build a wheel with <code>pip wheel craik</code> on a connected host and copy.</p>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../quickstart/">
<strong>Step 2</strong>
<span>Quickstart</span>
<small>Register a project, build a case file, run a governed task.</small>
</a>

<a href="../setup/">
<strong>Step 3</strong>
<span>Run the setup wizard</span>
<small>An interactive walkthrough that wires together home, identity, and a first project.</small>
</a>

<a href="../../concepts/project-model/">
<strong>Concept</strong>
<span>Read the runtime model</span>
<small>Understand the typed objects Craik composes — project, case file, receipt, handoff.</small>
</a>

</div>
