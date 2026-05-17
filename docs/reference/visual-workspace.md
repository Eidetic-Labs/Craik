# Live Visual Workspace Decision

Craik treats visual workspaces and canvases as governed operator surfaces over
existing work records. A visual workspace may make work graph state easier to
scan, but it must not become an unreviewed mutation layer.

`VisualWorkspaceSurface` records:

- surface id;
- support level: `supported`, `experimental`, or `deferred`;
- read-only posture;
- work graph link preservation;
- evidence link preservation;
- receipt requirement;
- visual state redaction;
- accessibility controls;
- raw canvas payload persistence posture;
- documentation reference.

## Decision Rules

`visual_workspace_decision` allows a supported surface only when it preserves:

- read-only graph inspection;
- visual state redaction;
- accessibility controls;
- work graph links;
- evidence links;
- receipts.

Experimental visual workspace surfaces require explicit review. Deferred
surfaces are not available as product surfaces.

Visual workspace surfaces are blocked when they persist raw canvas payloads,
mutate workflow state, skip visual state redaction, omit accessibility controls,
lose work graph or evidence links, or skip receipts.

## Current Posture

Read-only visual work graph views can be supported when they satisfy the
controls above.

Live mutating canvases, raw visual state persistence, and canvas-driven workflow
mutation are deferred until a later bridge defines explicit policy, evidence,
receipt, and accessibility behavior.
