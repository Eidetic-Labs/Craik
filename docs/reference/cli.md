# CLI Reference

Craik exposes the `craik` command.

## `craik --version`

Print the installed Craik package version.

## `craik version`

Print the installed Craik package version.

## `craik setup`

Initialize the local home layout, local store, and default gateway
configuration. The command writes no secrets and prints the persisted
configuration as JSON.

Options:

- `--project-id <id>`: optional project id for the gateway configuration.
- `--enable-gateway` / `--disable-gateway`: persist gateway enabled state.
- `--gateway-bind-host <host>`: gateway bind host; defaults to `127.0.0.1`.
- `--gateway-port <port>`: gateway port; defaults to `8765`.
- `--policy-envelope-id <id>`: policy envelope for gateway authority.

## `craik doctor`

Run read-only diagnostics for local home, local store, memory backend
configuration, gateway prerequisites, and gateway policy readiness. The command
prints JSON and does not create files or contact external services.

## `craik update`

Print update guidance as JSON. The command reports installed version,
compatibility state, manual update steps, and non-mutating boundaries. It does
not rewrite the installation, fetch release metadata, or migrate local state.

## `craik provider list`

Print registered model providers as JSON.

## `craik provider show <provider-id>`

Print one registered model provider as JSON.

## `craik provider select <provider-id>`

Print a redacted provider selection payload.

Options:

- `--mode <mode>`: provider mode to select; defaults to `chat`.
- `--policy-envelope-id <id>`: policy envelope linked to this selection.
- `--receipt-id <id>`: receipt id linked to this selection; may be repeated.

## `craik schema list`

List registered Craik runtime contract schemas.

## `craik schema show <name>`

Print the JSON Schema for a registered runtime contract.

## `craik runners matrix`

Print the built-in runner capability matrix and trust profiles as JSON.

Options:

- `--runner <id>`: print one runner matrix. Known preview ids are `codex`,
  `claude`, `gemini`, and `fixture`.

## `craik prompt compile <task-id>`

Compile a deterministic policy-aware prompt for a task and runner.

Options:

- `--runner <id>`: runner id from `craik runners matrix`.
- `--expected-output-schema <schema>`: expected output schema. May be repeated.

The Codex adapter preview consumes compiled prompts through the Python runtime
API. See [Codex Runner Adapter](codex-runner-adapter.md) for fixture-mode setup,
metadata, and limitations.

The Claude adapter preview follows the same runtime API for Claude-compatible
prompt handoff. See [Claude Runner Adapter](claude-runner-adapter.md).

The Gemini adapter preview follows the same runtime API for conservative
read/review-oriented prompt handoff. See [Gemini Runner Adapter](gemini-runner-adapter.md).

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
- `--discovery-include <glob>`: context discovery include override; may be repeated.
- `--discovery-exclude <glob>`: context discovery exclude override; may be repeated.

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
- `--github / --no-github`: load or skip read-only GitHub context.
- `--discovery-include <glob>`: one-off context discovery include override; may be repeated.
- `--discovery-exclude <glob>`: one-off context discovery exclude override; may be repeated.

## `craik case show <case-id-or-task-id>`

Print one persisted case file by case id or task id.

## `craik connect stigmem`

Detect Stigmem backend compatibility.

Options:

- `--url <url>`: Stigmem node URL. Can also be set with `CRAIK_STIGMEM_URL`.
- `--api-key <key>`: bearer API key. Prefer `CRAIK_STIGMEM_API_KEY`.
- `--timeout <seconds>`: request timeout. Can also be set with `CRAIK_STIGMEM_TIMEOUT`.

## `craik demo stigmem-docs`

Run the Stigmem documentation reconciliation demo.

Options:

- `--repo-path <path>`: path inside the Stigmem Git repository; defaults to `.`.
- `--project-name <name>`: project name to register; defaults to `Stigmem`.
- `--stigmem-url <url>`: Stigmem node URL. Can also be set with `CRAIK_STIGMEM_URL`.
- `--stigmem-api-key <key>`: bearer API key. Prefer `CRAIK_STIGMEM_API_KEY`.
- `--github / --no-github`: load or skip read-only GitHub context.
- `--max-tokens <count>`: approximate case-file context budget.

