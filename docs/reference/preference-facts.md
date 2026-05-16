# Preference Facts

Preference facts model user and team preferences as reviewable records.

`PreferenceFact` records:

- preference id;
- subject, such as `user:maintainer` or `team:platform`;
- scope: `user` or `team`;
- preference statement;
- status: `inferred`, `approved`, or `rejected`;
- confidence;
- evidence ids;
- receipt ids;
- inferred-from references;
- optional review fields;
- creation timestamp.

Inferred preferences are not approved facts. They must cite evidence, receipts,
and inferred-from references, and they must not include review fields.

Approved and rejected preferences require reviewer, reason, and review
timestamp.

## Scope Boundary

User preferences require `user:` subjects. Team preferences require `team:`
subjects. Do not promote a user preference into a team preference without an
explicit review decision and evidence for that broader scope.
