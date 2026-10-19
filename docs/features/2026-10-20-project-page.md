# Feature: Project page on GitHub Pages

**Branch:** feat/project-page
**Date:** 2026-10-20

## Summary

Adds a one-page project site at `docs/index.html`, served by GitHub Pages from `main:/docs` at https://tatendaz.github.io/QuotaSignal/.

## Motivation

The repository had no page outside GitHub. The other project pages (claude-usage, yapui) share one layout, and QuotaSignal now matches them.

## What changed

- `docs/index.html`: what QuotaSignal does, who it is for, the menu illustration and the architecture diagram from the repo, notifications, how it works, the README install steps, status and limits, a link to claude-usage, and a footer. Light and dark mode follow the system, with a toggle.
- `docs/index.md`: the same content as Markdown, linked with `rel="alternate"`.
- `docs/404.html`, `docs/.nojekyll`, and `docs/social-preview.png` (1280x640, for Open Graph and X cards).
- README: a link to the project page in the documentation table.

## Notes

All copy comes from the README, `docs/`, the changelog, the roadmap, and the source. The menu image is still labeled as an illustration. The app code is unchanged. `.nojekyll` means the Markdown files under `docs/` are served as plain text instead of rendered by Jekyll.
