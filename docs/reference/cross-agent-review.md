# Cross-Agent Review

Cross-agent review lets one specialist role request review from another without
collapsing distinct decisions into a single worker result.

## Review Flow

1. Create `craik.review_request` for one or more worker results or debate
   summaries.
2. The reviewer returns `craik.review_result` with a decision of `approved`,
   `changes_requested`, `blocked`, or `deferred`.
3. An adjudicator records `craik.adjudication_outcome` with a decision of
   `accepted`, `rejected`, `revised`, or `deferred`.
4. Handoffs include `adjudication_ids` and `unresolved_disagreements` so the
   next agent can resume from the durable decision boundary.

## Reviewer Boundaries

Policy reviewer and adversarial reviewer results stay explicit. Adjudication
outcomes preserve `policy_review_result_ids` and
`adversarial_review_result_ids` so later agents can see which role made each
decision.

Reviewers can cite evidence, contradictions, receipts, handoffs, worker
results, and debate summaries. They should not rewrite worker output in place.
If a finding needs different wording, the adjudicator records a `revised`
adjudicated finding with replacement text.

## Deferral

Deferred adjudication is a durable outcome. It requires at least one unresolved
disagreement and should be carried into the next handoff. Use it when the
adjudicator cannot accept, reject, or revise a finding without more context,
human review, or a policy decision.
