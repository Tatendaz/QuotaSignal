import json
import queue

import pytest

from codex_usage.protocol import AppServerClient, CodexProtocolError


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
