# Multimodal Artifact References

Multimodal artifact references let Craik workflows cite audio, image, video,
transcript, canvas, document, and other media without embedding raw media
payloads in portable records.

`MultimodalArtifactReference` records:

- artifact id;
- task id;
- kind: `audio`, `image`, `video`, `transcript`, `canvas`, `document`, or
  `other`;
- locator kind: `artifact_id`, `content_hash`, `url`, `relative_path`, or
  `external_ref`;
- locator;
- media MIME type;
- redacted media metadata;
- policy envelope id;
- evidence ids;
- receipt ids;
- redacted paths;
- redaction status;
- creation timestamp.

## Portability

Artifact references store locators, not raw media payloads. `relative_path`
locators must be portable relative paths, not absolute local filesystem paths.

Use artifact ids or content hashes when a record must survive machine moves.
Use URLs only when the URL is already safe to persist and does not carry
credentials or private query parameters.

## Redaction Boundary

Media metadata must not persist raw audio, raw image data, raw video data, media
bytes, private metadata, credentials, tokens, or private payloads. The reference
builder redacts secret-like values and replaces private media payload fields
with `[REDACTED]`.

Artifact references preserve evidence, receipt, and policy links so later
speech, visual workspace, accessibility, and review surfaces can audit how the
artifact entered the workflow.
