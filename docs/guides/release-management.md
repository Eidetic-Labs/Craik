# Release Management

Craik's first public package target is a robust `0.x.0` MVP, not `1.0.0`.
The `0.x.0` series can still change contracts between minor releases, but each
published release must be installable, documented, and recoverable.

## Release Cadence

Use minor releases for MVP capability increments and patch releases for fixes.
Do not publish a release only because changes have accumulated. Publish when the
roadmap gate for that release has completed, CI is green, and release notes are
reviewed.

Recommended cadence:

- `0.x.0`: capability-bearing MVP milestones;
- `0.x.y`: bug, docs, packaging, compatibility, and security patches;
- `1.0.0`: deferred until compatibility promises, upgrade paths, and real-world
  security soak justify the stability signal.

## Tag Policy

Release tags use `vMAJOR.MINOR.PATCH`, for example `v0.1.0`.

Before tagging:

1. Update `pyproject.toml`, `src/craik/__init__.py`, and `docs/package.json`.
2. Move relevant `CHANGELOG.md` entries from `Unreleased` into the target
   version section.
3. Run package, docs, quality, and version checks.
4. Open a release PR that links the completed roadmap issue.
5. Tag only the merge commit from the release PR.

## Release Notes

Every release needs a GitHub release entry and a matching `CHANGELOG.md`
section. Release notes must include:

- user-facing additions and fixes;
- migration notes and compatibility risks;
- provider, policy, persistence, and receipt changes;
- known limitations that remain after the release;
- links to the closing issues and release PR.

## Package Verification

Package artifacts are built in CI by the Package workflow. That workflow checks
version consistency, validates release-process docs, builds `sdist` and wheel
artifacts, runs `twine check`, smoke-installs the wheel, and uploads the build
artifacts for inspection.

Local equivalent:

```sh
python scripts/check_version_consistency.py
python scripts/check_release_readiness.py
python -m build
python -m twine check dist/*
```

## PyPI Publishing

Publishing is handled by the Publish workflow. Manual dispatch builds and
validates artifacts only. PyPI publication runs only from the immutable release
tag, currently `v0.1.0`, after the workflow verifies that the tag, package
version, and changelog all agree.

Publishing requires the `pypi` Protected Environment. The environment should
require reviewer approval and should use trusted publishing through GitHub OIDC
instead of stored PyPI tokens.

## Protected Environment

Configure the `pypi` Protected Environment before the first public release:

- require at least one maintainer approval;
- restrict the workflow to protected branches and release tags;
- keep PyPI trusted publisher configuration aligned with
  `eidetic-labs/craik`;
- do not store long-lived PyPI credentials in repository secrets.

## Rollback

PyPI releases are immutable from the perspective of dependent users. If a bad
release ships, publish a patch release with a clear changelog entry and GitHub
release note. Yank only when installation of the bad artifact is actively
harmful.
