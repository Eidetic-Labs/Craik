# Memory Impact Preview View

The memory impact preview view is a read-only operator display for proposed
memory writes before promotion or direct write attempts.

The v0.7.0 TUI surface formats:

- pending memory proposals and their status;
- facts that would be added or updated;
- facts that would be invalidated;
- proposals missing evidence;
- likely contradiction risks;
- scope counts;
- policy envelope and receipt links when available.

## Preview Boundary

Memory proposals are not accepted facts. The view lists proposals separately
from `facts_to_add` and `facts_to_invalidate` so operators can see the proposed
change without treating it as durable memory.

Pending and rejected proposals remain review records. Approved proposals still
require the configured backend and policy path before becoming durable facts.

## Evidence And Contradictions

Evidence gaps are shown by proposal ID. Likely contradictions are preview risks,
not resolved conflicts. A contradiction preview points to the existing value,
proposed value, and reason so the operator can decide whether to approve,
reject, revise, or open a formal contradiction review.

See [Memory Backends](memory-backends.md) and
[Memory Proposals](../guides/memory-proposals.md) for the underlying proposal
workflow.
