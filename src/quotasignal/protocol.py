"""Small JSON-lines client for the local Codex app-server."""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from . import __version__


class CodexProtocolError(RuntimeError):
    """The local Codex app-server could not provide a usage snapshot."""


def find_codex() -> str:
    override = os.environ.get("QUOTASIGNAL_CODEX_BIN") or os.environ.get("CODEX_USAGE_CODEX_BIN")
    if override:
        path = Path(override).expanduser()
        if path.is_file():
            return str(path)
        raise CodexProtocolError("QUOTASIGNAL_CODEX_BIN does not point to a file")

    found = shutil.which("codex")
    if found:
        return found

    candidates = [
        Path.home() / ".local" / "bin" / "codex",
        Path.home() / ".npm-global" / "bin" / "codex",
        # launchd starts login items with a minimal PATH, so check the usual macOS prefixes.
        Path("/opt/homebrew/bin/codex"),
        Path("/usr/local/bin/codex"),
    ]
    if os.name == "nt":
        candidates.extend(
            [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "codex" / "codex.exe",
                Path(os.environ.get("APPDATA", "")) / "npm" / "codex.cmd",
            ]
        )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise CodexProtocolError("Codex CLI was not found; install Codex or set QUOTASIGNAL_CODEX_BIN")


class AppServerClient:
    """Persistent app-server process with request/response matching."""

    def __init__(self, timeout: float = 20.0, codex_bin: str | None = None) -> None:
        self.timeout = timeout
        self.codex_bin = codex_bin or find_codex()
        self._next_id = 1
        self._messages: queue.Queue[dict[str, Any] | BaseException] = queue.Queue()
        self._lock = threading.Lock()
        self._process = subprocess.Popen(
            [self.codex_bin, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            # The tray runs under pythonw on Windows; without this a console window flashes.
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()
        try:
            self._initialize()
        except BaseException:
            self.close()
            raise

    def _read_stdout(self) -> None:
        assert self._process.stdout is not None
        try:
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    self._messages.put(value)
        except BaseException as exc:  # pragma: no cover - OS pipe failures are platform-specific
            self._messages.put(exc)

    def _send(self, message: dict[str, Any]) -> None:
        if self._process.poll() is not None:
            raise CodexProtocolError("Codex app-server stopped unexpectedly")
        assert self._process.stdin is not None
        try:
            self._process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise CodexProtocolError("Could not communicate with the Codex app-server") from exc

    def _request(self, method: str, params: Any = None) -> dict[str, Any]:
        with self._lock:
            request_id = self._next_id
            self._next_id += 1
            self._send({"id": request_id, "method": method, "params": params})
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    # One deadline per request; server notifications must not extend it.
                    message = self._messages.get(timeout=max(0.0, deadline - time.monotonic()))
                except queue.Empty as exc:
                    raise CodexProtocolError(f"Codex app-server timed out during {method}") from exc
                if isinstance(message, BaseException):
                    raise CodexProtocolError(
                        "Could not read from the Codex app-server"
                    ) from message
                if message.get("id") != request_id:
                    continue
                if "error" in message:
                    detail = message["error"]
                    if isinstance(detail, dict):
                        detail = detail.get("message") or "request failed"
                    raise CodexProtocolError(f"Codex app-server rejected {method}: {detail}")
                result = message.get("result")
                if not isinstance(result, dict):
                    raise CodexProtocolError(
                        f"Codex app-server returned an invalid {method} response"
                    )
                return result

    def _initialize(self) -> None:
        self._request(
            "initialize",
            {
                "clientInfo": {
                    "name": "quotasignal",
                    "title": "QuotaSignal",
                    "version": __version__,
                },
                "capabilities": {"experimentalApi": True},
            },
        )
        self._send({"method": "initialized"})

    def read_rate_limits(self) -> dict[str, Any]:
        return self._request("account/rateLimits/read")

    def close(self) -> None:
        if self._process.poll() is not None:
            return
        if self._process.stdin is not None:
            self._process.stdin.close()
        self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive cleanup
            self._process.kill()

    def __enter__(self) -> AppServerClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