The command prints a `craik.demo.stigmem_docs_reconciliation` JSON payload and
creates local project, task, case-file, contradiction, memory proposal, receipt,
handoff, and work-graph artifacts.

## `craik onboard`

Print runner-readable project onboarding context.

Required options:

- `--project <id-or-name>`: registered project id or name.

Options:

- `--policy-profile <name>`: `strict`, `trusted-local`, or `automation`; defaults to `strict`.
- `--trusted-local-fail-open`: explicitly opt in to trusted-local fail-open semantics.
- `--max-recent-handoffs <count>`: recent handoffs to include; defaults to `5`.

The command prints a `craik.agent_onboarding` JSON payload with the project
model, active policy, docs boundaries, recent handoffs, unresolved
contradictions, stale-risk warnings, validation commands, Stigmem backend status,
known traps, and allowed next actions.

## `craik contradictions open`

Open and persist a local contradiction report.

Required options:

- `--summary <text>`: contradiction summary.
- `--fact <id-or-text>`: conflicting fact id or statement. Repeat at least twice.

Options:

- `--task-id <id>`: task associated with this contradiction.
- `--affected-artifact <path-or-id>`: affected artifact. May be repeated.
- `--evidence-id <id>`: linked evidence id. May be repeated.
- `--owner <identity>`: owner responsible for resolution.
- `--proposed-resolution <text>`: proposed resolution.
- `--stigmem-conflict-id <id>`: optional future Stigmem conflict id.

## `craik contradictions list`

List local contradiction reports.

Options:

- `--task-id <id>`: only include reports for this task.
- `--status <status>`: `open`, `resolved`, or `ignored`.

## `craik contradictions show <report-id>`

Show one local contradiction report and linked evidence.

## `craik graph export`

Export the local work graph as deterministic JSON.

Options:

- `--task-id <id>`: only export graph objects for this task.

## `craik run list`

List persisted single-agent runs.

Options:

- `--task-id <id>`: only include runs for one task.

## `craik run inspect <run-id-or-task-id>`

Inspect a persisted single-agent run. The command prints the task run, linked
receipts, captured run outputs, memory proposals, and handoff references.

Options:

- `--json`: print machine-readable JSON.
- `--include-outputs / --no-include-outputs`: include captured run output
  payloads; defaults to including summaries and links.

## `craik run recover <run-id-or-task-id>`

Prepare recovery context for an interrupted or blocked run. Recovery inspects
durable state and emits the next safe recovery boundary; it must re-check policy
grants, intent-lock stop conditions, and iteration limits before any side
effect.

Options:

- `--dry-run`: print the recovery plan without creating new run state.
- `--reason <text>`: reason for recovery; recorded in follow-up handoff state.

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

## `craik memory diff <task-id>`

Print and persist a run-scoped memory diff for local proposal activity.

## `craik memory preview <task-id>`

Print and persist a memory impact preview before promotion or direct writes.

## `craik policy show`

Print a generated policy envelope.

Options:

- `--task-id <id>`: task id to include in the envelope.
- `--actor <actor>`: actor to include in the envelope.
- `--profile <name>`: `strict`, `trusted-local`, or `automation`.
- `--trusted-local-fail-open`: required explicit opt-in for trusted-local fail-open.
- `--include-receipt`: include the fail-open receipt preview when applicable.

## `craik policy test`

Run the v0.1.0 policy regression harness.

The command prints a JSON `craik.policy_test_report`. It exits with code `0`
when every check passes and code `1` if any policy check fails.

## `craik receipts list`

Print persisted capability receipts as JSON.

Options:

- `--task-id <id>`: only include receipts for this task id.
- `--policy-id <id>`: only include receipts linked to this policy envelope.
- `--handoff-id <id>`: only include receipts linked to this handoff.

## `craik receipts show <receipt-id>`

Print one persisted capability receipt as JSON.

Additional commands will be documented as they are implemented.
