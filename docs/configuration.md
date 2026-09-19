# Configuration

Files live in `~/.config/quotasignal` (`%USERPROFILE%\.config\quotasignal` on Windows). Set `XDG_CONFIG_HOME` or `XDG_CACHE_HOME` to move them.

| File | Written by | Holds |
| --- | --- | --- |
| `config.json` | you | notification settings |
| `preferences.json` | the macOS menu | `show_percentage`, `show_icon` |
| `notification-state.json` | the app | the reset time and the levels already sent |
| `~/.cache/quotasignal/usage.json` | the app | percentages, reset times, plan label |

## Notifications

```json
{
  "notifications": {
    "enabled": true,
    "remaining_thresholds": [50, 20, 10]
  }
}
```

Levels are whole numbers from 0 to 100. If one refresh crosses several levels, you get one notification. A file that cannot be parsed falls back to 50, 20, and 10.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `QUOTASIGNAL_CODEX_BIN` | found on `PATH` | full path to the Codex executable |
| `QUOTASIGNAL_TTL` | `60` | seconds the command line reuses the cache |

## Display modes on macOS

The icon-only mode uses the template icon from an installed ChatGPT or Codex desktop app. QuotaSignal does not ship that icon. If neither app is installed, the menu entry is disabled and the percentage stays.
