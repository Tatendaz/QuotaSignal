"""Native macOS menu-bar and Windows system-tray front ends."""

from __future__ import annotations

import json
import os
import platform
import queue
import threading
import webbrowser
from collections.abc import Callable, Iterable
from pathlib import Path

from .core import Usage, fetch_usage, format_usage
from .notify import pending_notifications
from .protocol import AppServerClient, CodexProtocolError

DASHBOARD_URL = "https://chatgpt.com/codex/settings/usage"
APP_NAME = "QuotaSignal"
PREFERENCES_FILE = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "codex-usage"
    / "preferences.json"
)


def find_menu_bar_icon(candidates: Iterable[Path] | None = None) -> Path | None:
    """Find the official adaptive menu-bar asset from an installed OpenAI app."""
    if candidates is None:
        resource_roots = (
            Path("/Applications/ChatGPT.app/Contents/Resources"),
            Path("/Applications/Codex.app/Contents/Resources"),
            Path.home() / "Applications/ChatGPT.app/Contents/Resources",
            Path.home() / "Applications/Codex.app/Contents/Resources",
        )
        candidates = (
            root / filename
            for root in resource_roots
            for filename in ("chatgptTemplate@2x.png", "chatgptTemplate.png")
        )
    return next((path for path in candidates if path.is_file()), None)


