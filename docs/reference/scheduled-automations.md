# Scheduled Automations

Scheduled automations are enabled gateway definitions backed by cron-like
schedules. They evaluate one observed schedule tick at a time.

`craik.runtime.scheduled_automations` enforces:

- explicit enabled state;
- policy envelope checks;
- narrow `gateway.schedule.execute` authority;
- schedule tick deduplication;
- redacted automation receipts.

## Execution Boundary

A scheduled automation creates a task only when:

- the automation is enabled;
- the policy allows `gateway.schedule.execute`;
- the tick id has not already created a task;
- the schedule expression is valid.

Disabled automations, policy-denied automations, and duplicate ticks do not
create tasks.

## Receipts

Automation receipts record:

- policy envelope id;
- automation id;
- schedule id;
- tick id;
- created task id when one exists.

Receipts use `gateway.schedule.execute` and stay redacted.

## Limits

Scheduled automations do not run a clock or execute created tasks. They preserve
the boundary between schedule observation, task creation, and later task
execution under policy.
