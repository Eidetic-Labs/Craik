# Mobile Companion App Decision

Craik treats mobile companion apps as governed operator surfaces. A mobile
companion may expose review notifications and explicit operator-triggered
actions, but it must not become a credential cache or uncontrolled remote
automation channel.

`MobileCompanionSurface` records:

- surface id;
- support level: `supported`, `experimental`, or `deferred`;
- operator consent requirement;
- policy context preservation;
- evidence link preservation;
- receipt requirement;
- credential storage posture;
- encrypted device storage posture;
- push notification controls;
- remote action controls;
- offline action controls;
- documentation reference.

## Decision Rules

`mobile_companion_decision` allows a supported surface only when it preserves:

- explicit operator consent;
- encrypted device storage;
- push notification controls;
- remote action controls;
- offline action controls;
- policy context;
- evidence links;
- receipts.

Experimental mobile companion surfaces require explicit review. Deferred
surfaces are not available as product surfaces.

Mobile companion surfaces are blocked when they store credentials, skip
operator consent, use unencrypted device storage, omit push notification
controls, allow uncontrolled remote or offline actions, lose policy or evidence
links, or skip receipts.

## Current Posture

Mobile companion support is a governed extension point. Reviewable
notifications and explicit operator-triggered actions can be supported when
they satisfy the controls above.

Always-on mobile automation, credential storage, uncontrolled remote actions,
and offline action queues without receipts are deferred unless a later roadmap
gate adds stronger product and security requirements.
