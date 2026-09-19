#!/usr/bin/env bash
set -euo pipefail

install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/quotasignal"
plist_path="$HOME/Library/LaunchAgents/com.tatendaz.quotasignal.plist"

launchctl bootout "gui/$(id -u)" "$plist_path" 2>/dev/null || true
rm -f "$plist_path"
rm -rf "$install_dir"
echo "QuotaSignal is removed. Settings stay in ~/.config/quotasignal."
