from test_core import payload

from codex_usage import core
from codex_usage.protocol import CodexProtocolError


class FailingClient:
    def read_rate_limits(self):
        raise CodexProtocolError("offline")


def test_fetch_uses_typed_stale_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "CACHE_ROOT", tmp_path)
    monkeypatch.setattr(core, "CACHE_FILE", tmp_path / "usage.json")
    cached = core.parse_usage(payload())
    core._save_cache(cached)

    result = core.fetch_usage(FailingClient())

    assert result.stale is True
    assert result.weekly.remaining_percent == 66
    assert result.session is not None
    assert result.session.remaining_percent == 88
