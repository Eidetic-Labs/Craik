# Memory Diffs

Craik memory diffs explain how memory changed during a task.

Print a diff for a task:

```sh
craik memory diff task_review_docs
```

The diff records:

- proposals created during the task,
- proposals approved,
- proposals rejected,
- facts written,
- write failures,
- and facts read into the task context.

The current implementation derives proposal activity from local state. Later runner and Stigmem workflows can attach fact reads, direct writes, and write failures to the same `craik.memory_diff` contract.

Diffs are persisted in the local store so handoffs and future receipts can reference them.
