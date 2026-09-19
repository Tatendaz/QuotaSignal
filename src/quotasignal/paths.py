"""Per-user config and cache locations."""

from __future__ import annotations

import contextlib
import os
import shutil
from pathlib import Path

APP_DIR = "quotasignal"
LEGACY_DIR = "codex-usage"


def user_dir(env_var: str, fallback: str) -> Path:
    """Return the app directory, copying files from the pre-rename directory once."""
    base = Path(os.environ.get(env_var) or Path.home() / fallback)
    current = base / APP_DIR
    legacy = base / LEGACY_DIR
    if not current.exists() and legacy.is_dir():
        with contextlib.suppress(OSError):
            shutil.copytree(legacy, current)
    return current
