# Accessibility Requirements

Multimodal and companion surfaces must remain usable without relying on a
single input mode, visual presentation, or motion pattern.

`AccessibilityRequirements` records:

- surface kind: `desktop_companion`, `mobile_companion`, `visual_workspace`, or
  `voice`;
- keyboard navigation;
- screen reader labels;
- reduced motion support;
- contrast checks;
- transcript availability;
- caption availability;
- notification controls;
- policy envelope id;
- evidence ids;
- receipt ids.

`accessibility_check` returns a reviewable result with missing requirement names
when a surface does not meet the baseline.

## Baseline

Companion and visual workspace surfaces should provide:

- complete keyboard navigation for controls;
- meaningful labels for screen readers;
- reduced-motion behavior for animated or live surfaces;
- contrast checks for text, controls, and status indicators;
- transcripts for voice or audio interactions;
- captions for video or generated speech playback;
- operator controls for notifications.

Accessibility reviews must preserve policy, evidence, and receipt links so the
decision can be audited later.

## Boundary

Accessibility checks do not approve product surfaces by themselves. They provide
evidence for [Desktop Companion App Decision](desktop-companion.md),
[Mobile Companion App Decision](mobile-companion.md), and
[Live Visual Workspace Decision](visual-workspace.md).
