"""Command-line interface."""

from __future__ import annotations

import argparse

from . import __version__
from .core import cached_or_fetch, format_usage, usage_json
from .protocol import CodexProtocolError


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        prog="codex-usage",
        description="Show the shared ChatGPT and Codex quota.",
    )
    value.add_argument(
        "--json",
        action="store_true",
        help="print the sanitized usage snapshot as JSON",
    )
    value.add_argument("--compact", action="store_true", help="print a short status-bar label")
    value.add_argument("--check", action="store_true", help="verify Codex login and quota access")
    value.add_argument("--fresh", action="store_true", help="ignore the short local cache")
    value.add_argument("--version", action="version", version=__version__)
    subcommands = value.add_subparsers(dest="command")
    subcommands.add_parser("tray", help="start the macOS menu-bar or Windows tray app")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "tray":
        from .tray import run_tray

        run_tray()
        return 0
    try:
        usage = cached_or_fetch(ttl=0 if args.fresh or args.check else 60)
    except CodexProtocolError as exc:
        print(f"codex-usage: {exc}")
        return 1
    if args.check:
        print(f"check passed: {format_usage(usage)}")
    elif args.json:
        print(usage_json(usage))
    else:
        print(format_usage(usage, compact=args.compact))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
