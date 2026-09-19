"""Usage parsing, caching, and human-friendly formatting."""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from .protocol import AppServerClient, CodexProtocolError

WEEK_MINUTES = 7 * 24 * 60
DEFAULT_TTL = int(os.environ.get("CODEX_USAGE_TTL", "60"))
CACHE_ROOT = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "codex-usage"
CACHE_FILE = CACHE_ROOT / "usage.json"


@dataclass(frozen=True)
class Window:
    name: str
    used_percent: int
    remaining_percent: int
    duration_minutes: int | None = None
    resets_at: int | None = None


@dataclass(frozen=True)
class Usage:
    weekly: Window
    session: Window | None = None
    plan: str | None = None
    fetched_at: int = 0
    stale: bool = False


def _bounded_percent(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CodexProtocolError("Codex returned an invalid usage percentage")
    return max(0, min(100, round(value)))


def _window(name: str, value: Any) -> Window | None:
    if not isinstance(value, dict) or "usedPercent" not in value:
        return None
    used = _bounded_percent(value["usedPercent"])
    duration = value.get("windowDurationMins")
    reset = value.get("resetsAt")
    return Window(
        name=name,
        used_percent=used,
        remaining_percent=100 - used,
        duration_minutes=duration if isinstance(duration, int) else None,
        resets_at=reset if isinstance(reset, int) else None,
    )


def _pick_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    by_id = payload.get("rateLimitsByLimitId")
    if isinstance(by_id, dict) and by_id:
        preferred = by_id.get("codex")
        if isinstance(preferred, dict):
            return preferred
        candidates = [value for value in by_id.values() if isinstance(value, dict)]
        if candidates:
            return max(candidates, key=lambda item: _snapshot_span(item))
    legacy = payload.get("rateLimits")
    if isinstance(legacy, dict):
        return legacy
    raise CodexProtocolError("Codex did not return an account rate-limit snapshot")


def _snapshot_span(snapshot: dict[str, Any]) -> int:
    spans = [
        value.get("windowDurationMins", 0)
        for key in ("primary", "secondary")
        if isinstance((value := snapshot.get(key)), dict)
    ]
    return max((span for span in spans if isinstance(span, int)), default=0)


def parse_usage(payload: dict[str, Any], fetched_at: int | None = None) -> Usage:
    snapshot = _pick_snapshot(payload)
    windows = [
        item
        for item in (
            _window("primary", snapshot.get("primary")),
            _window("secondary", snapshot.get("secondary")),
        )
        if item is not None
    ]
    if not windows:
        raise CodexProtocolError("Codex returned no active rate-limit windows")

    weekly = max(windows, key=lambda item: item.duration_minutes or 0)
    session_candidates = [item for item in windows if item is not weekly]
    session = min(session_candidates, key=lambda item: item.duration_minutes or 0, default=None)
    weekly = Window(**{**asdict(weekly), "name": "week"})
    if session:
        label = (
            "5h"
            if session.duration_minutes and session.duration_minutes <= 6 * 60
            else "session"
        )
        session = Window(**{**asdict(session), "name": label})
    plan = snapshot.get("planType")
    return Usage(
        weekly=weekly,
        session=session,
        plan=plan if isinstance(plan, str) else None,
        fetched_at=fetched_at or int(time.time()),
    )


def _save_cache(usage: Usage) -> None:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".usage-", dir=CACHE_ROOT)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(asdict(usage), handle)
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, CACHE_FILE)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _load_cache() -> Usage | None:
    try:
        value = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        weekly = Window(**value["weekly"])
        session = Window(**value["session"]) if value.get("session") else None
        return Usage(
            weekly=weekly,
            session=session,
            plan=value.get("plan"),
            fetched_at=int(value["fetched_at"]),
            stale=bool(value.get("stale", False)),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


def fetch_usage(client: AppServerClient | None = None) -> Usage:
    owns_client = client is None
    active = client or AppServerClient()
    try:
        usage = parse_usage(active.read_rate_limits())
        _save_cache(usage)
        return usage
    except CodexProtocolError:
        cached = _load_cache()
        if cached:
            return replace(cached, stale=True)
        raise
    finally:
        if owns_client:
            active.close()


def cached_or_fetch(client: AppServerClient | None = None, ttl: int = DEFAULT_TTL) -> Usage:
    cached = _load_cache()
    if cached and time.time() - cached.fetched_at < ttl:
        return cached
    return fetch_usage(client)


def reset_text(timestamp: int | None) -> str:
    if not timestamp:
        return ""
    seconds = max(0, timestamp - int(time.time()))
    if seconds < 3600:
        return f"{max(1, seconds // 60)}m"
    if seconds < 86400:
        return f"{max(1, seconds // 3600)}h"
    return f"{max(1, seconds // 86400)}d"


def format_usage(usage: Usage, compact: bool = False) -> str:
    stale = "~" if usage.stale else ""
    if compact:
        return f"C {usage.weekly.remaining_percent}%{stale}"
    parts = [f"week {usage.weekly.remaining_percent}% left"]
    if usage.session:
        parts.append(f"{usage.session.name} {usage.session.remaining_percent}% left")
    reset = reset_text(usage.weekly.resets_at)
    if reset:
        parts[0] += f" · resets in {reset}"
    return "◉ " + " · ".join(parts) + stale


def usage_json(usage: Usage) -> str:
    value = asdict(usage)
    value["observed_at"] = datetime.fromtimestamp(usage.fetched_at).astimezone().isoformat()
    return json.dumps(value, indent=2, sort_keys=True)
