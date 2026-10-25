# Feature: merge-when-clean template v4

**Branch:** security/merge-when-clean-v4
**Date:** 2026-10-25

## Summary

Updates `.github/workflows/merge-when-clean.yml` from template v2 to v5 (sha256 `1c493dd7...`), unchanged.

## Motivation

v2 checked "changes requested" only through `reviewDecision`. That field is null here because `main` does not require reviews, so a changes-requested review did not block. v4 blocks on any reviewer's latest `CHANGES_REQUESTED` review. It also adds an optional `.github/merge-hold-paths` file (one regex per line). A bad regex there makes the job merge nothing. It also removes `tr | grep -q` pipes that could turn a match into a pass under `pipefail`.

## What changed

- `.github/workflows/merge-when-clean.yml`: template v4.
- `docs/review.md`: the merge gate list is now complete (other commit statuses, merge conflicts, label/path skips, hold file).

## Notes

This repo has no `.github/merge-hold-paths`, so the hold-file feature does nothing here. This PR touches the workflow file itself, so merge-when-clean will not merge it. It is merged by hand under the same rules.

v5 adds `set +e`: GitHub runs `shell: bash` as `bash -e -o pipefail`, so in v4 a grep "no match" (exit 1) killed the job on every PR that was not held.
