# Session: merge-when-clean template v4

**Branch:** security/merge-when-clean-v4
**Date:** 2026-10-25

## Prompts

1. Security sweep coordinator: "templates/merge-when-clean.yml is now v4 ... Repos already merged with v2/v3: open one small follow-up PR to v4."

## Work

Checked the template's sha256 (`f0c005a3...`) and copied it unchanged. Ran `actionlint` and `zizmor`. Completed the gate list in `docs/review.md`, which the backup review on #10 flagged as missing two gates.
- Coordinator update: replaced v4 with v5 (sha256 `1c493dd7...`), which adds `set +e` after `set -uo pipefail`.
