# Scheduled Task Creation

Cron-like gateway schedules convert one schedule tick into one deterministic
`craik.task_request`.

`craik.runtime.schedules` does not run a scheduler loop. It validates schedule
definitions and converts an observed tick into a task while preserving gateway
context.

## Cron Shape

Schedules use a conservative five-field cron-like expression. Supported field
characters are digits, `*`, `/`, `,`, and `-`.

Examples:

```text
0 9 * * *
*/15 9-17 * * 1,2,3,4,5
```

Named shortcuts such as `@daily` are not supported.

## Task Context

Created tasks preserve:

- schedule id;
- schedule tick id;
- cron expression;
- run timestamp;
- project id;
- policy envelope id;
- channel;
- linked receipt ids.

The task id is deterministic from schedule id and tick id.

## Deduplication

Callers pass the set of already-seen tick ids. If the tick id was already seen,
task creation returns `created = false` and does not create another
`TaskRequest`.

## Limitations

Scheduled task creation does not execute the task, persist it, or start a clock.
Future gateway scheduling layers are responsible for tracking seen ticks,
persisting tasks, and emitting schedule execution receipts.
