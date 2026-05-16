# CLI Reference

Craik exposes the `craik` command.

## `craik --version`

Print the installed Craik package version.

## `craik version`

Print the installed Craik package version.

## `craik schema list`

List registered Craik runtime contract schemas.

## `craik schema show <name>`

Print the JSON Schema for a registered runtime contract.

## `craik home show`

Print resolved Craik local state paths without creating directories.

## `craik home init`

Create Craik's local state directories.

## `craik project add <path>`

Register a Git repository in the local project registry.

Options:

- `--name <name>`: project name; defaults to the repository directory name.
- `--docs-path <path>`: documentation path to include; may be repeated.
- `--immutable-path <path>`: immutable path to include; may be repeated.

## `craik project list`

Print registered projects as JSON.

## `craik project show <id-or-name>`

Print one registered project as JSON.

## `craik task create`

Create a task request for a registered project.

Required options:

- `--project <id-or-name>`: registered project id or name.
- `--title <title>`: task title.
- `--objective <objective>`: task objective.

Options:

- `--requested-by <identity>`: requester identity; defaults to `user:local`.
- `--priority <name>`: `low`, `normal`, `high`, or `urgent`.
- `--mode <name>`: `plan`, `review`, `implement`, or `verify`.
- `--constraint <text>`: task constraint; may be repeated.
- `--accepted-interpretation <text>`: accepted interpretation to capture in the intent lock.
- `--in-scope <text>`: in-scope work for the intent lock; may be repeated.
- `--out-of-scope <text>`: excluded work for the intent lock; may be repeated.
- `--allowed-autonomy <text>`: autonomous action allowed by the intent lock; may be repeated.
- `--stop-condition <text>`: condition that should stop execution; may be repeated.
- `--scope-change-rule <text>`: rule for handling scope changes; may be repeated.
- `--expected-output <text>`: expected output; may be repeated.

The command prints both the task request and the generated intent lock.

## `craik intent show <intent-id-or-task-id>`

Print one persisted intent lock by intent lock id or task id.

## `craik case build <task-id>`

Build and persist a deterministic case file for a task.

Options:

- `--max-tokens <count>`: approximate context budget; defaults to `24000`.

## `craik case show <case-id-or-task-id>`

Print one persisted case file by case id or task id.

## `craik connect stigmem`

Detect Stigmem backend compatibility.

Options:

- `--url <url>`: Stigmem node URL. Can also be set with `CRAIK_STIGMEM_URL`.
- `--api-key <key>`: bearer API key. Prefer `CRAIK_STIGMEM_API_KEY`.
- `--timeout <seconds>`: request timeout. Can also be set with `CRAIK_STIGMEM_TIMEOUT`.

## `craik handoff create <task-id>`

Create and persist a structured handoff for a task.

Required options:

- `--summary <text>`: handoff summary.

Options:

- `--agent <identity>`: agent identity; defaults to `agent:local`.
- `--status <name>`: `completed`, `incomplete`, `blocked`, or `failed`.
- `--completed-action <text>`: completed action; may be repeated.
- `--file-changed <path>`: changed file; may be repeated.
- `--artifact <path-or-id>`: artifact path or id; may be repeated.
- `--command-run <command>`: command run; may be repeated.
- `--test-run <command-or-name>`: validation run; may be repeated.
- `--risk <text>`: residual risk; may be repeated.
- `--next-step <text>`: next step; may be repeated.
- `--policy-exception <text>`: policy exception or fail-open note; may be repeated.
- `--self-audit-note <text>`: self-audit note; may be repeated.
- `--markdown`: print Markdown instead of JSON after creating the handoff.

## `craik handoff show <handoff-id-or-task-id>`

Print one persisted handoff by handoff id or task id.

Options:

- `--markdown`: print Markdown instead of JSON.

## `craik memory propose <task-id>`

Create a reviewable local memory proposal.

Required options:

- `--entity <entity>`: fact entity.
- `--relation <relation>`: fact relation.
- `--value <value>`: fact value.
- `--source <source>`: fact source.
- `--evidence-source <source>`: evidence source.
- `--evidence-locator <locator>`: evidence locator.
- `--evidence-summary <summary>`: evidence summary.

Options:

- `--confidence <value>`: confidence from `0.0` to `1.0`.
- `--scope <scope>`: `local`, `team`, `company`, or `public`.
- `--trust-class <class>`: `observed`, `reported`, `inferred`, `policy`, `external`, or `stale-risk`.
- `--operation <operation>`: `add`, `update`, or `invalidate`.

## `craik memory list`

List local memory proposals.

Options:

- `--task-id <id>`: only include proposals for this task.
- `--status <status>`: only include proposals with this status.

## `craik memory show <proposal-id>`

Print one local memory proposal.

## `craik memory approve <proposal-id>`

Approve a local memory proposal for local search. Approval requires evidence.

Options:

- `--decided-by <identity>`: reviewer identity.
- `--reason <text>`: decision reason.

## `craik memory reject <proposal-id>`

Reject a local memory proposal.

Options:

- `--decided-by <identity>`: reviewer identity.
- `--reason <text>`: decision reason.

## `craik memory search <query>`

Search approved local memory facts.

## `craik policy show`

Print a generated policy envelope.

Options:

- `--task-id <id>`: task id to include in the envelope.
- `--actor <actor>`: actor to include in the envelope.
- `--profile <name>`: `strict`, `trusted-local`, or `automation`.
- `--trusted-local-fail-open`: required explicit opt-in for trusted-local fail-open.
- `--include-receipt`: include the fail-open receipt preview when applicable.

## `craik receipts list`

Print persisted capability receipts as JSON.

Options:

- `--task-id <id>`: only include receipts for this task id.
- `--policy-id <id>`: only include receipts linked to this policy envelope.
- `--handoff-id <id>`: only include receipts linked to this handoff.

## `craik receipts show <receipt-id>`

Print one persisted capability receipt as JSON.

Additional commands will be documented as they are implemented.
