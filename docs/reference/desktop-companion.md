# Desktop Companion App Decision

Craik treats desktop companion apps as governed operator surfaces. A desktop
companion may present status, notifications, and controlled actions, but it must
not become an unreviewed background automation channel.

`DesktopCompanionSurface` records:

- surface id;
- support level: `supported`, `experimental`, or `deferred`;
- operator consent requirement;
- policy context preservation;
- evidence link preservation;
- receipt requirement;
- local storage encryption posture;
- secret storage posture;
- notification controls;
- background action controls;
- documentation reference.

## Decision Rules

`desktop_companion_decision` allows a supported surface only when it preserves:

- explicit operator consent;
- encrypted local storage;
- notification controls;
- background action controls;
- policy context;
- evidence links;
- receipts.

Experimental desktop companion surfaces require explicit review. Deferred
surfaces are not available as product surfaces.

Desktop companion surfaces are blocked when they store secrets, skip operator
consent, use unencrypted local storage, omit notification controls, allow
uncontrolled background actions, lose policy or evidence links, or skip
receipts.

## Current Posture

Desktop companion support is a governed extension point. Status panels,
reviewable notifications, and explicit operator-triggered actions can be
supported when they satisfy the controls above.

Always-on desktop automation, secret caching, uncontrolled background actions,
and private local-state synchronization are deferred unless a later roadmap gate
adds stronger product and security requirements.
