# Gateway Daemon Mode

Gateway daemon mode is post-MVP unless a later proof workflow explicitly pulls
it forward. The current surface documents contracts and deterministic lifecycle
helpers, not an operational always-on service. See
[Post-MVP Scope](post-mvp-scope.md).

The daemon lifecycle is represented by two contracts:

- `craik.gateway_config` records local bind settings, mode, policy envelope,
  pid/log file paths, and whether the gateway is enabled.
- `craik.gateway_runtime_state` records the supervised lifecycle state,
  process id, timestamps, receipts, and supervision notes.

## Lifecycle

The initial lifecycle states are:

- `starting`: a supervisor has accepted a start request and is preparing the
  process.
- `running`: the supervisor has a process id and start timestamp.
- `stopping`: reserved for future graceful shutdown coordination.
- `stopped`: the process is no longer active and has a stop timestamp.
- `failed`: the supervisor recorded an explicit failure reason.

Daemon mode requires a pid file. Public binds such as `0.0.0.0` require a policy
envelope so externally reachable gateway behavior is never implicit.

## Boundary

This phase defines lifecycle state, persistence, and inspection boundaries. It
does not add open inbound messages, webhook handling, channel adapters,
scheduled task creation, or a production dispatch loop. Those surfaces are
post-MVP work items and must attach policy checks and receipts before they can
affect runtime state.

Gateway records are safe to inspect from the operator surface and local store.
Starting a real long-running service remains an explicit supervisor operation;
tests use deterministic lifecycle helpers rather than background processes.
