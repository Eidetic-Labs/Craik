# CI/CD gates

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The split CI surface — pull-request gates, coverage ratchet, conformance
reports, provider integration, code scanning, dependency audit, static
analysis, changed-file strictness, and nightly reliability.

</div>

<div className="craik-keypoint">

**Surface-split so failures point.**

Craik CI is split by surface so failures point at the area that
regressed.

</div>

## Pull request gates

| Gate | Purpose |
| --- | --- |
| `lint` | Ruff import, style, and modernization checks. |
| `type` | Strict mypy checks for the `craik` package. |
| `unit` | Full pytest suite with coverage XML and JUnit artifacts. |
| `contract` | Runtime contract fixture conformance and report generation. |
| `integration` | Recorded provider integration tests that do not require live credentials. |
| `security` | Dependency audit, static analysis, policy baseline, release readiness, public docs hygiene. |
| `CodeQL` | GitHub code scanning for Python on PRs and pushes to `main`. |
| `docs` | Generated CLI docs, docs hygiene, Docusaurus build. |
| `package` | Source distribution and wheel build, metadata validation, smoke install. |

## Coverage ratchet

<div className="craik-keypoint">

**Currently 75% line coverage.**

Configured in <code>pyproject.toml</code>. Conservative for the MVP
ramp — only moves upward after CI has been green at the higher
threshold on <code>main</code>.

</div>

Coverage artifacts uploaded from the `unit` job:

<div className="craik-grid">

<div><h4><code>reports/tests/unit.xml</code></h4></div>
<div><h4><code>reports/coverage/coverage.xml</code></h4></div>

</div>

## Conformance reports

The contract job validates every registered runtime schema against the
pinned fixture bundle and writes:

<div className="craik-grid">

<div><h4><code>reports/conformance/contracts.json</code></h4></div>
<div><h4><code>reports/conformance/contracts.md</code></h4></div>

</div>

These reports are uploaded as CI artifacts and also produced by the
nightly reliability workflow.

## Provider integration

<div className="craik-keypoint">

**Cassettes, not live credentials.**

The <code>integration</code> job runs
<code>pytest -m "integration and not live" tests/integration</code>.
Live-shaped payloads pass through cassettes so PRs validate provider
wiring without paid API keys or secrets in CI.

</div>

Optional live provider checks stay gated behind explicit env flags
such as `CRAIK_RUN_LIVE_TESTS=1` and are not part of the default PR
gate.

## Code scanning

The repo-owned CodeQL workflow runs Python analysis on pull requests
and pushes to `main`, using the default query suite with
`build-mode: none`. The analyze step uses its default SARIF upload
behavior; results publish to GitHub Security → Code scanning when
repository code-scanning configuration permits advanced workflow
uploads.

## Dependency audit

The `security` job exports `uv.lock` to a hash-pinned requirements
file and runs `pip-audit` against that locked set. The audit runs in
pip-free mode so CI checks the committed lock state without resolving
a new dependency graph.

## Static analysis

<div className="craik-decision">

<div>
<h4>Bandit</h4>
<p>Runs against <code>src/craik</code> with an explicit baseline for accepted findings. New findings fail the job and should either be fixed or added to the baseline only with a reviewable rationale.</p>
</div>

<div>
<h4>Gitleaks</h4>
<p>Runs against the checked-out tree with repo-local <code>.gitleaks.toml</code>. The configuration extends the default rules and only allowlists generated documentation dependency trees plus intentionally fake test credential fixtures.</p>
</div>

</div>

## Changed-file strictness

`scripts/check_changed_file_strictness.py` enforces minimum review
discipline.

<div className="craik-grid">

<div><h4>Package source changes</h4><p>Require tests.</p></div>
<div><h4>Contract model changes</h4><p>Require contract test coverage.</p></div>
<div><h4>Workflow-only changes</h4><p>Require a docs or scripts rationale change.</p></div>

</div>

<div className="craik-keypoint">

**Guard, not substitute.**

This is a low-friction guard against high-risk changes landing without
visible verification — not a substitute for review.

</div>

## Nightly reliability

The nightly workflow runs the full quality, coverage, conformance,
security, docs, and package checks on `main` and uploads all artifacts.

## What's next

<div className="craik-next">

<a href="../../guides/development/">
<strong>Guide</strong>
<span>Development checks</span>
<small>The local equivalent operators run.</small>
</a>

<a href="../../release-readiness/">
<strong>Read</strong>
<span>Release readiness</span>
<small>The validation gates these CI jobs enforce.</small>
</a>

<a href="../policy-tests/">
<strong>Reference</strong>
<span>Policy tests</span>
<small>The regression gate that runs inside <code>security</code>.</small>
</a>

</div>
