# Evidence And Assumptions

Craik separates evidence from assumptions.

Evidence is source material the runtime can cite. Assumptions are unresolved claims that should not be treated as facts yet.

## Evidence References

The local case assembler creates evidence references for:

- the task request,
- the project profile,
- repository status,
- discovered documentation files,
- and discovered immutable documentation files.

Each evidence reference includes a source, kind, locator, summary, and optional metadata.

## Assumption Ledger

The local case assembler records assumptions when expected context is missing.

Current examples:

- memory facts were not loaded,
- GitHub issue or pull request state was not loaded,
- no mutable documentation files were discovered,
- or some documentation was omitted by the context budget.

Agents should not promote assumptions to memory or documentation claims unless later evidence supports them.

## Immutable Documentation

Immutable documentation, such as ADRs, can be included as evidence without authorizing edits. Case files label immutable documentation separately in `adrs` and mark matching evidence with `metadata.immutable = true`.
