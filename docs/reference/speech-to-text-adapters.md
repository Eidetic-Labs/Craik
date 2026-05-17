# Speech-To-Text Adapter Contract

Speech-to-text adapters convert referenced audio artifacts into redacted
transcripts while preserving Craik's policy, evidence, and receipt model.

`SpeechToTextInputMetadata` records:

- media artifact id;
- media MIME type;
- duration in milliseconds;
- language hint;
- channel count;
- redacted metadata.

`SpeechToTextTranscript` records:

- transcript text;
- language;
- confidence;
- transcript segments;
- redacted metadata;
- redaction status.

`SpeechToTextResult` records:

- result id;
- task id;
- adapter id;
- status: `completed`, `partial`, or `failed`;
- input metadata;
- transcript;
- errors;
- policy envelope id;
- evidence ids;
- receipt ids;
- redacted paths;
- creation timestamp.

## Validation

Completed and partial results require a transcript. Failed results require at
least one error. All results require policy envelope, evidence, and receipt
links.

Transcript segments can carry start and end offsets. When both offsets are
present, the end must be greater than or equal to the start.

## Redaction Boundary

Speech-to-text results must not persist raw audio payloads, audio bytes,
waveforms, raw payloads, private transcript metadata, credentials, tokens, or
private local state.

Adapters should preserve media artifact ids and transcript summaries instead of
embedding raw audio. Use [Voice Input And Output Posture](voice-posture.md) to
evaluate whether a voice surface may call an adapter.
