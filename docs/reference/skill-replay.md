# Skill Replay

Skill replay compares current skill behavior against redacted, reproducible
fixtures before learning-loop changes are promoted.

`SkillReplayFixture` records:

- fixture id;
- skill package id;
- fixture name;
- input references;
- expected outcome;
- expected output references;
- evidence ids;
- redaction status;
- redacted metadata.

`SkillReplayObservation` records current behavior for a fixture, including
outcome, output references, validation signal ids, telemetry id, receipt ids,
and redacted metadata.

`replay_skill_fixture` returns a `SkillReplayResult` with pass/fail status,
reason, expected and observed outcome, missing output refs, unexpected output
refs, telemetry id, receipt ids, and timestamp.

## Fixture Expectations

Replay fixtures must be redacted and evidence-backed. They should reference
case files, worker results, telemetry, receipts, and evidence by id instead of
persisting raw prompts, outputs, traces, stdout, stderr, payloads, responses, or
credentials.

Failed replay results should block skill promotion until reviewed.

Learning loops can use [Memory Review Nudges](memory-review-nudges.md) to
surface stale or unsupported memory facts without rewriting them.
