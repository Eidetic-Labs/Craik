# Skill Promotion Gates

Skill promotion gates prevent reviewed skill proposals from becoming promoted
guidance without explicit approval.

`SkillPromotionRequest` records:

- proposal id;
- skill package id;
- promoted version id;
- approver;
- policy envelope id;
- evidence ids;
- eval result ids;
- receipt ids;
- approval receipt id.

`SkillPromotionDecision` records:

- request id;
- proposal id;
- skill package id;
- decision status: `approved` or `denied`;
- approver;
- promoted version id;
- policy envelope id;
- evidence ids;
- eval result ids;
- receipt ids;
- denial reasons.

## Required Gates

Promotion is approved only when:

- the request references the same proposal, skill package, and policy envelope as
  the proposal;
- the proposal status is `approved`;
- the proposal has a structured improvement plan;
- the approver is explicit and not an agent identity;
- evidence ids are present;
- eval result ids are present;
- receipt ids are present;
- an approval receipt id is present.

Missing gates produce a denied decision with reviewable denial reasons.

Promotion decisions should be accompanied by a
[Learning Receipt](learning-receipts.md) using the `promotion` action and can be
evaluated with [Skill Replay](skill-replay.md) results before approval.
