# Companion App Security

Companion app surfaces are governed operator surfaces. They can expose status,
review notifications, and explicit operator-triggered actions, but they must not
become unreviewed background automation channels.

Use the companion security guide with:

- [Desktop Companion App Decision](../reference/desktop-companion.md);
- [Mobile Companion App Decision](../reference/mobile-companion.md);
- [Voice Input And Output Posture](../reference/voice-posture.md);
- [Multimodal Artifact References](../reference/multimodal-artifacts.md);
- [Accessibility Requirements](../reference/accessibility-requirements.md).

## Credential Handling

Companion surfaces must not store secrets or credentials. If a companion action
needs authority, it should reference an existing policy envelope, capability
grant, or approval record rather than caching credentials.

Companion records may preserve:

- policy envelope ids;
- capability grant ids;
- approval receipt ids;
- evidence ids;
- task ids;
- sanitized summaries.

Companion records must not preserve raw tokens, passwords, API keys, private
payloads, unredacted prompts, or credential-bearing URLs.

## Local Storage

Desktop and mobile companion state must be encrypted when persisted. Stored
records should be minimal and reconstructable from durable Craik records.

Allowed companion state includes:

- user-visible notification ids;
- last-viewed task ids;
- display preferences;
- redacted artifact references;
- receipt ids for actions already recorded.

Prohibited companion state includes:

- secrets or credentials;
- raw multimodal payloads;
- private local workspace paths;
- unredacted transcripts;
- generated speech payloads;
- raw canvas state that can expose private content.

## Notifications

Companion notifications require operator controls. Operators must be able to
disable, filter, or defer notifications. Notifications should link back to
reviewable Craik records instead of embedding private content.

Notification payloads should contain:

- task id;
- short sanitized summary;
- severity or review state;
- receipt or evidence id when available.

Notification payloads should not contain raw prompts, secrets, private
transcripts, raw media metadata, or local-only paths.

## Approvals And Actions

Companion-triggered actions require explicit operator intent. Background actions
must be disabled unless a later product surface defines a reviewable action
queue with policy and receipt guarantees.

Every companion-triggered action should preserve:

- actor identity;
- policy envelope id;
- evidence ids;
- receipt id;
- action summary;
- result status.

Mobile offline action queues are deferred unless they can guarantee receipts,
ordering, replay protection, and operator review before side effects occur.

## Redaction Boundary

Companion surfaces use the same redaction posture as other Craik runtime
records. They preserve ids and summaries rather than raw payloads.

Redact:

- secrets and credentials;
- local-only paths;
- private prompts;
- raw transcripts;
- raw audio, image, video, or generated speech payloads;
- raw canvas state;
- private notification payloads.

## Validation

Safe checks for companion security changes:

```sh
uv run --extra dev pytest tests/test_desktop_companion.py tests/test_mobile_companion.py
uv run --extra dev pytest tests/test_voice_posture.py tests/test_multimodal_artifacts.py
uv run --extra dev pytest tests/test_accessibility.py tests/test_docs.py
```

Expected successful output includes:

```text
passed
```
