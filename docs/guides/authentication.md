# Authentication and Credentials

Craik separates operator identity from credential identity. The operator is the
human or automation identity driving a run. The credential is the provider
account used for model calls. Provider receipts record both so audit can answer
"who authorized this" and "which credential carried it out" without inspecting
secret material.

## Operator Login

Use OIDC login when a policy requires an authenticated operator:

```sh
export CRAIK_OIDC_ISSUER=https://idp.example.com
export CRAIK_OIDC_CLIENT_ID=craik-cli
craik login
craik whoami
```

`craik login` starts the CLI device-code flow, prints the verification URL and
user code, validates the returned ID token against the issuer JWKS, and stores
the session at `<CRAIK_HOME>/operator-session.json` with owner-only
permissions. The lower-level OIDC authenticator also supports loopback + PKCE
for IdPs and entrypoints that are configured to use a browser redirect.

End the local session with:

```sh
craik logout
```

Logout removes the session file and attempts refresh-token revocation when the
issuer exposes a revocation endpoint.

## Credential Profiles

Credential profiles live in `<CRAIK_HOME>/auth-profiles.json` and use
`<provider_family>:<name>` IDs such as `anthropic:work` or
`chat_completions:local`. Profile metadata is masked in CLI output.

### Env-Var API Key

Use an environment variable for the simplest live provider setup:

```sh
export ANTHROPIC_API_KEY=...
craik auth add anthropic:work --kind=api-key --env-var=ANTHROPIC_API_KEY
craik auth test anthropic:work
```

Anthropic profiles send `x-api-key`. OpenAI and OpenAI-compatible
Chat Completions profiles send `Authorization: Bearer`.

### Local-CLI OAuth Fallback

Claude Code users can reuse the local CLI credential file:

```sh
craik auth add anthropic:claude-code --kind=oauth-token --source=local-cli
```

The default path is `~/.claude/.credentials.json`; override it when needed:

```sh
craik auth add anthropic:claude-code \
  --kind=oauth-token \
  --source=local-cli \
  --credentials-path ~/.claude/.credentials.json \
  --refresh-endpoint https://idp.example.com/oauth/token
```

Subscription OAuth tokens may route to a different billing pool than API-key
provider calls. Receipts name the auth profile so operators can distinguish the
credential path used by a run.

### Vendor CLI Bridge

`cli-bridge` profiles are for vendor tools that mint a token through a
subprocess or maintain a credentials file. The runtime supports `stdout_json`,
`stdout_line`, and `credentials_file` extractors. Today these profiles are
created by writing profile metadata into `auth-profiles.json`; the CLI does not
yet expose dedicated bridge flags.

### External Secret Manager

`secret-ref` profiles resolve provider credentials through a secret manager. The
built-in managers treat the ref as an environment variable name or a local file
path. Custom managers can implement the same resolver protocol for Vault, AWS
Secrets Manager, cloud KMS brokers, or internal secret services.

### Stigmem-Backed Credentials

`stigmem-ref` profiles resolve credential material from a Stigmem fact, normally
using relation `craik:credential:value`. The profile metadata includes the node
URL, entity, optional API key, scope, relation, and timeout. This supports
team-shared credentials with Stigmem provenance and revocation semantics. See
[Connecting Stigmem](connecting-stigmem.md) for node configuration.

### Marker Profiles

Marker credential identity is used when a provider path intentionally needs no
secret, such as a local OpenAI-compatible server. The provider receipt records a
`<provider_family>:no-credential` marker instead of a secret-bearing profile.

## Credential Pool

Use a credential pool when a provider has multiple usable accounts and the run
should rotate or fail over between them. Pools are stored in
`<CRAIK_HOME>/credential_pool.json` and support `round_robin`, `failover`, and
`weighted` strategies with per-profile health tracking. The current CLI exposes
profile operations; pool configuration is file-backed/runtime configuration.

## Approval Flow

The first live use of an auth profile is approval-gated. When a run pauses with
a credential approval request, approve the profile for that run:

```sh
craik auth approve anthropic:work --run=run_123
```

The approval is recorded as a receipt. Operator-to-profile authorization grants
are also receipted:

```sh
craik auth grant anthropic:work --to-group=prod-deploy
craik auth grant anthropic:work --to-subject=operator-subject-123
```

## Workload Identity

Workload identity lets CI or cloud platforms mint short-lived credentials
without storing long-lived provider secrets.

GitHub Actions uses the standard Actions OIDC environment:

```sh
ACTIONS_ID_TOKEN_REQUEST_URL=...
ACTIONS_ID_TOKEN_REQUEST_TOKEN=...
```

Kubernetes reads a projected service account token from
`/var/run/secrets/tokens/craik` by default. Generic file and env-var workload
providers support other CI systems that expose a current OIDC token directly.

## OIDC Token Exchange

The RFC 8693 token-exchange manager combines workload identity with an external
broker. Craik sends a platform-issued OIDC token to the exchange endpoint and
caches the returned short-lived credential until expiry. A common deployment is
GitHub Actions OIDC exchanged for a provider credential that is never committed,
printed, or stored as a long-lived secret in the repo.

## Policy-Bound Auth

Policy envelopes can constrain both operators and credentials. This example
requires a logged-in operator from the corporate issuer, restricts access to the
`prod-deploy` group, and allows only secret-manager-backed credentials:

```json
{
  "required_operator": true,
  "required_operator_issuer": "https://idp.example.com",
  "allowed_operator_groups": ["prod-deploy"],
  "allowed_credential_kinds": ["secret-ref"],
  "allowed_credential_profiles": ["anthropic:prod-*"]
}
```

Denied runs produce denial receipts that name the failing policy condition
without exposing credential material.

## Receipts and Audit

Provider receipts include:

- `auth_profile_id`
- `auth_kind`
- `auth_identity_hash`
- `operator_subject`
- `operator_issuer`
- `operator_email`
- `operator_groups`

The identity hash is stable across runs but non-reversible. It supports queries
like "every action taken by this operator" and "every action carried by this
credential identity" without storing the raw credential or account identifier in
the receipt.

## Health Check

Use `craik auth status` for stored profile state and `craik doctor` for
read-only health checks:

```sh
craik auth status
craik doctor
```

Doctor reports per-profile health, including environment variable presence,
local credential file readability, and OAuth token expiry when the source can
inspect it.

## Common Failures

Missing operator session: A policy with `required_operator=true` fails before
any provider call. Run `craik login`, then retry.

Expired OAuth token: Local-CLI OAuth sources refresh when possible. If refresh
cannot complete, the profile is reported as rejected or expired, and
long-running case files can surface token-expiry risk before the run starts.

Credential approval required: First live use of a profile pauses with a
credential approval request. Run `craik auth approve <profile_id> --run=<run_id>`
to unblock the run.
