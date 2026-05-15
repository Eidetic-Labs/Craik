# Governance Model

Craik should be governance-native. Policy is not an enterprise add-on; it is part of the runtime contract.

## Policy Envelope

Every task runs inside a policy envelope.

The envelope defines:

- actor identity,
- task scope,
- repository scope,
- memory scope,
- allowed capabilities,
- write boundaries,
- required approvals,
- required verification,
- documentation obligations,
- and handoff obligations.

## Default Security Posture

Craik should be secure by default and explicitly fail-open by policy.

Default behavior:

- task execution starts read-only,
- file writes require capability grants,
- shell commands require capability grants,
- GitHub writes require capability grants,
- memory writes default to proposals,
- immutable paths are denied by default,
- runner adapters cannot bypass Craik grants,
- plugins start probationary,
- and important actions create receipts.

Fail-open behavior is allowed only through named policy profiles. It should never happen as an accidental fallback.

Every fail-open decision must be visible in:

- the policy envelope,
- the case file,
- capability receipts,
- and the final handoff.

The v0.1.0 policy profile implementation generates the policy envelope directly and provides a mandatory fail-open receipt shape for trusted-local opt-ins. Case files and handoffs must preserve those fields when those layers are implemented.

## Policy Profiles

Craik should ship with conservative named policy profiles.

### Strict

Default profile for normal tasks.

```yaml
policy:
  mode: strict
  fail_open: false
```

Expected behavior:

- read-only by default,
- explicit grants for all writes,
- memory writes become proposals unless direct write is granted,
- shell commands require grant,
- GitHub writes require grant,
- immutable path writes denied.

### Trusted Local

Opt-in profile for trusted local development.

```yaml
policy:
  mode: trusted-local
  fail_open: true
  require_receipts: true
```

Expected behavior:

- broader local file and shell access may be allowed,
- receipts remain mandatory,
- secrets are still redacted,
- immutable path writes still require explicit override,
- and direct memory writes still require a memory write grant.

### Automation

Profile for CI and unattended workflows.

```yaml
policy:
  mode: automation
  fail_open: false
```

Expected behavior:

- deterministic grants,
- no interactive approval requirement,
- no broad shell access unless granted,
- no direct memory writes unless granted,
- and failures should stop execution instead of widening permissions.

## Capability Grants

Agents should not receive ambient authority.

A capability grant should include:

- capability name,
- target scope,
- allowed operations,
- reason,
- expiration,
- approval requirement,
- and receipt requirement.

Examples:

- read repository files,
- write docs only,
- run tests,
- inspect GitHub PRs,
- create GitHub comments,
- write Stigmem facts in a specific scope.

## Secret Handling And Redaction

Craik should treat secrets as toxic runtime data.

Secret storage:

- store local secrets under `~/.craik/secrets/` by default,
- support environment variables for CI and agent-runner workflows,
- use owner-only file permissions where supported,
- and avoid writing secrets to project-local state.

Redaction requirements:

- centralize redaction in a shared runtime utility,
- redact known tokens, API keys, bearer headers, auth URLs, and configured secret patterns,
- apply redaction before writing logs, receipts, handoffs, case files, memory proposals, errors, and work graph events,
- preserve enough shape to debug without exposing raw secret values,
- and treat redaction failures as security bugs.

The v0.1.0 utility is `craik.runtime.redaction`; local persistence rejects payloads that still appear to contain unredacted secret material.

Secrets must not be written to Stigmem facts.

## Capability-Gated Actions

The following actions require explicit grants:

- file writes,
- file deletion,
- shell command execution,
- Git branch mutation,
- Git commit creation,
- Git push,
- GitHub issue/PR/comment creation or mutation,
- Stigmem direct fact writes,
- contradiction resolution that invalidates facts,
- plugin execution with side effects,
- and runner actions that invoke tools outside read-only context.

Read-only actions may still require grants when they can expose sensitive data.

## Immutable Path Protection

Project profiles may define immutable paths.

Examples:

- ADR directories,
- signed release artifacts,
- generated audit records,
- historical migration records.

Immutable paths are denied by default. A write to an immutable path requires:

- explicit immutable-path override,
- user or maintainer approval,
- receipt,
- and handoff note explaining why the override was used.

In v0.1.0 grant checks, override metadata must include who approved the override and why. The override is still denied unless a matching immutable write grant is present.

## Capability Receipts

Important actions produce receipts.

Receipt fields:

- receipt id,
- actor,
- task id,
- capability,
- target,
- reason,
- input summary,
- result summary,
- timestamp,
- policy envelope id,
- and links to artifacts.

Receipts are not meant to replace logs. They are concise accountability records for actions that matter.

Receipts must record when a task runs under a fail-open policy profile or when a capability grant widens access beyond strict defaults.

## Memory Write Policy

Memory writes should be governed by confidence and source.

Initial write classes:

- **observed:** directly seen in repo, tool output, API response, or artifact,
- **reported:** stated by a user or agent,
- **inferred:** reasoned from evidence,
- **policy:** sourced from ADRs, repo rules, or governance docs,
- **external:** sourced from web or package registries,
- **stale-risk:** likely to change and should be refreshed before use.

Agents may be allowed to act directly on observed and policy facts while treating inferred and reported facts as leads unless confirmed.

## Human Overrides

Human overrides should create durable records.

An override should capture:

- what was overridden,
- who overrode it,
- why,
- what evidence or policy applies,
- and what downstream facts or tasks are affected.

## Contradictions

Contradictions should not be silently resolved by last write wins.

Craik should surface:

- conflicting assertions,
- source and confidence for each,
- affected tasks,
- affected docs,
- proposed resolution,
- and required reviewer or owner.

## Degraded Mode

Craik may run without Stigmem, but governance features should degrade transparently.

Without Stigmem:

- facts may be local or ephemeral,
- contradiction tracking may be local only,
- provenance may be limited,
- federation is unavailable,
- and trust tiers may be advisory.

The product should be explicit about unavailable capabilities.

## Local State Governance

Craik uses `~/.craik` as the default local home, with `CRAIK_HOME` as the primary override.

Local state should keep data classes separated:

- `config/` for user-editable configuration,
- `secrets/` for local credentials and tokens,
- `state/` for SQLite databases and durable runtime state,
- `cache/` for disposable data,
- `logs/` for runtime logs,
- `receipts/` for capability receipts,
- `handoffs/` for durable handoff artifacts,
- `case-files/` for assembled task context,
- `projects/` for project registry metadata.

Security expectations:

- home and secrets paths should be owner-only where supported,
- secret values should not appear in receipts, logs, handoffs, or case files,
- path commands should make active local paths inspectable,
- and project-local `.craik/` directories should be explicit opt-in only.
