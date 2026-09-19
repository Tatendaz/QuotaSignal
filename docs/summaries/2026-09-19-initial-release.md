# Initial Codex Usage release

**Branch:** main
**Date:** 2026-09-19

## Prompts

1. "Create a Codex plugin in my Projects folder that shows weekly remaining usage in the macOS menu bar and Windows status area."
2. "Call the project Codex Usage, like Claude Usage."
3. "Show weekly usage as it happens and add notifications."
4. "Make it open source on my GitHub and compatible with ChatGPT as well as Codex."

## Steps taken

Created the portable and Codex-compatible plugin manifests, implemented a Python quota reader using the local Codex app-server protocol, added macOS and Windows status UIs, notifications, tests, documentation, and GitHub workflows.

## Decisions

- Reused the existing Codex login through the local app server so the project never handles tokens.
- Displayed remaining percentage because it answers how much usable quota is left.
- Used native lightweight Python adapters for macOS and Windows and kept quota parsing dependency-free.
- Showed the percentage without an icon by default to reduce menu-bar width. A remembered control
  can switch to the installed app's native template icon without making the item wider.
- Added one startup notification that confirms the app is running and explains menu-bar overflow.
