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
