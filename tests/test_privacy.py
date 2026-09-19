import json

from test_core import payload

from quotasignal import core

SECRETS = ("sk-secret-token", "person@example.com", "acct_123")


def test_cache_and_json_output_drop_account_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "CACHE_ROOT", tmp_path)
    monkeypatch.setattr(core, "CACHE_FILE", tmp_path / "usage.json")
    raw = payload()
    raw["accessToken"] = SECRETS[0]
    raw["rateLimitsByLimitId"]["codex"].update(email=SECRETS[1], accountId=SECRETS[2])

    class Client:
        def read_rate_limits(self):
            return raw

    usage = core.fetch_usage(Client())
    written = (tmp_path / "usage.json").read_text()

    for secret in SECRETS:
        assert secret not in written
        assert secret not in core.usage_json(usage)
        assert secret not in core.format_usage(usage)
    assert set(json.loads(written)) == {"weekly", "session", "plan", "fetched_at", "stale"}
