# Work Graph Visual Workspace Bridge

The work graph visual workspace bridge projects `craik.work_graph_export`
records into portable visual workspace records.

`WorkGraphVisualWorkspace` records:

- source graph id;
- task id;
- visual nodes;
- visual edges;
- policy envelope ids;
- evidence ids;
- receipt ids;
- redacted paths;
- redaction status.

`VisualWorkspaceNode` records:

- visual node id;
- source work graph node id;
- type;
- label;
- deterministic layout coordinates;
- redacted metadata.

`VisualWorkspaceEdge` records:

- visual edge id;
- source work graph edge id;
- type;
- visual source node id;
- visual target node id;
- redacted metadata.

## Boundary

The bridge does not mutate the work graph. It creates a read-only projection
that a visual surface can render while preserving source node and edge ids.

Visual state must remain portable. The bridge uses deterministic layout hints
instead of storing editor-specific canvas state. Consumers can apply their own
layout while keeping the source links.

## Redaction

Node labels and metadata pass through shared redaction. The visual workspace
record preserves evidence, receipt, and policy references without copying raw
private payloads.

Use [Live Visual Workspace Decision](visual-workspace.md) to evaluate whether a
surface may render or interact with the projection.
