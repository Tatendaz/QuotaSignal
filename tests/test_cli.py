import pytest

from quotasignal import cli
from quotasignal.core import Usage, Window
from quotasignal.protocol import CodexProtocolError


def test_compact_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "cached_or_fetch", lambda ttl: Usage(weekly=Window("week", 34, 66)))

    assert cli.main(["--compact"]) == 0
    assert capsys.readouterr().out.strip() == "Q 66%"


def test_check_bypasses_cache_and_reports_failure(monkeypatch, capsys):
    seen = []

    def fail(ttl):
        seen.append(ttl)
        raise CodexProtocolError("login required")

    monkeypatch.setattr(cli, "cached_or_fetch", fail)

    assert cli.main(["--check"]) == 1
    assert seen == [0]
    assert "quotasignal: login required" in capsys.readouterr().out


def test_version_flag(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--version"])
    assert capsys.readouterr().out.strip() == cli.__version__
