# Memory Review Nudges

Memory review nudges identify facts that should be reviewed without directly
rewriting memory.

`MemoryReviewCandidate` records:

- fact reference;
- entity and relation;
- scope;
- confidence;
- evidence ids;
- last review timestamp;
- optional expiry timestamp;
- owner.

`memory_review_nudge` returns either `not_due` or `due`. Due nudges can be
triggered by stale review cadence, expired or expiring facts, low confidence, or
missing evidence.

Due nudges require receipt ids. They preserve evidence and owner links so a
reviewer can decide whether to approve, reject, refresh, or invalidate the
underlying fact through the normal memory proposal workflow.

## Boundary

Review nudges are reminders, not memory writes. They do not alter facts,
resolve contradictions, or promote inferred preferences.

Use [Preference Facts](preference-facts.md) to keep inferred user and team
preferences reviewable before approval.
