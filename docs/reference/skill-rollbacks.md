# Skill Rollbacks

Skill rollbacks provide a reviewable path for reverting promoted skill updates
when a promoted version causes regressions or violates policy.

`SkillRollbackTarget` records:

- skill package id;
- promoted version id;
- rollback version id;
- promoted proposal id;
- promoted receipt id.

The rollback version must be distinct from the promoted version. Rollbacks point
at a prior promoted version; they do not invent replacement guidance.

`SkillRollbackRequest` records:

- task id;
- rollback target;
- rollback reason;
- rationale;
- policy envelope id;
- evidence ids;
- receipt ids;
- replay result ids;
- requester and request timestamp.

Requests require policy, evidence, and receipt references so reviewers can audit
why the rollback was proposed.

## Decision Gate

`decide_skill_rollback` approves a rollback only when the request has replay
result context and the decision records its own receipt. Missing replay context
or a missing decision receipt produces a denied `SkillRollbackDecision`.

Approved decisions preserve the rollback version id and decision receipt id.
Denied decisions preserve explicit denial reasons.

Rollback decisions should also be recorded with a
[Learning Receipt](learning-receipts.md) using the `rollback` action.
