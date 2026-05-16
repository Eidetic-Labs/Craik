# Docker Sandbox Backend

The Docker sandbox backend represents containerized execution as an explicit
environment boundary. It does not start containers by itself.

`DockerSandboxRequest` records:

- backend id;
- image reference;
- command reference;
- network mode;
- mount references and target paths;
- environment reference names;
- privileged flag;
- policy envelope id;
- capability grant id;
- receipt id.

## Isolation Defaults

Docker sandbox requests are allowed only when:

- the backend is `container` with `container` isolation;
- the backend declares `container.run` with `run` operation;
- `privileged` is false;
- network mode is `none` or `restricted`;
- mounts are read-only by default;
- policy, grant, and receipt links are present.

Requests using host-like network defaults, privileged containers, read-write
mounts, missing policy controls, or missing receipts are denied before dispatch.

## Explicit Settings

Image refs, command refs, mount refs, and environment refs are references. They
must not embed raw credentials, tokens, passwords, or API keys.

Use [Environment Receipts](environment-receipts.md) to record allowed and denied
Docker sandbox decisions before a caller dispatches through a governed container
runtime.
