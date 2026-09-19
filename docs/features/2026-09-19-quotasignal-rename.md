# QuotaSignal rename and release preparation

**Branch:** main
**Date:** 2026-09-19

## Summary

Renames the project from Codex Usage to QuotaSignal and fixes the problems found in a pre-publication review.

## Motivation

The app was branded QuotaSignal in the menu but `codex-usage` everywhere else: package, command, URLs, manifests, installers, and docs. "Codex" is also an OpenAI product name, which a third-party project should not carry as its own.

## What changed

- Package, command, plugin, skill, launch agent, and install directories are now `quotasignal`. Repository URLs point to `Tatendaz/QuotaSignal`.
- Settings and cache from `codex-usage` are copied to the new directories on first run. `CODEX_USAGE_CODEX_BIN` still works.
- macOS: **Quit** now stays quit. The launch agent used `KeepAlive = true`, so launchd restarted the app at once. It now restarts only after a crash.
- macOS: the installer records the full path of `codex`, and the app also checks `/opt/homebrew/bin` and `/usr/local/bin`. Login items start with a short `PATH` and could not find Codex.
- Windows: the Codex child process starts with `CREATE_NO_WINDOW`, so no console window flashes under `pythonw`. The installer now stops when `--check` fails.
- Notifications: one refresh that crosses several levels sends one notification, not three. A malformed `config.json` falls back to the defaults and no longer raises.
- Windows: the tray icon is now set visible at startup and refreshes every 60 seconds. Before, it refreshed once and pystray left the icon hidden because a custom setup function was used.
- A dead app server is replaced on the next refresh. Before, the app showed the stale value until restart.
- One request has one timeout, even when the server sends other messages. A cache that cannot be written no longer hides a fresh value. A level can fire again after the quota recovers when Codex gives no reset time.
- The app server handshake reports the real package version.
- Added uninstall scripts, a privacy regression test, CLI tests, a fake app-server handshake test, coverage reporting, format checks, a package smoke test, a manifest consistency check, Dependabot, dependency review, issue and pull-request templates, `SECURITY.md`, `CONTRIBUTING.md`, and `CHANGELOG.md`.

## Notes

Windows behavior is covered by unit tests in CI only. The tray icon, notifications, and installer have not run on real Windows hardware.