def load_menu_preferences(path: Path = PREFERENCES_FILE) -> tuple[bool, bool]:
    """Default to the narrow percentage-only layout for crowded menu bars."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return True, False
    if not isinstance(value, dict):
        return True, False
    percentage = value.get("show_percentage")
    icon = value.get("show_icon")
    show_percentage = percentage if isinstance(percentage, bool) else True
    show_icon = icon if isinstance(icon, bool) else False
    if show_percentage:
        return True, False
    return (False, True) if show_icon else (True, False)


def save_menu_preferences(
    show_percentage: bool,
    show_icon: bool,
    path: Path = PREFERENCES_FILE,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {
                "show_percentage": show_percentage,
                "show_icon": show_icon,
            }
        ),
        encoding="utf-8",
    )
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def menu_bar_title(
    usage: Usage | None,
    *,
    show_percentage: bool,
    has_icon: bool,
    failed: bool = False,
) -> str:
    """Keep the status item visible even if the official icon cannot be found."""
    if usage is not None:
        percent = f"{usage.weekly.remaining_percent}%{'~' if usage.stale else ''}"
        if show_percentage:
            return percent
        return "" if has_icon else f"Q {percent}"
    marker = "!" if failed else "…"
    if show_percentage:
        return marker
    return "" if has_icon else f"Q {marker}"


def startup_message(usage: Usage) -> str:
    return (
        f"Weekly quota: {usage.weekly.remaining_percent}% left. "
        "If the status item is hidden, your menu bar may be full."
    )


class UsageSource:
    """Create the Codex connection on first refresh, after the tray UI is visible."""

    def __init__(self, client_factory: Callable[[], AppServerClient] = AppServerClient) -> None:
        self._client_factory = client_factory
        self._client: AppServerClient | None = None
        self._lock = threading.Lock()

    def read(self) -> Usage:
        with self._lock:
            if self._client is None:
                self._client = self._client_factory()
            return fetch_usage(self._client)

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None


def _poll(source: UsageSource, callback: Callable[[Usage | None, str | None], None]) -> None:
    try:
        callback(source.read(), None)
    except CodexProtocolError as exc:
        callback(None, str(exc))


def run_macos() -> None:
    try:
        import rumps
    except ImportError as exc:
        raise SystemExit('Install menu support with: pip install "codex-usage[menu]"') from exc

    source = UsageSource()

    class CodexUsageApp(rumps.App):
        def __init__(self) -> None:
            self._icon_path = find_menu_bar_icon()
            self._show_percentage, self._show_icon = load_menu_preferences()
            self._show_icon = self._show_icon and self._icon_path is not None
            self._usage: Usage | None = None
            self._announced_running = False
            super().__init__(
                APP_NAME,
                title=menu_bar_title(
                    None,
                    show_percentage=self._show_percentage,
                    has_icon=self._show_icon,
                ),
                icon=str(self._icon_path) if self._show_icon else None,
                template=True,
                quit_button=None,
            )
            self._updates: queue.SimpleQueue[tuple[Usage | None, str | None]] = (
                queue.SimpleQueue()
            )
            self.details = rumps.MenuItem("Loading usage…")
            self.percentage_item = rumps.MenuItem(
                "Use percentage-only display",
                callback=self.select_percentage,
            )
            self.percentage_item.state = self._show_percentage
            self.icon_item = rumps.MenuItem(
                "Use icon-only display",
                callback=self.select_icon,
            )
            self.icon_item.state = self._show_icon
            self.icon_item.set_callback(self.select_icon if self._icon_path else None)
            self.menu = [
                self.details,
                rumps.MenuItem("Refresh now", callback=self.refresh),
                rumps.MenuItem(
                    "Open usage dashboard",
                    callback=lambda _: webbrowser.open(DASHBOARD_URL),
                ),
                self.percentage_item,
                self.icon_item,
                None,
                rumps.MenuItem(f"Quit {APP_NAME}", callback=self.quit_app),
            ]
            self.timer = rumps.Timer(self.refresh, 60)
            self.timer.start()
            self.update_timer = rumps.Timer(self._apply_updates, 0.25)
            self.update_timer.start()
            self.refresh(None)

        def refresh(self, _: object) -> None:
            threading.Thread(target=_poll, args=(source, self._enqueue_update), daemon=True).start()

        def _enqueue_update(self, usage: Usage | None, error: str | None) -> None:
            self._updates.put((usage, error))

        def _apply_updates(self, _: object) -> None:
            latest: tuple[Usage | None, str | None] | None = None
            try:
                while True:
                    latest = self._updates.get_nowait()
            except queue.Empty:
                pass
            if latest is not None:
                self._updated(*latest)

        def _updated(self, usage: Usage | None, error: str | None) -> None:
            if usage:
                self._usage = usage
                self._update_title()
                self.details.title = format_usage(usage)
                if not self._announced_running:
                    rumps.notification(APP_NAME, "Running", startup_message(usage))
                    self._announced_running = True
                for message in pending_notifications(usage):
                    rumps.notification(APP_NAME, "Weekly quota", message)
            else:
                self.title = menu_bar_title(
                    None,
                    show_percentage=self._show_percentage,
                    has_icon=self._show_icon,
                    failed=True,
                )
                self.details.title = error or "Usage unavailable"

        def _update_title(self) -> None:
            self.title = menu_bar_title(
                self._usage,
                show_percentage=self._show_percentage,
                has_icon=self._show_icon,
            )

        def select_percentage(self, item: object) -> None:
            self._show_percentage = True
            self._show_icon = False
            self._apply_display_mode()

        def select_icon(self, item: object) -> None:
            if self._icon_path is None:
                return
            self._show_percentage = False
            self._show_icon = True
            self._apply_display_mode()

        def _apply_display_mode(self) -> None:
            self.percentage_item.state = self._show_percentage
            self.icon_item.state = self._show_icon
            self.icon = str(self._icon_path) if self._show_icon else None
            self._save_preferences()
            self._update_title()

        def _save_preferences(self) -> None:
            save_menu_preferences(self._show_percentage, self._show_icon)

        def quit_app(self, _: object) -> None:
            source.close()
            rumps.quit_application()

    CodexUsageApp().run()


def run_windows() -> None:
    try:
        import pystray
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit('Install tray support with: pip install "codex-usage[menu]"') from exc

    source = UsageSource()
    current = {"usage": None}

    def image_for(percent: int | None):
        image = Image.new("RGBA", (64, 64), (18, 18, 18, 255))
        draw = ImageDraw.Draw(image)
        text = "?" if percent is None else str(percent)
        font = ImageFont.load_default(size=24)
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(((64 - box[2]) / 2, (64 - box[3]) / 2), text, fill="white", font=font)
        return image

    def update(icon: pystray.Icon, usage: Usage | None, error: str | None) -> None:
        current["usage"] = usage
        icon.icon = image_for(usage.weekly.remaining_percent if usage else None)
        icon.title = format_usage(usage) if usage else (error or f"{APP_NAME} unavailable")
        if usage:
            for message in pending_notifications(usage):
                icon.notify(message, APP_NAME)

    def refresh(icon: pystray.Icon, _: object = None) -> None:
        threading.Thread(
            target=_poll,
            args=(source, lambda usage, error: update(icon, usage, error)),
            daemon=True,
        ).start()

    def quit_app(icon: pystray.Icon, _: object = None) -> None:
        source.close()
        icon.stop()

    icon = pystray.Icon(
        "codex-usage",
        image_for(None),
        APP_NAME,
        menu=pystray.Menu(
            pystray.MenuItem("Refresh now", refresh),
            pystray.MenuItem("Open usage dashboard", lambda *_: webbrowser.open(DASHBOARD_URL)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", quit_app),
        ),
    )
    icon.run(setup=lambda active: refresh(active))


def run_tray() -> None:
    system = platform.system()
    if system == "Darwin":
        run_macos()
    elif system == "Windows":
        run_windows()
    else:
        raise SystemExit("The native status app currently supports macOS and Windows")
