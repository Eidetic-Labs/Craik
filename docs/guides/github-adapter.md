# GitHub Adapter

Craik can load read-only GitHub context into case files.

The adapter reads:

- repository metadata,
- open issues,
- open pull requests,
- changed files for open pull requests,
- and commit status for the local Git `HEAD`.

Build a case file with GitHub context:

```sh
craik case build task_review_docs
```

Build without GitHub network access:

```sh
craik case build task_review_docs --no-github
```

GitHub context is stored in the case file `github_state` field. If the project remote is not a GitHub repository, the API is unavailable, auth fails, or rate limits block reads, Craik records a warning and leaves an assumption instead of failing the case-file build.

GitHub writes are not part of the read adapter. Creating issues, comments, branches, or pull requests requires future guarded write workflows and explicit capability grants.
