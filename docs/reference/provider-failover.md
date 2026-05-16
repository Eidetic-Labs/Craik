# Provider Failover

Provider failover is an explicit routing policy. Craik only falls back from one
model provider to another when a `ProviderFailoverPolicy` contains a matching
rule from the failed provider id to the fallback provider id.

Failover decisions preserve the active policy envelope id so routing changes can
be tied back to the same governance boundary that authorized the original
provider selection.

## Rules

`ProviderFailoverRule` defines:

- the failed provider id;
- the fallback provider id;
- the audit reason for the fallback;
- whether a receipt is required for the decision.

If no rule matches the failed provider, failover is denied.

## Stop Conditions

Policies can name failure reasons that stop failover entirely. Stop conditions
are checked before fallback rules. This keeps routing from crossing policy,
trust, or capability boundaries after a failure reason that requires operator
review.

Stopped decisions do not name a fallback provider.

## Denied Fallback Paths

Policies can deny specific fallback provider ids. A denied fallback path blocks
the decision even when a rule points to that provider. This allows an operator to
disable a provider for budget, trust, capability, incident, or compliance
reasons without removing every rule that references it.

## Receipts

`ProviderFailoverDecision` records whether failover was allowed, denied, or
stopped. Decisions include the failed provider id, the fallback provider id when
one was evaluated, the policy envelope id, the decision reason, and whether the
decision requires a receipt.

Provider failover does not contact providers, load secrets, or grant execution
authority by itself. It supplies routing metadata for the caller to enforce
alongside provider switching, budgets, quotas, and policy envelopes.
