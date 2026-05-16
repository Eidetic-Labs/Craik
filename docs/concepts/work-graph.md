# Work Graph

The work graph connects runtime objects that would otherwise be scattered across case files, receipts, handoffs, memory proposals, evidence, assumptions, and contradictions.

Nodes can represent:

- tasks,
- case files,
- handoffs,
- receipts,
- memory proposals,
- facts proposed by memory updates,
- evidence,
- assumptions,
- and contradictions.

Edges explain relationships such as:

- a task has a case file,
- a task has receipts,
- a handoff records receipts,
- a handoff proposes memory,
- a proposal is supported by evidence,
- and a case file contains assumptions or contradictions.

Graph export is read-only. It does not grant authority, mutate GitHub, write memory, or resolve contradictions.

Exports are deterministic and redacted before printing.
