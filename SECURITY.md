# Security Policy

Craik is pre-release software. Security-sensitive behavior should be designed conservatively because the runtime is expected to interact with agents, tools, shell commands, Git repositories, GitHub, secrets, and Stigmem memory.

## Supported Versions

Craik has no supported release line yet.

| Version | Supported |
| --- | --- |
| pre-0.1.0 | No formal support; best-effort private disclosure |

This table should be updated when the first package release is published.

## Reporting a Vulnerability

Do not open public GitHub issues for security vulnerabilities.

Report privately to:

security@eideticlabs.ai

Include:

- affected version or commit,
- environment,
- reproduction steps,
- expected impact,
- whether secrets, tokens, repositories, or memory facts may be exposed,
- and any suggested mitigation.

## Expected Response

Until Craik has a staffed security process, response is best effort. The intended target process is:

- acknowledge within 5 business days,
- assess severity and scope,
- coordinate a fix privately when appropriate,
- credit reporters when requested and appropriate,
- and publish advisories for released versions when needed.

## Security-Sensitive Areas

Please report issues involving:

- command execution,
- file write boundaries,
- GitHub write operations,
- token or API key handling,
- memory scope leaks,
- Stigmem fact visibility,
- prompt or context injection that bypasses policy,
- capability grant bypass,
- receipt redaction failures,
- plugin sandbox failures,
- and unsafe default configuration.

## Safe Harbor

Good-faith research that avoids privacy violations, data destruction, service disruption, and public disclosure before remediation will be treated as helpful security research.
