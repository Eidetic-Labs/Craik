# Policy Test Reference

`craik policy test` is the machine-readable policy regression gate for v0.1.0.

Output shape:

```json
{
  "schema": "craik.policy_test_report",
  "version": "0.1.0",
  "status": "passed",
  "summary": {
    "passed": 6,
    "failed": 0,
    "total": 6
  },
  "results": []
}
```

Each result includes:

- `name`: stable check name,
- `status`: `passed` or `failed`,
- `message`: human-readable result or failure,
- `details`: check-specific evidence.

## Checks

| Check | Purpose |
| --- | --- |
| `immutable_path_requires_override_and_grant` | Confirms immutable paths cannot be written with ordinary docs grants. |
| `memory_writes_become_proposals` | Confirms memory updates follow the proposal path and direct local writes are denied. |
| `trusted_local_fail_open_receipts` | Confirms trusted-local fail-open is explicit and receipt-backed. |
| `automation_fails_closed` | Confirms automation does not widen authority or prompt for approvals. |
| `provider_runner_enforces_shell_grants` | Confirms the provider-backed runner blocks fixture side effects without a shell grant and completes with the scoped grant. |
| `redaction_receipts_logs_handoffs_case_files` | Confirms policy-relevant payload shapes redact secret-like material. |

## Failure Behavior

If any check fails, `status` becomes `failed`, the failed result includes the
violated condition, and the CLI exits with status code `1`.
