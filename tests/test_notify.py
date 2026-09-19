import json

from test_core import payload

import codex_usage.notify as notify
from codex_usage.core import parse_usage


def test_notification_fires_once_per_threshold_and_reset(tmp_path, monkeypatch):
    monkeypatch.setattr(notify, "CONFIG_ROOT", tmp_path)
    monkeypatch.setattr(notify, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(notify, "STATE_FILE", tmp_path / "state.json")
    (tmp_path / "config.json").write_text(
        json.dumps({"notifications": {"remaining_thresholds": [50, 20, 10]}})
    )
    usage = parse_usage(payload(5, 55))

    assert notify.pending_notifications(usage) == ["45% of your weekly quota remains"]
    assert notify.pending_notifications(usage) == []


def test_notifications_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(notify, "CONFIG_ROOT", tmp_path)
    monkeypatch.setattr(notify, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(notify, "STATE_FILE", tmp_path / "state.json")
    (tmp_path / "config.json").write_text(json.dumps({"notifications": {"enabled": False}}))

    assert notify.pending_notifications(parse_usage(payload(5, 99))) == []
