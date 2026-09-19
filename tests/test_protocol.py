import json
import queue

import pytest

from quotasignal.protocol import AppServerClient, CodexProtocolError


def client_without_process():
    client = object.__new__(AppServerClient)
    client.timeout = 0.01
    client._next_id = 2
    client._messages = queue.Queue()
    client._lock = __import__("threading").Lock()
    sent = []
    client._send = sent.append
    return client, sent


def test_request_ignores_notifications_and_matches_id():
    client, sent = client_without_process()
    client._messages.put({"method": "account/rateLimits/updated", "params": {}})
    client._messages.put({"id": 2, "result": {"rateLimits": {}}})

    assert client._request("account/rateLimits/read") == {"rateLimits": {}}
    assert sent == [{"id": 2, "method": "account/rateLimits/read", "params": None}]


def test_request_surfaces_protocol_error():
    client, _ = client_without_process()
    client._messages.put({"id": 2, "error": {"message": "login required"}})

    with pytest.raises(CodexProtocolError, match="login required"):
        client._request("account/rateLimits/read")


def test_sent_messages_are_json_serializable():
    client, sent = client_without_process()
    client._messages.put({"id": 2, "result": {}})
    client._request("account/rateLimits/read")

    json.dumps(sent)


def test_find_codex_honours_new_and_legacy_override(tmp_path, monkeypatch):
    from quotasignal.protocol import find_codex

    binary = tmp_path / "codex"
    binary.write_text("")
    monkeypatch.delenv("QUOTASIGNAL_CODEX_BIN", raising=False)
    monkeypatch.setenv("CODEX_USAGE_CODEX_BIN", str(binary))
    assert find_codex() == str(binary)

    monkeypatch.setenv("QUOTASIGNAL_CODEX_BIN", str(tmp_path / "missing"))
    with pytest.raises(CodexProtocolError, match="QUOTASIGNAL_CODEX_BIN"):
        find_codex()


FAKE_SERVER = """#!{python}
import json, sys
assert sys.argv[1:] == ["app-server", "--stdio"]
for line in sys.stdin:
    message = json.loads(line)
    if message.get("method") == "initialize":
        print(json.dumps({{"id": message["id"], "result": {{}}}}), flush=True)
    elif message.get("method") == "account/rateLimits/read":
        print("not json", flush=True)
        print(json.dumps({{"id": message["id"], "result": {{"rateLimits": {{}}}}}}), flush=True)
"""


@pytest.mark.skipif(__import__("os").name == "nt", reason="needs an executable script")
def test_client_handshake_against_fake_app_server(tmp_path):
    import sys

    binary = tmp_path / "codex"
    binary.write_text(FAKE_SERVER.format(python=sys.executable))
    binary.chmod(0o755)

    with AppServerClient(timeout=10, codex_bin=str(binary)) as client:
        assert client.read_rate_limits() == {"rateLimits": {}}
    assert client._process.poll() is not None
