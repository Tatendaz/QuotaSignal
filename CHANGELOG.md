# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-19

### Added

- macOS menu-bar item and Windows system-tray icon that show the remaining shared ChatGPT and
  Codex weekly quota.
- Percentage-only display by default, with an optional icon-only mode for crowded menu bars.
- Notifications when the weekly quota drops below 50%, 20%, and 10%, once per weekly reset.
- `quotasignal` command with `--compact`, `--json`, `--check`, and `--fresh`.
- Login-startup installers and uninstallers for macOS and Windows.
- Agent Plugin and Codex plugin manifests with an install and troubleshooting skill.

[Unreleased]: https://github.com/Tatendaz/QuotaSignal/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Tatendaz/QuotaSignal/releases/tag/v0.1.0
