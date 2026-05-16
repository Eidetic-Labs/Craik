# Project Model

Craik's project model is the runner-readable view of a registered repository.
It combines local project configuration, repository state, documentation
boundaries, memory backend configuration, policy posture, and known continuity
records.

The model is intentionally operational. It tells an agent:

- which repository it is entering,
- which docs are mutable,
- which paths are immutable evidence,
- which memory backend is configured,
- which tasks and handoffs already exist,
- which contradictions still need review,
- which validation commands are expected,
- and which next actions are allowed.

## Boundaries

Project profiles can declare mutable documentation paths and immutable paths.
Immutable paths, such as ADR directories, are included as evidence but are not
normal edit targets. Agents should treat these paths as read-only unless a
separate policy grant explicitly allows a change.

## Onboarding Output

`craik onboard --project <project-id-or-name>` prints a
`craik.agent_onboarding` payload. The payload is designed for agents and
runners, not just humans. It includes:

- the project model,
- active policy envelope,
- docs boundaries,
- recent handoffs,
- unresolved contradictions,
- stale-risk warnings,
- validation commands,
- Stigmem backend status,
- known traps,
- and allowed next actions.

The command does not probe external services by default. Stigmem status reports
whether the project is configured for Stigmem and whether connection environment
variables are present, without printing credentials.
