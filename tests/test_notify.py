import json

from test_core import payload

import quotasignal.notify as notify
from quotasignal.core import parse_usage


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


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(notify, "CONFIG_ROOT", tmp_path)
    monkeypatch.setattr(notify, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(notify, "STATE_FILE", tmp_path / "state.json")


def test_several_crossed_thresholds_send_one_message(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    usage = parse_usage(payload(5, 95))

    assert notify.pending_notifications(usage) == ["5% of your weekly quota remains"]
    assert notify.pending_notifications(usage) == []
    assert json.loads((tmp_path / "state.json").read_text())["sent"] == ["10", "20", "50"]


def test_malformed_config_falls_back_to_defaults(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    for text in ("[]", '{"notifications": 3}', '{"notifications": {"remaining_thresholds": 5}}'):
        (tmp_path / "config.json").write_text(text)
        assert notify.load_thresholds() == notify.DEFAULT_THRESHOLDS
    (tmp_path / "config.json").write_text(
        json.dumps({"notifications": {"remaining_thresholds": [True, 30, 101, "x"]}})
    )
    assert notify.load_thresholds() == (30,)


def test_state_file_never_holds_more_than_the_ledger(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    notify.pending_notifications(parse_usage(payload(5, 95)))

    assert set(json.loads((tmp_path / "state.json").read_text())) == {"reset", "sent"}


def test_level_fires_again_after_quota_recovers_without_a_reset_time(tmp_path, monkeypatch):
    from dataclasses import replace

    _isolate(tmp_path, monkeypatch)

    def at(remaining):
        value = parse_usage(payload(5, 100 - remaining))
        return replace(value, weekly=replace(value.weekly, resets_at=None))

    assert notify.pending_notifications(at(40)) == ["40% of your weekly quota remains"]
    assert notify.pending_notifications(at(90)) == []
    assert notify.pending_notifications(at(45)) == ["45% of your weekly quota remains"]


def test_fractional_thresholds_are_ignored(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    (tmp_path / "config.json").write_text(
        json.dumps({"notifications": {"remaining_thresholds": [49.5, 25]}})
    )

    assert notify.load_thresholds() == (25,)
