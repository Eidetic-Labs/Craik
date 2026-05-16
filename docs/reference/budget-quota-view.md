# Budget And Quota View

The budget and quota view is a read-only operator display for configured limits,
observed usage, missing data, exceeded limits, and notes.

The v0.8.0 TUI surface formats:

- configured limits;
- usage summaries;
- missing data;
- exceeded limits;
- notes.

## Missing Data

Craik must not invent unavailable cost data. If a run or local store does not
contain cost, token, request, or quota information, the view should show the
missing key explicitly.

## Exceeded State

Exceeded states are only shown when supported data exists. The view can display
that a limit was exceeded, but it does not enforce limits or mutate policy.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
