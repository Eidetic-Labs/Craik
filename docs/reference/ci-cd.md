# CI/CD Gates

Craik CI is split by surface so failures point at the area that regressed.

## Pull Request Gates

| Gate | Purpose |
| --- | --- |
| `lint` | Ruff import, style, and modernization checks. |
| `type` | Strict mypy checks for the `craik` package. |
| `unit` | Full pytest suite with coverage XML and JUnit artifacts. |
| `contract` | Runtime contract fixture conformance and report generation. |
| `integration` | Recorded provider integration tests that do not require live credentials. |
| `security` | Dependency audit, static analysis, policy baseline, release readiness, and public documentation hygiene. |
| `CodeQL` | GitHub code scanning for Python on pull requests and pushes to `main`. |
| `docs` | Generated CLI docs, docs hygiene, and Docusaurus build. |
| `package` | Source distribution and wheel build, metadata validation, smoke install. |

## Coverage Ratchet

Coverage is configured in `pyproject.toml` and currently fails below 75 percent
line coverage. The threshold is intentionally conservative for the MVP ramp. It
should only move upward after CI has been green at the higher threshold on
`main`.

Coverage artifacts are uploaded from the `unit` job:

- `reports/tests/unit.xml`;
- `reports/coverage/coverage.xml`.

## Conformance Reports

The contract job validates every registered runtime schema against the pinned
fixture bundle and writes:

- `reports/conformance/contracts.json`;
- `reports/conformance/contracts.md`.

These reports are uploaded as CI artifacts and are also produced by the nightly
reliability workflow.

## Provider Integration

The `integration` job runs recorded provider integration tests with
`pytest -m "integration and not live" tests/integration`. These tests exercise
live-shaped provider payloads through cassettes so pull requests can validate
provider wiring without requiring paid API keys, localhost model servers, or
secret material in CI.

Optional live provider checks stay gated behind explicit environment flags such
as `CRAIK_RUN_LIVE_TESTS=1` and are not part of the default pull request gate.

## Code Scanning

The repo-owned CodeQL workflow runs Python analysis on pull requests and pushes
to `main`, using the default query suite with `build-mode: none`. The analyze
step uses its default SARIF upload behavior, so results are published to GitHub
Security -> Code scanning when repository code-scanning configuration permits
advanced workflow uploads.

## Dependency Audit

The `security` job exports `uv.lock` to a hash-pinned requirements file and
runs `pip-audit` against that locked dependency set. The audit runs in
pip-free mode so CI checks the committed lock state without resolving a new
dependency graph.

## Static Analysis

The `security` job runs Bandit against `src/craik` with an explicit baseline
for accepted findings. New findings fail the job and should either be fixed or
added to the baseline only with a reviewable rationale.

## Changed-File Strictness

`scripts/check_changed_file_strictness.py` enforces minimum review discipline:

- package source changes require tests;
- contract model changes require contract test coverage;
- workflow-only changes require a docs or scripts rationale change.

This is not a substitute for review. It is a low-friction guard against
high-risk changes landing without visible verification.

## Nightly Reliability

The nightly workflow runs the full quality, coverage, conformance, security,
docs, and package checks on `main` and uploads test, coverage, conformance,
docs, and package artifacts.
