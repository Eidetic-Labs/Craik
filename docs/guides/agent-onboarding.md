# Agent Onboarding

Use onboarding before starting project work:

```sh
craik onboard --project Example
```

The command prints a JSON `craik.agent_onboarding` report. It is safe for
runners to parse directly and includes the current project model, policy
envelope, documentation boundaries, recent handoffs, unresolved contradictions,
stale-risk warnings, validation commands, Stigmem backend status, known traps,
and allowed next actions.

## Policy Profile

By default, onboarding uses the `strict` policy profile:

```sh
craik onboard --project Example --policy-profile strict
```

The active policy is included in the output so agents can see allowed
capabilities, denied capabilities, approval requirements, and verification
requirements before acting.

Trusted-local onboarding requires the same explicit fail-open opt-in as policy
preview:

```sh
craik onboard --project Example --policy-profile trusted-local --trusted-local-fail-open
```

## Documentation Boundaries

The `docs_boundaries` section separates mutable docs paths from immutable paths.
Immutable docs, such as ADR directories, are evidence. Do not edit them unless a
separate policy approval explicitly allows it.

## Continuity Checks

The output surfaces:

- recent handoffs for the project,
- unresolved contradiction reports,
- stale-risk warnings,
- configured validation commands,
- and known traps.

Agents should review these fields before creating a plan. Missing handoffs,
missing docs paths, dirty repository state, unresolved contradictions, or missing
Stigmem environment configuration are reported as stale-risk warnings.

## Stigmem Status

Onboarding does not print secrets or make a live Stigmem request. For Stigmem
projects, it reports whether `CRAIK_STIGMEM_URL` and `CRAIK_STIGMEM_API_KEY` are
configured. Use `craik connect stigmem` when a live backend compatibility check
is needed.
