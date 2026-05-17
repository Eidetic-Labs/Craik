# Text-To-Speech Adapter Contract

Text-to-speech adapters convert redacted text requests into referenced generated
speech artifacts while preserving Craik's policy, evidence, and receipt model.

`TextToSpeechRequestMetadata` records:

- redacted text summary;
- voice id;
- language;
- speaking rate;
- redacted metadata.

`TextToSpeechArtifact` records:

- media artifact id;
- media MIME type;
- duration in milliseconds;
- byte count;
- redacted metadata;
- redaction status.

`TextToSpeechResult` records:

- result id;
- task id;
- adapter id;
- status: `completed`, `partial`, or `failed`;
- request metadata;
- generated artifact reference;
- errors;
- policy envelope id;
- evidence ids;
- receipt ids;
- redacted paths;
- creation timestamp.

## Validation

Completed and partial results require a generated artifact reference. Failed
results require at least one error. All results require policy envelope,
evidence, and receipt links.

## Redaction Boundary

Text-to-speech results must not persist raw prompts, private payloads, adapter
request payloads, raw generated speech, responses, credentials, tokens, or media
metadata that should remain private.

Adapters should preserve artifact ids, redacted summaries, evidence ids, and
receipt ids instead of embedding generated speech payloads. Use
[Voice Input And Output Posture](voice-posture.md) to evaluate whether a voice
surface may call an adapter.
