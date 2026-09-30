# Security Policy

Report security problems through [GitHub's private advisory form](https://github.com/Tatendaz/QuotaSignal/security/advisories/new), not public issues. Include the affected version, reproduction steps, and impact. Reports are reviewed by @Tatendaz. This is a single-maintainer project with no response-time guarantee.

## Supported versions

| Version | Security fixes |
| --- | --- |
| 0.1.x and the default branch | Supported |
| Older development snapshots | Upgrade to 0.1.x |

## Credential and data promises

1. QuotaSignal requests quota only from `codex app-server` using `account/rateLimits/read`.
2. It does not open Codex or ChatGPT authentication files or persist authentication tokens.
3. The quota cache and JSON output contain percentages, reset timestamps, and a plan label, without account identifiers.
4. The app makes no network requests of its own and has no telemetry. The Codex CLI handles account access using the user's existing login.
5. Cache, notification state, and display preference files use user-only permissions where the operating system supports them. Quitting stops quota polling.

Token exposure, account identifiers written to the quota cache, unintended network requests, and unauthorized code execution are vulnerabilities. Quota inaccuracies, a hidden menu item, unsigned build warnings, and upstream service downtime are ordinary bugs unless they create a security impact. Report dependency vulnerabilities upstream and privately describe how they affect this app.
