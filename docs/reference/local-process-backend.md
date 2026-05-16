# Local Process Backend

The local process backend represents execution through the host process
environment. It is intentionally a decision boundary, not ambient shell
authority.

`LocalProcessRequest` uses command references instead of inline shell strings.
Callers should resolve command references through policy-controlled runtime
configuration before dispatch.

## Required Controls

Local process execution requires:

- a `craik.sandbox_backend` with kind `local_process` and isolation mode
  `process`;
- declared `shell.execute` capability with `run` operation;
- policy envelope id;
- capability grant id;
- receipt id;
- redaction controls for persisted metadata.

Requests missing any of those controls are denied before execution.

## Limitations

The local process backend does not provide container, VM, or remote isolation. It
can only describe and authorize a command reference for a caller that already has
local execution capability. Do not use it for untrusted commands, unreviewed
input, or workloads that require filesystem, network, or process isolation.

Inline shell strings are denied. This avoids granting broad shell authority by
smuggling flags, pipes, command substitution, or chained commands into a command
reference field.

The helper in `craik.runtime.local_process_backend` does not execute commands.
It returns an allowed or denied decision that can be recorded in receipts before
the caller dispatches through a governed execution path.

Use [Environment Receipts](environment-receipts.md) to record allowed and denied
local process decisions.
