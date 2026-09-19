"""Threshold notification state."""

from __future__ import annotations

import json
import os
import tempfile

from .core import Usage
from .paths import user_dir

CONFIG_ROOT = user_dir("XDG_CONFIG_HOME", ".config")
CONFIG_FILE = CONFIG_ROOT / "config.json"
STATE_FILE = CONFIG_ROOT / "notification-state.json"
DEFAULT_THRESHOLDS = (50, 20, 10)


def load_thresholds() -> tuple[int, ...]:
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DEFAULT_THRESHOLDS
    section = config.get("notifications") if isinstance(config, dict) else None
    if not isinstance(section, dict):
        return DEFAULT_THRESHOLDS
    if section.get("enabled", True) is False:
        return ()
    values = section.get("remaining_thresholds", DEFAULT_THRESHOLDS)
    if not isinstance(values, (list, tuple)):
        return DEFAULT_THRESHOLDS
    valid = sorted(
        {
            int(item)
            for item in values
            if isinstance(item, (int, float)) and not isinstance(item, bool) and 0 <= item <= 100
        },
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
    """Return one message when new weekly thresholds are crossed, and persist the ledger."""
    reset_key = str(usage.weekly.resets_at or "unknown")
    state = _read_state()
    previous = state.get("sent")
    sent = (
        {str(item) for item in previous}
        if state.get("reset") == reset_key and isinstance(previous, list)
        else set()
    )
    crossed = {
        str(threshold)
        for threshold in load_thresholds()
        if usage.weekly.remaining_percent <= threshold
    } - sent
    _write_state({"reset": reset_key, "sent": sorted(sent | crossed)})
    if not crossed:
        return []
    return [f"{usage.weekly.remaining_percent}% of your weekly quota remains"]
