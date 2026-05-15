# Maintainer and Release Policy

Craik is currently maintained by Eidetic Labs.

## Project State

Craik is pre-implementation and pre-`0.1.0`. Until the first package release:

- runtime contracts may change,
- command names may change,
- local state format may change,
- storage layout may change,
- and no API compatibility is guaranteed.

## Branch Policy

- `main` is the active development branch.
- Small documentation updates may be committed directly by maintainers.
- Implementation changes should use pull requests once code exists.
- Large design or architecture changes should start with an issue or design note.

## Review Policy

Before merging implementation changes, maintainers should check:

- contract compatibility,
- policy and security implications,
- test coverage,
- documentation updates,
- secret redaction,
- Stigmem boundary correctness,
- and whether the change should update roadmap or feature docs.

## Versioning

Craik should use Semantic Versioning after the first package release.

Before `0.1.0`, compatibility is not guaranteed. After `0.1.0`, breaking changes to persisted schemas should require:

- versioned schema updates,
- migration notes,
- and release notes.

## Release Process

The release process will be finalized before the first package publication.

Expected minimum release steps:

1. Confirm tests, linting, and type checks pass.
2. Update changelog or release notes.
3. Confirm schema versions and migrations.
4. Tag the release.
5. Publish package artifacts.
6. Publish GitHub release notes.

## Security Releases

Security fixes may be prepared privately before public disclosure. See [SECURITY.md](SECURITY.md).

## Maintainer Changes

Maintainer changes should be recorded in this file. Access should be granted only to contributors who have demonstrated consistent judgment around runtime contracts, security boundaries, governance, and project scope.
