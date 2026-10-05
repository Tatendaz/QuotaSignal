# Feature: Public QuotaSignal repository

**Branch:** chore/open-source
**Date:** 2026-10-01

Prepare QuotaSignal for public GitHub use with an MIT license, a concise README, a documented data boundary, community policies, and reproducible architecture diagrams.

CI tests Python 3.10 through 3.14 on macOS, Windows, and Linux. Actions are pinned to release commit SHAs, checkout does not retain credentials, and jobs have time limits. The docs gate runs `.github/scripts/require-docs-entry.sh`. Dependabot patch/minor merges require passing required checks.

The app behavior is unchanged. Windows desktop verification and unsigned build limitations remain explicit. GitHub security, metadata, and branch-protection settings require the owner's separate approval.
