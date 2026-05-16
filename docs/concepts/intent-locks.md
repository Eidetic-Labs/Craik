# Intent Locks

Intent locks capture the accepted task intent before execution.

They reduce scope drift by separating the user's request from the runtime's accepted interpretation and explicit boundaries.

An intent lock records:

- the original request,
- the objective,
- the accepted interpretation,
- in-scope work,
- excluded work,
- allowed autonomy,
- stop conditions,
- and scope-change rules.

Intent locks are persisted as `craik.intent_lock` records and are linked from case files. Handoff contracts also include an intent lock field so future handoff writers can preserve the same boundary.

## Why Intent Locks Exist

Long-running agent work can drift when new findings, tool output, or partial implementation details make nearby work tempting. Intent locks make that boundary reviewable.

An agent should stop or ask for a scope update when:

- the requested work no longer matches the accepted interpretation,
- a required action is listed as out of scope,
- the task would cross a stop condition,
- or the task requires new autonomy not listed in the lock.

## Current Implementation

`craik task create` creates an intent lock for the task.

`craik case build` ensures the task has an intent lock and includes its id in the case file.

`craik intent show` prints an intent lock by intent lock id or task id.
