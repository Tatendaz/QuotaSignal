#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS."
  exit 1
fi

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/codex-usage"
launch_agents="$HOME/Library/LaunchAgents"
plist_path="$launch_agents/com.tatendaz.codex-usage.plist"

python3 -m venv "$install_dir/venv"
"$install_dir/venv/bin/python" -m pip install --upgrade pip
"$install_dir/venv/bin/python" -m pip install "$repo_dir[menu]"
mkdir -p "$launch_agents"

sed \
  -e "s|__PROGRAM__|$install_dir/venv/bin/codex-usage|g" \
  "$repo_dir/assets/com.tatendaz.codex-usage.plist.template" > "$plist_path"

launchctl bootout "gui/$(id -u)" "$plist_path" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$plist_path"

"$install_dir/venv/bin/codex-usage" --check
echo "Codex Usage is installed and starts automatically at login."
