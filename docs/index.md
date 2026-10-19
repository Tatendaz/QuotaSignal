# QuotaSignal

Your shared ChatGPT and Codex quota, in the menu bar.

The weekly allowance you have left, in the macOS menu bar or Windows tray. A notification at 50%, 20%, and 10%.

[GitHub](https://github.com/Tatendaz/QuotaSignal) · [Install](#install)

A live quota check on macOS returned:

```text
$ quotasignal --check
check passed: ◉ week 94% left · resets in 6d
```

## Who it is for

People who run the Codex CLI signed in with a ChatGPT account and share one weekly allowance between ChatGPT and Codex. QuotaSignal puts the remaining percentage where you can see it, so you can check it before you start a long task.

It needs Python 3.10 or newer and the Codex CLI. No API key. Setups that use only an API key may have no subscription quota to show.

## What sits in the menu bar

The bar shows a percentage. Click it for the weekly figure, the reset time, and the 5-hour window when Codex reports one.

![Illustration of the QuotaSignal menu](https://tatendaz.github.io/QuotaSignal/images/menu-dark.svg)

This menu is an illustration, not a screenshot. The `--check` output above is from a real quota read.

- Percentage only by default. An icon-only mode is there for crowded menu bars on macOS.
- When a read fails, the last cached value stays on screen with a `~` after it, as in `66%~`.

## Notifications before you run out

You get one notification when the weekly quota left drops below each level, once per weekly reset. If one refresh crosses several levels, you get a single notification. The default levels are 50%, 20%, and 10%.

Change the levels, or turn notifications off, in `~/.config/quotasignal/config.json`:

```json
{
  "notifications": {
    "enabled": true,
    "remaining_thresholds": [50, 20, 10]
  }
}
```

## How it works

- QuotaSignal starts `codex app-server` and requests `account/rateLimits/read` over stdio once a minute. Codex owns the signed-in session.
- It makes no network requests of its own, has no telemetry, and does not read authentication files. Codex talks to OpenAI with your existing ChatGPT login.
- `~/.cache/quotasignal/usage.json` holds percentages, reset times, and a plan label. No account identifiers are written to the cache or to `--json` output.

## Install

Requires Python 3.10+ and the [Codex CLI](https://developers.openai.com/codex/cli), signed in to your ChatGPT account. QuotaSignal is free; your ChatGPT subscription is separate.

1. Clone the repository:
   ```bash
   git clone https://github.com/Tatendaz/QuotaSignal.git
   cd QuotaSignal
   ```
2. Create an environment and install the app:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install ".[menu]"
   ```
3. Check access, then start the indicator:
   ```bash
   quotasignal --check
   quotasignal tray
   ```

On Windows, use `py -m venv .venv` and `.venv\Scripts\Activate.ps1`. For startup at login, run `./scripts/install-macos.sh` or `.\scripts\install-windows.ps1`. See the [installation details](https://github.com/Tatendaz/QuotaSignal/blob/main/docs/install.md).

```bash
quotasignal             # weekly quota and reset time
quotasignal --compact   # Q 94%
quotasignal --json      # sanitized snapshot
quotasignal --fresh     # bypass the 60-second CLI cache
quotasignal tray        # menu bar or system tray
```

## Status

Version 0.1.0, released 2026-09-19 and marked alpha. The source install above is the documented path.

- The macOS menu bar item has been used on Apple silicon. Windows tests run in CI, but the real Windows tray and installers have not been checked on hardware yet.
- Linux gets the command line only.
- The Codex app-server API is experimental and can change between CLI releases.
- Desktop builds are unsigned.
- Crowded macOS menu bars can hide the item. Windows may put it in the overflow area.

## Also on a Claude plan?

[claude-usage](https://tatendaz.github.io/claude-usage/) is the sister tool. It shows your Claude session, weekly, and per-model quota in the iTerm2, tmux, WezTerm, kitty, or starship status bar.

## Built by Tatenda Zhou

QuotaSignal is MIT licensed. The source is on [GitHub](https://github.com/Tatendaz/QuotaSignal).

- [tatendaz.github.io](https://tatendaz.github.io/)
- [Follow on X](https://x.com/realtatendazhou)
- [LinkedIn](https://www.linkedin.com/in/tatendazhou)

Need help making AI coding agents reliable? [tatendaz@me.com](mailto:tatendaz@me.com?subject=AI%20coding%20agents%20(via%20QuotaSignal))

Not affiliated with OpenAI. ChatGPT and Codex are names of OpenAI products.
