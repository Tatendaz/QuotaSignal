#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS."
  exit 1
fi

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/quotasignal"
launch_agents="$HOME/Library/LaunchAgents"
plist_path="$launch_agents/com.tatendaz.quotasignal.plist"

codex_bin="$(command -v codex || true)"
if [[ -z "$codex_bin" ]]; then
  echo "Codex CLI was not found on PATH. Install Codex and sign in, then run this script again."
  exit 1
fi

python3 -m venv "$install_dir/venv"
"$install_dir/venv/bin/python" -m pip install --upgrade pip
"$install_dir/venv/bin/python" -m pip install "$repo_dir[menu]"
mkdir -p "$launch_agents"

sed \
  -e "s|__PROGRAM__|$install_dir/venv/bin/quotasignal|g" \
  -e "s|__CODEX_BIN__|$codex_bin|g" \
  "$repo_dir/assets/com.tatendaz.quotasignal.plist.template" > "$plist_path"

chmod 644 "$plist_path"

# Remove the login item from before the rename so two copies never run.
legacy_plist="$launch_agents/com.tatendaz.codex-usage.plist"
if [[ -f "$legacy_plist" ]]; then
  launchctl bootout "gui/$(id -u)" "$legacy_plist" 2>/dev/null || true
  rm -f "$legacy_plist"
fi

launchctl bootout "gui/$(id -u)" "$plist_path" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$plist_path"

"$install_dir/venv/bin/quotasignal" --check
echo "QuotaSignal is installed and starts automatically at login."
