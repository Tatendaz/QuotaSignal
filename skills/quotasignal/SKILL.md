---
name: quotasignal
description: Install, configure, run, or troubleshoot QuotaSignal, the shared ChatGPT and Codex quota indicator for the macOS menu bar and Windows system tray.
---

# QuotaSignal

Use the scripts in this plugin to install or troubleshoot the QuotaSignal desktop indicator.

## Install

1. Confirm Python 3.10+ and the `codex` CLI are available.
2. From the plugin root, run `python3 -m pip install --user ".[menu]"` on macOS or `py -m pip install --user ".[menu]"` on Windows.
3. Verify the authenticated quota source with `quotasignal --check`.
4. Start the indicator with `quotasignal tray`.
5. Use the platform startup instructions in the README only when the user asks for automatic startup.

QuotaSignal calls the local `codex app-server` process. It must not read, print, copy, or store tokens from Codex authentication files.

## Notifications

Notifications are on by default when weekly remaining quota crosses 50%, 20%, and 10%. To customize them, create `~/.config/quotasignal/config.json` on macOS or the corresponding user config path on Windows:

```json
{
  "notifications": {
    "enabled": true,
    "remaining_thresholds": [50, 20, 10]
  }
}
```

Use only whole-number thresholds from 0 through 100.

## Troubleshooting

- If the CLI cannot find Codex, set `QUOTASIGNAL_CODEX_BIN` to the full path of the Codex executable.
- If quota access fails, have the user open Codex and sign in, then run `quotasignal --check` again.
- A tilde after the percentage means the last cached value is being shown because a fresh read failed.
- API-key-only Codex setups may not have a ChatGPT subscription quota to display.
