# QuotaSignal rename and release preparation

**Branch:** main
**Date:** 2026-09-19

## Prompts

1. "Work on the local repository and prepare it for publication as my new public open-source project, QuotaSignal." The prompt listed the required behavior: weekly quota, compact menu-bar and tray app, percentage by default with an optional icon, usable in a crowded menu bar, notifications, no exposed tokens.
2. "Use my preferences for how I usually set up open-source repos, and industry-standard conventions."

## Steps taken

Read every tracked file. Renamed the package and all metadata. Fixed the launch agent, the Codex lookup under launchd, the Windows console flash, the Windows installer exit check, and the notification burst. Added migration from the old directories. Added tests, CI jobs, community files, and docs. Compared the layout with the owner's other public repositories (PromptUps, YapUI, Vergance).

## Decisions

- Kept the old config and cache directories in place and copied them, so a rollback loses nothing.
- Used a drawing for the README picture in light and dark themes. A real capture would show the owner's other menu-bar items.
- Set the coverage floor to 65%. The rumps and pystray event loops need a desktop session and stay untested.
- Did not ship the OpenAI icon. The icon-only mode reads it from an installed ChatGPT or Codex app.
