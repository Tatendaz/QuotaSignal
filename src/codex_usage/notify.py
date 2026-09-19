"""Threshold notification state."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .core import Usage

CONFIG_ROOT = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "codex-usage"
CONFIG_FILE = CONFIG_ROOT / "config.json"
STATE_FILE = CONFIG_ROOT / "notification-state.json"
DEFAULT_THRESHOLDS = (50, 20, 10)


def load_thresholds() -> tuple[int, ...]:
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DEFAULT_THRESHOLDS
    if config.get("notifications", {}).get("enabled", True) is False:
        return ()
    values = config.get("notifications", {}).get("remaining_thresholds", DEFAULT_THRESHOLDS)
    valid = sorted(
        {int(item) for item in values if isinstance(item, (int, float)) and 0 <= item <= 100},
        reverse=True,
    )
    return tuple(valid)


def _read_state() -> dict[str, object]:
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_state(value: dict[str, object]) -> None:
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".notify-", dir=CONFIG_ROOT)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle)
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, STATE_FILE)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def pending_notifications(usage: Usage) -> list[str]:
    """Return newly crossed weekly thresholds and persist their delivery ledger."""
    reset_key = str(usage.weekly.resets_at or "unknown")
    state = _read_state()
    sent = set(state.get("sent", [])) if state.get("reset") == reset_key else set()
    messages: list[str] = []
    for threshold in load_thresholds():
        key = str(threshold)
        if usage.weekly.remaining_percent <= threshold and key not in sent:
            messages.append(f"{usage.weekly.remaining_percent}% of your weekly quota remains")
            sent.add(key)
    _write_state({"reset": reset_key, "sent": sorted(sent)})
    return messages
