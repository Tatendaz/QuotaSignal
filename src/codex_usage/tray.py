"""Native macOS menu-bar and Windows system-tray front ends."""

from __future__ import annotations

import platform
import queue
import threading
import webbrowser
from collections.abc import Callable

from .core import Usage, fetch_usage, format_usage
from .notify import pending_notifications
from .protocol import AppServerClient, CodexProtocolError

DASHBOARD_URL = "https://chatgpt.com/codex/settings/usage"


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
            super().__init__("Codex Usage", title="C …", quit_button=None)
            self._updates: queue.SimpleQueue[tuple[Usage | None, str | None]] = (
                queue.SimpleQueue()
            )
            self.details = rumps.MenuItem("Loading usage…")
            self.menu = [
                self.details,
                rumps.MenuItem("Refresh now", callback=self.refresh),
                rumps.MenuItem(
                    "Open usage dashboard",
                    callback=lambda _: webbrowser.open(DASHBOARD_URL),
                ),
                None,
                rumps.MenuItem("Quit Codex Usage", callback=self.quit_app),
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
                self.title = format_usage(usage, compact=True)
                self.details.title = format_usage(usage)
                for message in pending_notifications(usage):
                    rumps.notification("Codex Usage", "Weekly quota", message)
            else:
                self.title = "Codex !"
                self.details.title = error or "Usage unavailable"

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
        icon.title = format_usage(usage) if usage else (error or "Codex Usage unavailable")
        if usage:
            for message in pending_notifications(usage):
                icon.notify(message, "Codex Usage")

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
        "Codex Usage",
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
