# Runtime Critics And Red Team

Runtime critic and red-team findings are typed review inputs. They are not
facts, final decisions, or policy overrides until a separate adjudication accepts
them.

## Runtime Critic Findings

`craik.runtime_critic_finding` captures quality issues found before accepting a
major output, handoff, or memory write. Finding types include unsupported claims,
policy violations, scope drift, missing validation, stale evidence, missing
handoffs, unredacted sensitive content, and risky memory writes.

Critic findings preserve:

- severity,
- rationale,
- affected artifacts,
- evidence ids,
- proposed actions,
- review status,
- and an optional adjudication link.

High and critical critic findings must include proposed actions. Findings about
unsupported claims or stale evidence must include evidence ids.

## Red-Team Findings

`craik.red_team_finding` captures adversarial review results for high-risk work.
Finding types include prompt injection, privilege escalation, data exfiltration,
destructive action, policy bypass, memory poisoning, adversarial input, and
other explicit attack paths.

Red-team findings can be marked `blocking`. A blocker must be high or critical
severity and must include proposed actions.

## Authority Boundary

Both contracts set `authoritative` to `false`. They are reviewable signals until
an adjudication record accepts, rejects, revises, or defers them. Callers should
surface reviewable blockers before durable handoffs or memory promotion, but
they should not treat the finding text as settled fact without adjudication.
