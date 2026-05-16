# Provider Switching

`craik provider` exposes a small operator-facing surface for model/provider
routing.

## List Providers

```sh
craik provider list
```

Prints registered provider metadata as JSON, including provider ids, supported
modes, capabilities, trust boundaries, config references, and secret reference
names. Secret values are not printed.

## Show Provider

```sh
craik provider show provider_fixture_local
```

Prints one provider by stable id.

## Select Provider

```sh
craik provider select provider_fixture_local --mode runner --policy-envelope-id policy_provider
```

Prints a redacted selection payload with:

- provider id;
- provider family;
- selected mode;
- trust boundary;
- runtime path;
- config references;
- secret reference names;
- budget and quota refs;
- policy envelope id;
- linked receipt ids.

Selection output is metadata-only. It does not contact providers, load secrets,
or grant execution authority.

Unsupported modes are rejected before a selection payload is produced.

Provider routing should check budget and quota status before dispatch. See
[Model Providers](model-providers.md) for budget and quota decision behavior.

Provider routing may fall back to another provider only through an explicit
[Provider Failover](provider-failover.md) policy that preserves policy envelope
boundaries and records the failover decision for audit.

For the full provider, MCP, sandbox, and receipt workflow, see
[Provider Routing And Sandboxes](../guides/provider-routing.md).
