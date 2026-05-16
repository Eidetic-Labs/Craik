# Doctor Diagnostics

`craik doctor` runs read-only diagnostics for local and gateway readiness.

```sh
craik doctor
```

The command does not create `CRAIK_HOME`, initialize a database, contact
Stigmem, start a gateway, or write receipts. It only inspects existing local
state and environment variables.

## Checks

Doctor reports:

- `local_home`: whether the resolved Craik home exists;
- `local_store`: whether the local SQLite store exists and is readable;
- `memory_backend`: whether shared Stigmem memory is configured;
- `gateway_config`: whether a default gateway config is stored;
- `gateway_prerequisites`: whether daemon prerequisites are present;
- `policy`: whether gateway policy state is inspectable.

Each check has a `pass`, `warning`, or `fail` status plus an action when the
operator needs to do something.

Run `craik setup` before `craik doctor` when starting from an empty machine.
