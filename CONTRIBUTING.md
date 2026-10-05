# Contributing

Three CI rules are not obvious from the code:

1. Name the branch `<type>/<slug>`, with `feat/`, `fix/`, `docs/`, `chore/`, or `refactor/`.
2. Every pull request adds `docs/features/<YYYY-MM-DD>-<slug>.md` and `docs/summaries/<YYYY-MM-DD>-<slug>.md`. The first says what changed and why. The second lists the prompts or steps behind the change.
3. A change under `src/` needs a change under `tests/`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,menu]"
pytest --cov=quotasignal
ruff check .
ruff format --check .
python scripts/check_manifests.py
```

The tests need no network, no Codex login, and no desktop session.

## The safety rule

Get quota data only from `codex app-server` with `account/rateLimits/read`. Do not read, print, copy, cache, or upload anything from Codex authentication files. Persist only percentages, reset times, the plan label, and notification state. `tests/test_privacy.py` guards this.

## Platform testing

Say in the pull request which platform you ran the tray app on. Windows reports are especially useful, because the maintainer develops on macOS.

## Releases

Bump the version in `src/quotasignal/__init__.py`, `pyproject.toml`, `plugin.json`, and `.codex-plugin/plugin.json` (`scripts/check_manifests.py` checks they agree). Move the `Unreleased` notes in `CHANGELOG.md` under the new version, tag `vX.Y.Z`, and publish a GitHub release. The release starts the desktop build workflow.

## Community and review

Follow the [Code of Conduct](CODE_OF_CONDUCT.md). Reports can be sent privately to the maintainer at the address there. Dependabot patch and minor updates merge automatically only after required checks pass; major updates need review.

CodeAndConfirm runs an independent static review and the unit suite using `codeandconfirm.toml`. It does not certify desktop GUI behavior. See [review scope](docs/review.md).
