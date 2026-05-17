# MVP Failure Modes

Craik's MVP hardening posture is fail-closed. The runtime should preserve enough
state to recover or review a failed run without silently promoting uncertain
work to durable facts.

## Boundaries

The MVP supports one release acceptance workflow, deterministic provider-backed
OpenAI and Anthropic execution, local case files, receipts, handoffs, memory
proposals, and work graphs. It does not treat live provider calls, broad daemon
operation, dashboards, or direct durable memory writes as required MVP paths.

## Prompt Injection

User text, repository text, documentation, and memory facts can contain hostile
instructions. Prompt compilation keeps those inputs inside task or context
sections and always renders the policy envelope, denied capabilities, grants,
context omissions, and stop conditions. Hostile text is evidence or input; it is
not authority to remove policy constraints.

## Secrets

Persisted payloads are validated before writing to the local store. Secret-shaped
values in keys or strings are rejected or redacted at persistence and receipt
boundaries. Public documentation checks also block secrets, private paths, and
private task names from Docusaurus content.

## Tool Calls And Side Effects

Side effects require matching policy grants and receipts. Missing or mismatched
grants block shell, file write, memory write, and GitHub write attempts. Immutable
documentation paths require explicit approval metadata. Unsupported loop
side-effect capabilities fail closed before runner output is accepted.

## Timeouts, Retries, And Budgets

Network clients expose timeout configuration and default to bounded requests.
Provider adapters classify retryable throttling and transient failures without
performing hidden live retries. Provider routing blocks exhausted or mismatched
budget and quota status. Agent loops enforce max-iteration limits and persist an
interrupted run when the limit is reached.

## Persisted Payloads

The SQLite store validates every registered contract payload before persistence
and rejects unknown schemas, wrong versions, extra fields, and unredacted secret
material. CI exercises persisted demo artifacts by reading them back through the
contract registry and revalidating their JSON payloads.

## Recovery Expectations

When a run blocks or fails, review the case file, receipts, handoff, run state,
and memory proposals before retrying. Do not convert assumptions, stale risks, or
omitted context into facts without new evidence.
