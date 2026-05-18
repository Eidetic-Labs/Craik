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
- `auth_profiles`: whether configured auth profiles can be inspected;
- `auth_profile:<id>`: per-profile credential health, including env-var
  presence, token expiry, and local credential file readability when available;
- `gateway_config`: whether a default gateway config is stored;
- `gateway_prerequisites`: whether daemon prerequisites are present;
- `policy`: whether gateway policy state is inspectable.

Each check has a `pass`, `warning`, or `fail` status plus an action when the
operator needs to do something.

Run `craik setup` before `craik doctor` when starting from an empty machine.

## Auth Profile Health

A healthy profile appears as a pass-level profile check:

```json
{
  "name": "auth_profile:anthropic:work",
  "status": "pass",
  "summary": "Auth profile anthropic:work is ok.",
  "action": null
}
```

If an API-key profile points at a missing environment variable, doctor reports a
warning without printing the secret name's value:

```json
{
  "name": "auth_profile:anthropic:work",
  "status": "warning",
  "summary": "Auth profile anthropic:work is rejected. secret reference could not resolve",
  "action": "Refresh or replace the credential before running live providers."
}
```

Use [Authentication and Credentials](authentication.md) to add, test, approve,
or replace credential profiles.
