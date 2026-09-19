<div align="center">

# ◉ Codex Usage

**Your shared ChatGPT and Codex quota, live in the macOS menu bar or Windows system tray.**

```text
Codex 66%
```

See how much weekly quota remains while you work, with optional notifications before it runs low.

</div>

## What it does

- Shows weekly remaining quota as it changes.
- Includes the shorter session window in the details menu.
- Tracks the shared quota used by both ChatGPT and Codex.
- Sends one notification when weekly remaining quota crosses 50%, 20%, and 10%.
- Uses the existing Codex login through the local Codex app server. It never reads or stores your access token.
- Runs on macOS as a menu-bar title and on Windows as a percentage icon in the notification area.

## Requirements

- Python 3.10 or newer
- Codex CLI installed and signed into the same ChatGPT account you want to monitor
- macOS or Windows for the native status app

## Install from source

```bash
git clone https://github.com/Tatendaz/codex-usage.git
cd codex-usage
python3 -m pip install --user ".[menu]"
codex-usage --check
codex-usage tray
```

On Windows, replace `python3` with `py` when needed.

The first request can take a few seconds while the local Codex app server starts. Later updates reuse the same process and refresh once a minute.

### Start automatically

The platform installers create a private virtual environment and register Codex Usage for login startup:

```bash
./scripts/install-macos.sh
```

On Windows PowerShell:

```powershell
.\scripts\install-windows.ps1
```

## Command line

```bash
codex-usage                 # full text output
codex-usage --compact       # short status label
codex-usage --json          # sanitized machine-readable output
codex-usage --check         # verify Codex login and quota access
codex-usage tray            # start the native status app
```

Example:

```text
◉ week 66% left · resets in 3d · 5h 88% left
```

## Notifications

Notifications are enabled by default at 50%, 20%, and 10% weekly quota remaining. Customize them in `~/.config/codex-usage/config.json`:

```json
{
  "notifications": {
    "enabled": true,
    "remaining_thresholds": [50, 20, 10]
  }
}
```

Each threshold fires once per weekly reset.

## Install as a ChatGPT and Codex plugin

This repository includes both the portable Agent Plugin manifest and the Codex compatibility manifest. The bundled skill can install, configure, or troubleshoot the desktop indicator from ChatGPT Work or Codex.

During development, add the repository as a marketplace source:

```bash
codex plugin marketplace add Tatendaz/codex-usage
```

## Privacy and security

Codex Usage launches `codex app-server` and requests the same account rate-limit snapshot used by Codex’s status UI. Authentication stays inside Codex. The cache contains only percentages, reset times, and the plan label; cache and notification-state files are created with user-only permissions where the operating system supports them.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,menu]"
pytest
ruff check .
```

## License

[MIT](LICENSE)
