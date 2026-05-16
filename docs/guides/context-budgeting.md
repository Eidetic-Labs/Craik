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
- `docs_excluded`,
- `discovery_rules`,
- `evidence_count`,
- and `assumption_count`.

When docs are omitted, the assembler adds an open assumption so the next agent can see that the case file is incomplete.

Craik also applies repository discovery defaults before budgeting. Generated,
dependency, build, cache, and archive-heavy paths are excluded by default so a
case file does not spend context on paths such as `node_modules/`,
`docs/build/`, or `docs/archive/`.

Persist project-level discovery rules at registration time:

```sh
craik project add /path/to/repo \
  --discovery-exclude "docs/generated/**" \
  --discovery-include "docs/archive/current-release/**"
```

Apply one-off user overrides when building a case file:

```sh
craik case build task_review_docs \
  --discovery-exclude "docs/drafts/**" \
  --discovery-include "docs/archive/current-release/**"
```

Include rules restore matching paths even when a default exclude would normally
skip them. Exclude rules add to the default exclusions. Excluded paths are
reported in `context_budget.docs_excluded` with the matching rule so an agent can
see what was skipped and why.

The current estimator is intentionally conservative and path-based. Later case assembly work should replace it with content-aware budgeting as repo, memory, GitHub, and handoff adapters mature.
