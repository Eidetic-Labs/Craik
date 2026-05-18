# Setup Wizard

`craik setup` initializes the local Craik home, local store, and a default
gateway configuration.

```sh
craik setup
```

The command writes inspectable, non-secret configuration only. It does not ask
for API keys, channel tokens, webhook secrets, or bearer credentials. Store those
secrets in the operator's secret manager or environment variables for the
specific adapter that needs them.

For live provider calls, run OIDC operator login and add a credential profile
after setup:

```sh
craik login
craik auth add anthropic:work --kind=api-key --env-var=ANTHROPIC_API_KEY
```

See [Authentication and Credentials](authentication.md) for the full credential
surface, including local-CLI OAuth, secret references, Stigmem-backed
credentials, workload identity, and approval-gated first use.

## Gateway Options

Enable the persisted gateway configuration:

```sh
craik setup --enable-gateway --policy-envelope-id policy_gateway
```

Public gateway binds require a policy envelope:

```sh
craik setup --gateway-bind-host 0.0.0.0 --policy-envelope-id policy_gateway
```

The setup output includes:

- resolved local state paths;
- the persisted `craik.gateway_config` payload;
- `secrets_written = false`;
- next steps for diagnostics and gateway review.

Run diagnostics before starting an always-on gateway.
