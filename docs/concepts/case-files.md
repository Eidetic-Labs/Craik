# Case Files

Case files are task-specific context packages assembled before an agent acts.

A case file gives the next runtime step a durable view of:

- the task objective,
- the policy envelope id,
- the intent lock id,
- repository state,
- relevant docs and immutable docs,
- evidence references,
- assumptions that still need review,
- stale-risk markers,
- missing context,
- and context budget metadata.

Case files are not memory stores and they are not transcripts. They are bounded work packets that make the starting point of a task explicit and reviewable.

## Current Implementation

Craik can build local case files from persisted task and project profiles:

```sh
craik case build task_docs_reconcile
```

The local assembler includes:

- Git branch, head, clean/dirty status, default branch, remote or local repo identifier, and immutable path configuration,
- an intent lock id for accepted scope boundaries,
- documentation files discovered from the project profile,
- ADR or immutable documentation files labeled separately,
- evidence references for the task, project, repo status, docs, and immutable docs,
- assumptions for missing memory facts and GitHub state,
- stale-risk markers,
- and deterministic context budget metadata.

Case files are persisted as `craik.case_file` records in the local SQLite store.

## Evidence

Every case file should explain where its context came from. Local evidence references use `craik.evidence_reference` records embedded in the case file.

Immutable documentation is marked in evidence metadata:

```json
{
  "metadata": {
    "immutable": true
  }
}
```

## Assumptions

Unsupported conclusions must stay assumptions. The local assembler records open assumptions when context is unavailable, such as memory facts or GitHub issue state before those adapters are implemented.

Agents should review assumptions before acting and avoid promoting them to facts without evidence.

## Current Scope

The local assembler can load read-only GitHub issues and pull requests when a GitHub remote is configured. It does not yet load Stigmem facts, recent handoffs, or contradiction reports. Those planned adapter layers will extend the same case file contract.
