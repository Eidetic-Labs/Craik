# Learning Receipts

Learning receipts are normal `craik.capability_receipt` records for
self-improvement decisions.

Supported learning actions:

- `proposal`;
- `review`;
- `eval_replay`;
- `promotion`;
- `rollback`;
- `export`.

`LearningReceiptContext` links receipts to task, policy, skill package,
proposal, telemetry, replay fixture, preference, memory fact, evidence, and
prior receipt context.

## Redaction

Learning receipts redact trajectories, raw trajectories, prompts, responses,
conversation payloads, export payloads, preference evidence, credentials, and
secret-like metadata keys.

Receipts should store ids and summaries, not raw training examples, private
preference evidence, or unredacted trajectories.

Learning receipts record decisions. They do not approve promotion, rewrite
skills, write memory facts, or export trajectories by themselves.
