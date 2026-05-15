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
