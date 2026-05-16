# Context Budgeting

Case files should be bounded. The context budget records what was included and what was omitted.

Build with the default budget:

```sh
craik case build task_review_docs
```

Set a smaller or larger approximate token budget:

```sh
craik case build task_review_docs --max-tokens 12000
```

The local assembler records:

- `max_tokens`,
- `estimated_tokens`,
- `docs_included`,
- `adrs_included`,
- `docs_omitted`,
- `evidence_count`,
- and `assumption_count`.

When docs are omitted, the assembler adds an open assumption so the next agent can see that the case file is incomplete.

The current estimator is intentionally conservative and path-based. Later case assembly work should replace it with content-aware budgeting as repo, memory, GitHub, and handoff adapters mature.
