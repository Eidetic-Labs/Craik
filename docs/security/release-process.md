# Security Release Process

Craik security releases use the same package gates as normal releases with
private coordination before disclosure.

## Security Patch Flow

1. Triage the report privately and record the impacted versions.
2. Open a private fix branch or security advisory branch.
3. Add regression tests that fail without the fix.
4. Run quality, package, docs, and security checks.
5. Publish the smallest viable `0.x.y` patch release.
6. Publish advisory details after patched artifacts are available.

## Private Coordination

Do not disclose exploit details in public issues, public PR titles, changelog
drafts, or generated docs before patched packages are available. Use GitHub
Security Advisories or a private maintainer channel for coordination.

## Release Notes

Security release notes should state:

- affected versions;
- fixed version;
- severity and impact in user terms;
- mitigation if users cannot upgrade immediately;
- whether secrets, receipts, local state, provider calls, or memory writes may
  have been exposed.

## Disclosure

Disclosure should happen after:

- the patch release is published to PyPI;
- GitHub release notes are live;
- the changelog is updated;
- any required advisory or CVE entry is ready.

## Post-Release Verification

After release, install the patched package from PyPI in a clean environment and
run the relevant regression tests or smoke workflow. Confirm that docs and
release notes point to the fixed version.
