# Voice Input And Output Posture

Craik treats voice input and output as governed operator surfaces, not as an
always-on assistant layer.

`VoiceSurface` records:

- surface id;
- direction: `input`, `output`, or `bidirectional`;
- support level: `supported`, `experimental`, or `deferred`;
- consent requirement;
- policy context preservation;
- evidence link preservation;
- receipt requirement;
- transcript redaction;
- media metadata redaction;
- raw audio payload persistence posture;
- documentation reference.

## Decision Rules

`voice_posture_decision` allows a supported voice surface only when it preserves:

- explicit operator consent;
- transcript redaction;
- media metadata redaction;
- policy context;
- evidence links;
- receipts.

Experimental voice surfaces require explicit review before use. Deferred voice
surfaces are not available as product surfaces.

Voice surfaces are blocked when they persist raw audio payloads, skip explicit
operator consent, omit transcript or media metadata redaction, lose policy or
evidence links, or skip receipts.

## Redaction Boundary

Voice records should preserve ids and summaries instead of raw audio or private
transcripts. Safe records can include:

- transcript id;
- media artifact reference id;
- evidence ids;
- receipt ids;
- policy envelope id;
- adapter id;
- redaction status;
- short review summary.

Voice records must not persist raw audio payloads, credentials, private prompts,
private transcripts, local-only paths, or unredacted generated speech metadata.

## Current Posture

Voice support is a governed extension point. Supported surfaces must pass the
decision rules above. Experimental surfaces require explicit review, and
always-on or raw-audio-retaining assistant behavior is deferred unless a later
roadmap gate adds stronger product and security requirements.
