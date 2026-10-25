# Feature: Remove the unreviewed Dependabot auto-merge

**Branch:** security/remove-dependabot-auto-merge
**Date:** 2026-10-25

## Summary

Deletes `.github/workflows/dependabot-auto-merge.yml`. `merge-when-clean.yml` now merges Dependabot PRs.

## Motivation

The old workflow merged Dependabot patch and minor PRs once checks passed, with no review. `merge-when-clean.yml` (template v2) also needs a real review on the head (CodeRabbit "Review completed" or `review-failover` success) and 0 open threads, and it skips major bumps. Two merge paths for the same PRs meant the review gate could be skipped.

## What changed

- Removed `.github/workflows/dependabot-auto-merge.yml`.
- `docs/review.md` and `CONTRIBUTING.md` now describe the merge-when-clean path only.
