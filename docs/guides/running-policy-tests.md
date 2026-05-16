# Running Policy Tests

Craik includes a policy regression harness for release gates:

```sh
craik policy test
```

The command prints a JSON `craik.policy_test_report`. A passing report exits
with status code `0`. Any failed policy check exits nonzero and includes the
violated check name plus a failure message.

## What It Checks

The v0.1.0 policy gate verifies:

- immutable paths require approval metadata and a matching grant,
- memory updates are proposals by default and direct local writes are denied,
- trusted-local fail-open use creates a visible receipt,
- automation remains fail-closed,
- runner grant boundaries remain tracked until runner adapters exist,
- and receipts, logs, handoffs, and case files pass redaction regressions.

## CI Usage

Run the policy gate with the normal validation set:

```sh
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
craik policy test
```

In source-tree development, use:

```sh
uv run --python 3.12 --extra dev craik policy test
```

The harness uses local Craik state and may create a pending local memory proposal
inside the selected `CRAIK_HOME`.
