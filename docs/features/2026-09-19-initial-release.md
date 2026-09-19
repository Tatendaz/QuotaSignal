# Initial Codex Usage release

**Branch:** main
**Date:** 2026-09-19

## Summary

Adds a cross-platform status app and plugin that displays the shared ChatGPT and Codex account quota.

## Motivation

Users need to see weekly remaining usage while they work without repeatedly opening the usage dashboard or a Codex status screen.

## What changed

- Added the weekly percentage on macOS with an optional adaptive OpenAI provider icon. The compact
  percentage-only and icon-only display modes avoid menu overflow.
- Added a startup notification with the current weekly quota so a crowded menu bar cannot make a
  successful launch look like a failure.
- Added live weekly and session quota reads through the authenticated local Codex app server.
- Added cached fallback values and configurable threshold notifications.
- Added portable ChatGPT/Codex plugin metadata and an installation skill.
- Added macOS and Windows login-startup installers.
- Added tests, packaging metadata, CI, and open-source documentation.

## Notes

The first release reads the account-wide quota shared by ChatGPT and Codex. It does not access stored authentication tokens directly.
