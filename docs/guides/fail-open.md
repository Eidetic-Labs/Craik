# Fail-Open

Craik defaults to fail-closed behavior.

Fail-open behavior is only available through named profiles. In v0.1.0, the only fail-open profile is `trusted-local`, and it requires explicit opt-in.

Preview a trusted-local policy envelope:

```sh
craik policy show --profile trusted-local --trusted-local-fail-open
```

Include the mandatory fail-open receipt preview:

```sh
craik policy show \
  --profile trusted-local \
  --trusted-local-fail-open \
  --include-receipt
```

Fail-open does not bypass redaction, receipts, immutable path protection, or direct memory write approvals.

Automation mode is fail-closed. It should stop rather than widen permissions.

