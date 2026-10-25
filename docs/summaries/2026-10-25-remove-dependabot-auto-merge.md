# Session: Remove the unreviewed Dependabot auto-merge

**Branch:** security/remove-dependabot-auto-merge
**Date:** 2026-10-25

## Prompts

1. Security sweep follow-up: "dependabot-auto-merge.yml merges Dependabot PRs with no review, which skips the review gate; merge-when-clean v2 covers Dependabot now. Open one small PR per repo that deletes it."

## Work

Deleted the workflow. Searched the repo for references and updated `docs/review.md` and `CONTRIBUTING.md`. Ran `actionlint` and `zizmor` on the remaining workflows.
