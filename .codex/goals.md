# Active Goal

Continue the Craik roadmap workflow without stopping until all tasks through v0.13.0 are complete.

Do not stop after issue, PR, merge, cleanup, or section checkpoints. Stop only for an unrecoverable blocker, a failing CI state that cannot be diagnosed or fixed with available access, missing permissions that cannot be recovered, or explicit user instruction.

For every issue: implement the scoped change, run local checks, open a non-draft PR with a standard title and `Closes #NN`, verify the PR closes successfully through CI and merge, delete stale local and remote branches, update local `main`, record Stigmem facts, then continue to the next issue. When a section is complete, stage the next section and repeat.
