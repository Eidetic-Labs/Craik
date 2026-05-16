# Plugin Receipts

Plugin receipts record plugin actions and outputs under policy.

The `craik.plugin_receipt` contract links a plugin action to:

- task and actor;
- plugin descriptor and optional probation record;
- capability grants;
- trust boundary;
- redacted result summary;
- evidence and handoff records.

Plugin receipts must be redacted and must keep descriptor identity separate from
runtime authority. Capability grants show why the action was allowed, while the
receipt records what happened.

## Outcomes

Receipts use the shared receipt status values. Common plugin outcomes are:

- `passed`: the plugin action completed successfully;
- `failed`: the plugin action ran but did not complete successfully;
- `denied`: policy or missing authority blocked the action.

Successful, failed, and denied plugin receipts still require evidence and handoff
links so reviewers can reconstruct the action boundary without reading raw
plugin output.
