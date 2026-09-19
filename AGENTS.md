# Agent guide: codex-usage

Codex Usage is a Python 3.10+ app and Agent Plugin that displays the shared ChatGPT and Codex quota in the macOS menu bar or Windows system tray.

## Safety boundary

Use `codex app-server` and `account/rateLimits/read` for quota data. Never read, print, copy, cache, or upload token values from Codex authentication files. Persist only sanitized percentages, reset timestamps, plan labels, and notification state.

## Development checks

```bash
python -m pytest
ruff check .
python /Users/tatendazhou/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

New behavior needs focused tests. User-visible changes need matching entries in `docs/features/` and `docs/summaries/` before pushing.
