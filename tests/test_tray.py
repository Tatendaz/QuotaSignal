from codex_usage import tray
from codex_usage.core import Usage, Window
from codex_usage.protocol import CodexProtocolError


def usage() -> Usage:
    return Usage(weekly=Window("week", 3, 97))


def test_usage_source_connects_lazily_and_closes(monkeypatch):
    class FakeClient:
        closed = False

        def close(self):
            self.closed = True

    client = FakeClient()
    created = []
    source = tray.UsageSource(lambda: created.append(client) or client)
    monkeypatch.setattr(tray, "fetch_usage", lambda active: usage())

    assert created == []
    assert source.read() == usage()
    assert created == [client]

    source.close()
    assert client.closed is True


def test_poll_reports_protocol_errors():
    class FailingSource:
        def read(self):
            raise CodexProtocolError("unavailable")

    updates = []
    tray._poll(FailingSource(), lambda value, error: updates.append((value, error)))

    assert updates == [(None, "unavailable")]


def test_find_codex_icon_returns_first_installed_candidate(tmp_path):
    missing = tmp_path / "missing.png"
    installed = tmp_path / "icon-codex.png"
    installed.write_bytes(b"icon")

    assert tray.find_codex_icon([missing, installed]) == installed


def test_percentage_preference_defaults_to_compact_and_round_trips(tmp_path):
    path = tmp_path / "preferences.json"

    assert tray.load_show_percentage(path) is False
    tray.save_show_percentage(True, path)
    assert tray.load_show_percentage(path) is True


def test_menu_title_is_icon_only_by_default():
    assert tray.menu_bar_title(usage(), show_percentage=False, has_icon=True) == ""
    assert tray.menu_bar_title(usage(), show_percentage=True, has_icon=True) == "97%"


def test_menu_title_falls_back_to_quota_signal_initial_when_icon_is_missing():
    assert tray.menu_bar_title(usage(), show_percentage=False, has_icon=False) == "Q 97%"
    assert tray.menu_bar_title(None, show_percentage=False, has_icon=False) == "Q …"


def test_run_tray_dispatches_to_macos(monkeypatch):
    called = []
    monkeypatch.setattr(tray.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(tray, "run_macos", lambda: called.append("macos"))

    tray.run_tray()

    assert called == ["macos"]


def test_run_tray_dispatches_to_windows(monkeypatch):
    called = []
    monkeypatch.setattr(tray.platform, "system", lambda: "Windows")
    monkeypatch.setattr(tray, "run_windows", lambda: called.append("windows"))

    tray.run_tray()

    assert called == ["windows"]
