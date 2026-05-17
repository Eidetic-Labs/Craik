# Changelog

All notable Craik release changes are tracked here. Craik's first public
release target is a robust `0.x.0` MVP; `1.0.0` remains a later compatibility
signal after real-world usage and security soak.

This project follows the shape of Keep a Changelog and uses semantic versioning
within the `0.x.0` stability expectations described in
`docs/guides/release-management.md`.

## Unreleased

### Added

- Next MVP hardening work after the first live provider path.

## 0.1.0 - 2026-05-17

### Added

- Live provider transport path with stdlib HTTP, explicit live access, retries,
  cancellation, streaming callback capture, and recorded chat-completions
  integration coverage.
- Provider adapters for OpenAI Responses, Anthropic Messages, and
  OpenAI-compatible Chat Completions, including local `/v1` provider metadata.
- Secret reference resolution for provider credentials without storing raw
  secret material in transport instances.
- Governed loop support for dispatchable provider tool calls and replayable
  streaming output chunks.

## 0.0.0 - 2026-05-16

### Added

- Initial pre-release package metadata.
- Local CLI entrypoint and source-tree installation path.
