# Development Checks

<p className="craik-meta"><span>4 min read</span><span>For contributors</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Run the same quality gates locally that Craik runs in CI on every pull
request and push to `main`. By the end you'll have a tight inner loop:
tests, linting, type-checking, and the policy contract — all reproducible.

</div>

## Prerequisites

- Python 3.12 or newer (`python3 --version`).
- A local checkout of the Craik repo with the `dev` extras installed.
- [`uv`](https://docs.astral.sh/uv/) recommended (but not required) for
  reproducible, hermetic command runs.

```bash title="One-time setup"
git clone https://github.com/eidetic-labs/craik.git
cd craik
python3 -m pip install -e ".[dev]"
```

## The four core gates

<div className="craik-grid">

<div>
<h4><code>pytest</code></h4>
<p>Unit, contract, and integration tests. Covers runtime contracts, case-file assembly, policy gates, receipt redaction, handoff structure, and provider adapters.</p>
</div>

<div>
<h4><code>ruff check</code></h4>
<p>Lints style, imports, and a curated set of correctness rules. Runs in under a second on the full repo.</p>
</div>

<div>
<h4><code>mypy</code></h4>
<p>Strict type-checking. Craik runtime contracts are Pydantic models — keep them honest.</p>
</div>

<div>
<h4><code>craik policy test</code></h4>
<p>Exercises the policy contract: strict defaults, immutable path behavior, memory proposal defaults, fail-open receipts, automation fail-closed behavior, and redaction.</p>
</div>

</div>

## Run them with `uv` (recommended)

`uv run` resolves a per-invocation Python environment, so the command runs
the same way locally as in CI.

```bash title="The full pre-PR sweep"
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
uv run --python 3.12 --extra dev craik policy test
```

## Run them with the venv you already have

If you installed the dev extras into a virtual environment, just call the
tools directly:

```bash title="From an activated venv"
pytest
ruff check .
mypy
craik policy test
```

## Useful narrower runs

<div className="craik-cmd">
<code>pytest -k case_file</code>
<p>Run only the case-file-related tests.</p>
</div>

<div className="craik-cmd">
<code>pytest tests/test_docs.py -x</code>
<p>Run just the docs tests (link resolution, required coverage). Stops on first failure.</p>
</div>

<div className="craik-cmd">
<code>ruff check src/craik/runtime</code>
<p>Lint just one subtree — useful when iterating on a module.</p>
</div>

<div className="craik-cmd">
<code>mypy src/craik/policy</code>
<p>Type-check one package at a time.</p>
</div>

## What CI runs

The CI workflow (`.github/workflows/ci.yml`) runs the same four gates plus
a quickstart smoke test (`python scripts/quickstart_smoke.py`) and the
Docusaurus build (`docs/`). If your local sweep is green, the chances of
CI surprising you on a vanilla change are low.

## What to do when a gate fails

<div className="craik-decision">

<div>
<h4>Tests failing</h4>
<ul>
<li>Re-run with <code>pytest -x -vvv</code> to stop at first failure with full output.</li>
<li>Use <code>pytest --lf</code> after a fix to re-run only the last failures.</li>
<li>Snapshot mismatches in contract tests usually mean a schema changed — update the matching fixture deliberately.</li>
</ul>
</div>

<div>
<h4>Lint / type failing</h4>
<ul>
<li><code>ruff check . --fix</code> handles the autofixable cases.</li>
<li><code>mypy</code> errors that look mysterious are almost always a missing or wrong type hint on a runtime contract — start there.</li>
<li>Don't disable a rule to make CI green without a comment justifying why.</li>
</ul>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../doctor/">
<strong>Diagnose</strong>
<span>Run doctor</span>
<small>Health-check identity, credentials, and provider posture without firing a real run.</small>
</a>

<a href="../release-management/">
<strong>Operate</strong>
<span>Release management</span>
<small>How releases are cut, signed, and gated for v0.x.</small>
</a>

<a href="../../reference/policy-tests/">
<strong>Reference</strong>
<span>Policy tests</span>
<small>What <code>craik policy test</code> actually checks and how to extend it.</small>
</a>

</div>
