<div align="center">

# QuotaSignal

**The shared ChatGPT and Codex weekly quota you have left, in the macOS menu bar or the Windows system tray.**

[![CI](https://github.com/Tatendaz/QuotaSignal/actions/workflows/ci.yml/badge.svg)](https://github.com/Tatendaz/QuotaSignal/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](pyproject.toml)
[![Tokens: never read](https://img.shields.io/badge/tokens-never%20read-2ea44f.svg)](#privacy-and-security)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/menu-dark.svg">
  <img alt="Drawing of the QuotaSignal menu-bar item showing 66% with its menu open" src="docs/images/menu-light.svg" width="560">
</picture>

*The picture is a drawing of the macOS menu, not a screen capture.*

</div>

---

ChatGPT and Codex draw on one weekly allowance. QuotaSignal asks your local Codex app server for that number once a minute and shows it as a percentage, for example `66%`.

## What it does

- Shows the weekly quota that remains. The 5-hour window is in the menu.
- Shows the percentage alone by default, which is about four characters wide. An icon-only mode is in the menu for crowded macOS menu bars.
- Sends a notification when the weekly quota drops below 50%, 20%, and 10%. Each level fires once per weekly reset.
- Sends one notification at launch on macOS, so you know it runs even when the menu bar has no room for the item.
- Shows the last known value with a `~` when a fresh read fails.

## Platform status

| Platform | Status |
| --- | --- |
| macOS | Developed and used daily on macOS with Apple silicon. |
| Windows | The unit tests pass on Windows in CI. The tray icon, the notifications, and the installer are **not yet verified on real Windows hardware**. Please [open an issue](https://github.com/Tatendaz/QuotaSignal/issues) with what you see. |
| Linux | The command line works. There is no tray app. |

## Requirements

- Python 3.10 or newer
- The [Codex CLI](https://developers.openai.com/codex/cli), signed in to the ChatGPT account you want to watch

## Install

```bash
git clone https://github.com/Tatendaz/QuotaSignal.git
cd QuotaSignal
python3 -m pip install --user ".[menu]"
quotasignal --check
quotasignal tray
```

On Windows, use `py` in place of `python3`. The first read takes a few seconds while the Codex app server starts.

To start QuotaSignal at login, run `./scripts/install-macos.sh` or `.\scripts\install-windows.ps1`. [docs/install.md](docs/install.md) covers what the installers change, how to remove them, and how to move from the older `codex-usage` name.

## Command line

```bash
quotasignal             # ◉ week 66% left · resets in 3d · 5h 88% left
quotasignal --compact   # Q 66%
quotasignal --json      # sanitized snapshot
quotasignal --check     # verify the Codex login and quota access
quotasignal tray        # start the menu-bar or tray app
```

## Notifications

Edit `~/.config/quotasignal/config.json` to change the levels or turn notifications off:

```json
{ "notifications": { "enabled": true, "remaining_thresholds": [50, 20, 10] } }
```

More settings are in [docs/configuration.md](docs/configuration.md).

## Privacy and security

QuotaSignal starts `codex app-server` and sends it one request, `account/rateLimits/read`. Codex holds the login. QuotaSignal does not open Codex authentication files, and it makes no network requests of its own.

Three files are written, all with user-only permissions where the system supports them: the cache (percentages, reset times, plan label), the notification ledger, and the display preference. `tests/test_privacy.py` fails the build if an account field reaches the cache or the JSON output. Report problems through [SECURITY.md](SECURITY.md).

## Plugin for ChatGPT and Codex

The repository is also an Agent Plugin with a skill that installs and troubleshoots the app:

```bash
codex plugin marketplace add Tatendaz/QuotaSignal
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are listed in [CHANGELOG.md](CHANGELOG.md).

QuotaSignal is an independent project. It is not affiliated with or endorsed by OpenAI. ChatGPT and Codex are trademarks of OpenAI.

## License

[MIT](LICENSE)
