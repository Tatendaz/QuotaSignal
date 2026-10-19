# Session: Project page on GitHub Pages

**Branch:** feat/project-page
**Date:** 2026-10-20

## Prompts

1. "Build a GitHub Pages project page for the public repo Tatendaz/QuotaSignal, ship it through a PR, and turn Pages on."
2. "Problems to fix first: the repo has no GitHub description; the latest Dependabot CI run failed: find why."

## Work

Set the repository description from the README. Read the failed Dependabot run: the auto-merge job stops at `gh pr checks --required` with "no required checks reported", because `main` has no ruleset with required checks and repository auto-merge is off. `docs/review.md` already says the workflow needs both settings, and the open-source feature entry left those settings for the owner to approve. The app CI on the Dependabot PRs passed.

Read the claude-usage and yapui project pages and copied their structure, tokens, and theme toggle. Wrote the page from the README, `docs/`, the changelog, the roadmap, and the source. Checked the stale marker in `core.py` and `tray.py` (it is a trailing `~`) and the 60-second refresh in `tray.py`. Rendered the social preview with headless Chrome.

## Decisions

- Green accent instead of claude-usage's orange, so the two tools are told apart while the layout stays the same.
- The repo's own SVGs (menu illustration, architecture diagram) are reused in place; the page swaps the light and dark versions with the theme toggle.
- No ruleset or auto-merge change: those are repository settings that need the owner's approval.
