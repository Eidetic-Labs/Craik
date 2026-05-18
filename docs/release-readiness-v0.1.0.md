# v0.1.0 Release Readiness Validation

Validated on 2026-05-17 against `main` at
`bf29513d6ba65a8640050fbaa27cda2d6bf398b1`.

## Summary

Repository-owned readiness checks are complete. The remaining work is outside
the repository: create the `v0.1.0` tag and run the protected publication
process when the maintainer is ready.

## Code Health

- ✅ CI on `main` is green. The latest `ci.yml` run on `main` completed with
  `success`: [run 26010629626](https://github.com/eidetic-labs/craik/actions/runs/26010629626).
- ✅ CodeQL is green. The latest `codeql.yml` run on `main` completed with
  `success`: [run 26010629612](https://github.com/eidetic-labs/craik/actions/runs/26010629612).
- ✅ Code scanning has zero open alerts:
  `gh api repos/eidetic-labs/craik/code-scanning/alerts`.
- ✅ Version is consistent:
  `uv run python scripts/check_release_version.py`.
- ✅ File-size budget is enforced:
  `find src -name "*.py" -print0 | xargs -0 uv run python scripts/check_max_file_lines.py`.
- ✅ `craik --version` prints `0.1.0`:
  `uv run craik --version`.
- ✅ `craik doctor` runs to completion against a fresh initialized home:
  `CRAIK_HOME=<temporary-craik-home> uv run craik setup`
  followed by
  `CRAIK_HOME=<temporary-craik-home> uv run craik doctor`.
  An entirely empty home correctly reports missing local state rather than
  pretending it is healthy.
- ✅ Package artifacts build:
  `uv build` produced `dist/craik-0.1.0.tar.gz` and
  `dist/craik-0.1.0-py3-none-any.whl`.

## Test Coverage

- ✅ HTTP transport integration test is present and exercised:
  `tests/integration/test_http_transport_round_trip.py`.
- ✅ Credential source tests exist for env-var API keys, local-CLI OAuth,
  CLI bridge, secret references, Stigmem references, marker/no-credential
  behavior, and credential pools:
  `tests/test_auth_api_key_source.py`,
  `tests/test_auth_local_cli_oauth.py`,
  `tests/test_auth_cli_bridge.py`,
  `tests/test_auth_secret_ref.py`,
  `tests/test_auth_profiles.py`,
  `tests/test_auth_credential_pool.py`, and
  `tests/test_provider_runtime.py`.
- ✅ OIDC and workload identity tests exist for operator authentication,
  session storage, GitHub Actions, Kubernetes, generic file/env-var tokens, and
  RFC 8693 token exchange:
  `tests/test_oidc_operator.py`, `tests/test_operator_session_store.py`,
  `tests/test_workload_identity.py`, and
  `tests/test_oidc_exchange_secret_manager.py`.
- ✅ JWT validation rejects `alg=none`, unknown `kid`, tampered payloads, and
  asymmetric/symmetric algorithm confusion in `tests/test_oidc_operator.py`.
- ✅ Governance behavior tests exist for credential-scoped receipts,
  operator-scoped receipts, policy-bound credentials, policy-bound operators,
  approval gates, expiry-as-risk, per-credential redaction, and handoff identity
  isolation:
  `tests/test_provider_runtime.py`, `tests/test_policy.py`,
  `tests/test_loop.py`, `tests/test_case_files.py`,
  `tests/test_redaction.py`, and `tests/test_handoffs.py`.
- ✅ Focused readiness test set passed:
  `uv run pytest tests/integration/test_http_transport_round_trip.py tests/test_auth_api_key_source.py tests/test_auth_local_cli_oauth.py tests/test_auth_cli_bridge.py tests/test_auth_secret_ref.py tests/test_auth_profiles.py tests/test_auth_credential_pool.py tests/test_oidc_operator.py tests/test_operator_session_store.py tests/test_workload_identity.py tests/test_oidc_exchange_secret_manager.py tests/test_provider_runtime.py tests/test_policy.py tests/test_case_files.py tests/test_handoffs.py -q`.

## Security Hygiene

- ✅ No raw secret patterns were found in tests or scripts:
  `grep -rE "sk-[a-zA-Z0-9]{20,}|xoxb-|ghp_|ANTHROPIC.{0,5}=.{20,}" tests/ scripts/`.
- ✅ Operator session file permissions are enforced in
  `src/craik/runtime/auth/operator/store.py` with owner-only `0o600` writes.
- ✅ `auth-profiles.json` writes are file-locked and atomic in
  `src/craik/runtime/auth/store.py` using `fcntl.flock`, temporary files, and
  `os.replace`.
- ✅ Credential pool writes are file-locked and atomic in
  `src/craik/runtime/auth/pool.py`.
- ✅ Secret resolver and credential-source errors avoid including resolved
  secret values; error strings use reference-level wording such as
  `secret reference could not be resolved`.

## Documentation

- ✅ The roadmap has exactly 12 release gates, `v0.1.0` through `v0.12.0`,
  with no gaps.
- ✅ `docs/roadmap.md` states that `v0.1.0` includes OIDC, pluggable
  credentials, operator and credential identity on receipts, policy-bound auth,
  approval-gated first use, credential expiry risks, per-credential redaction,
  and handoff identity bookkeeping.
- ✅ `CHANGELOG.md` `## 0.1.0 - 2026-05-17` narrates Phase A and Phase B work.
- ✅ `README.md` "What Works Today" names OIDC and typed credential profiles.
- ✅ `docs/guides/authentication.md` exists and is linked from
  `docs/index.md`.
- ✅ `docs/guides/quickstart.md` includes the authentication on-ramp.
- ✅ `docs/limitations.md` no longer describes auth-related shipped
  capabilities as future work.
- ✅ `docs/mvp.md` and `docs/mvp-roadmap.md` reflect the expanded `v0.1.0`
  scope, including operator authentication and credential profiles.
- ✅ Docusaurus docs build succeeds:
  `npm run build` from `docs/`.

## Operational State

- ✅ GitHub milestones exist for `v0.1.0` through `v0.12.0` with titles matching
  the roadmap.
- ✅ The `v0.1.0 - Governed Agent-Runtime Substrate` milestone has 22 closed
  issues and 0 open issues.
- ✅ No open PRs or open issues are currently blocking the release.
- ✅ Dependabot alert #1 is fixed.
- ✅ Tag `v0.1.0` does not exist locally. Tagging remains a maintainer release
  action and should happen only after this readiness report is accepted.

## External Release Actions

- ⏳ Create and push tag `v0.1.0`.
- ⏳ Run the protected package publication workflow.
- ⏳ Optional live-provider smoke tests require real provider credentials and an
  operator IdP; fixture, cassette, and in-process socket paths are already
  validated in-repo.
