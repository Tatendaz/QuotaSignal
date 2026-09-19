# Install, start at login, and remove

## macOS

`./scripts/install-macos.sh` does four things:

1. Creates a virtual environment in `~/.local/share/quotasignal/venv` and installs QuotaSignal there.
2. Finds `codex` on your `PATH` and records its full path. Login items start with a short `PATH`, so the app could not find Codex without this.
3. Writes `~/Library/LaunchAgents/com.tatendaz.quotasignal.plist` and loads it.
4. Runs `quotasignal --check`.

launchd restarts the app if it crashes. **Quit QuotaSignal** in the menu stops it until the next login.

If the menu bar is full, macOS hides items on the left. QuotaSignal sends a launch notification so you can tell it runs. Hold Command and drag other items out of the bar to make room.

Remove it with `./scripts/uninstall-macos.sh`. Your settings stay in `~/.config/quotasignal`.

## Windows

`.\scripts\install-windows.ps1` creates a virtual environment in `%LOCALAPPDATA%\QuotaSignal`, adds a `QuotaSignal` shortcut to the Startup folder, runs `quotasignal --check`, and starts the tray icon. If PowerShell blocks the script, run `powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1`.

Windows puts new tray icons in the overflow area. Drag the icon onto the taskbar to keep it visible.

Remove it with `.\scripts\uninstall-windows.ps1`.

These Windows steps have not been verified on real hardware yet.

## Moving from `codex-usage`

The project was named Codex Usage before its first public release. On first run, QuotaSignal copies `~/.config/codex-usage` and `~/.cache/codex-usage` to the new `quotasignal` directories and leaves the old ones in place. The installers remove the old login item. The `CODEX_USAGE_CODEX_BIN` variable still works.
