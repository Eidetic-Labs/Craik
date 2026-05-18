# 0007 Credential And Identity Architecture

## Context

Provider credentials and operator identity are governance inputs, not incidental
plumbing. Craik receipts need to answer which human authorized work, which
credential carried the provider call, which policy allowed it, and which
authorization grant made the credential usable. Reconstructing those answers
from environment variables or local shell state would be fragile and would not
survive handoffs, audits, or future multi-agent coordination.

The governance thesis is: every action is authorized by a credential, every
credential is authorized by an operator, and every authorization graph is itself
receipted.

## Decision

Craik uses typed `AuthProfile` records with `<provider_family>:<name>` IDs as
the unit of credential identity. A `CredentialSource` protocol resolves request
headers at call time. Built-in source kinds cover env-var API keys, local-CLI
OAuth fallback, vendor CLI bridge, external secret references, Stigmem-backed
credential references, and marker identity for no-secret local providers.

Operators authenticate with OIDC. Device-code flow supports headless and remote
environments. Loopback + PKCE is available to entrypoints that can use a browser
redirect. Operator sessions are persisted locally and refreshed when possible.
Workload identity providers and RFC 8693 token exchange support CI and cloud
deployments without long-lived provider secrets.

Provider receipts carry both credential and operator fields: `auth_profile_id`,
`auth_kind`, `auth_identity_hash`, `operator_subject`, `operator_issuer`,
`operator_email`, and `operator_groups`. Policy envelopes can constrain both
dimensions with required operator identity, allowed operator subjects or groups,
required issuer, allowed credential kinds, and allowed credential profile
patterns.

First live use of a credential profile is approval-gated. Operator-to-profile
authorization grants are stored on the profile with a receipt chain so the
authorization graph is queryable.

## Consequences

Each provider receipt is a two-dimensional audit record: the operator who drove
the work and the credential identity that carried it. Operators can query all
actions taken by a human or all actions carried by a credential identity without
exposing raw credentials or account identifiers.

Credential authorization becomes first-class state instead of tribal knowledge.
Future multi-agent runtime work can isolate credentials and operators per agent
without redesigning receipts or handoff records. CI and cloud deployments can
use workload identity and token exchange instead of storing long-lived provider
secrets.

The tradeoff is extra setup surface. Users need to understand operator login,
credential profiles, approval, and policy constraints before using live
providers in governed mode.

## Alternatives Considered

SAML for operator identity was rejected for the MVP because OIDC is more common
for CLI, CI, and cloud-native authentication flows.

Direct OIDC provider authentication was rejected because major LLM providers do
not currently accept arbitrary workload or operator OIDC tokens as provider
credentials. Token exchange keeps the model extensible if providers or brokers
add federation later.

Env-var-only credential resolution was rejected because it cannot represent
Claude subscriber credentials, enterprise secret managers, team-shared Stigmem
credentials, credential rotation, or per-profile authorization.

Static origin allowlists for credentials were rejected because developer and CI
environments often have dynamic origins and because origin checks do not answer
which operator was authorized to use which credential.

## Retraction

No retraction is active. Retract this ADR if Craik adopts a federated identity
mesh that makes per-profile credential authorization and local operator sessions
obsolete.
