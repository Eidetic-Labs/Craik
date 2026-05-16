# Remote Shell Backend

The remote shell backend represents SSH or equivalent remote command execution
as an auditable boundary. It does not open connections or execute commands by
itself.

`RemoteShellTarget` stores non-secret target metadata:

- host reference;
- optional user and port references;
- external auth reference name;
- non-secret metadata.

References must point to configuration or secret tooling. They must not embed
raw usernames with passwords, bearer tokens, SSH private keys, or credential
values.

## Required Controls

Remote execution requires:

- a `craik.sandbox_backend` with kind `remote_shell` and isolation mode
  `remote`;
- declared `shell.remote.execute` capability with `run` operation;
- remote target id;
- external auth reference name;
- policy envelope id;
- capability grant id;
- receipt id;
- redaction controls for persisted metadata.

Denied and allowed decisions preserve the backend id, target id, command
reference, receipt id when present, decision reason, and required controls.

## Security Boundary

Remote shell requests use command references instead of inline shell strings.
Inline SSH commands, pipes, chained commands, and command substitution are
denied before dispatch.

Remote shell backends should be used only for trusted, policy-approved targets.
They do not provide container isolation, local filesystem protection, network
egress filtering, or credential brokering. Store SSH keys, passwords, tokens,
and host secrets outside Craik configuration and refer to them by auth reference
name.

Use [Environment Receipts](environment-receipts.md) to record allowed and denied
remote shell decisions.
