"""Runtime services for Craik."""

from __future__ import annotations

import sys

from craik.runtime.channels import allowlist, identity, messaging, policy

_LEGACY_MODULE_ALIASES = {
    "craik.runtime.channel_allowlist": allowlist,
    "craik.runtime.channel_identity": identity,
    "craik.runtime.channel_policy": policy,
    "craik.runtime.messaging_channel": messaging,
}

for _legacy_name, _module in _LEGACY_MODULE_ALIASES.items():
    sys.modules.setdefault(_legacy_name, _module)

del _legacy_name, _module
