# Policy Profiles

Craik ships with conservative v0.1.0 policy profiles.

Every generated policy envelope includes:

- profile name,
- fail-open status,
- allowed capabilities,
- denied capabilities,
- approval requirements,
- verification requirements,
- receipt requirement,
- handoff requirement,
- and redaction requirement.

## Strict

`strict` is the default profile.

Default behavior:

- fail-open is disabled,
- read-only repository and memory access are allowed,
- receipts are required,
- redaction is required,
- writes require explicit grants,
- shell commands require explicit grants,
- GitHub writes require explicit grants,
- direct memory writes require explicit grants,
- immutable path writes are denied.

Preview:

```sh
craik policy show
```

## Trusted Local

`trusted-local` is an explicit fail-open profile for trusted local development.

It is never selected accidentally. Callers must explicitly opt in:

```sh
craik policy show --profile trusted-local --trusted-local-fail-open
```

Expected behavior:

- fail-open is enabled,
- broader local file and shell capabilities may be allowed,
- receipts remain required,
- redaction remains required,
- immutable path writes remain denied unless separately approved,
- direct memory writes still require approval.

Every trusted-local fail-open decision must create a receipt.

## Automation

`automation` is for CI and unattended workflows.

Expected behavior:

- fail-open is disabled,
- approval prompts are not required,
- failures stop execution instead of widening authority,
- broad shell capabilities are denied,
- direct memory writes are denied unless granted elsewhere.

Preview:

```sh
craik policy show --profile automation
```

## Visibility

Fail-open profile use is visible in the policy envelope immediately. Later runtime layers must also preserve it in case files, receipts, and handoffs.

