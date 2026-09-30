# Review scope

CI tests the Python package across Python 3.10–3.14 on macOS, Windows, and Linux. It checks formatting, package construction, plugin manifests, and dependencies on pull requests. Static analysis and unit tests cannot establish every real desktop interaction.

## CodeAndConfirm

```bash
codeandconfirm review --branch chore/open-source --base main --criteria-file /tmp/criteria.md
```

The `desktop-static` profile runs an independent Claude static worker and a required Python suite with JUnit evidence in an isolated worktree. There are no mobile apps to build. A PASS covers this review scope only; it does not certify the macOS menu, Windows tray, notifications, installers, or physical-device performance. macOS live quota access was checked separately; Windows desktop verification remains on the roadmap.

Source and review context reach the configured model provider. No quota authentication files are needed by these tests. Machine overrides belong in `.codeandconfirm.local.toml`, which is ignored.

## Backup PR reviewer

The owner's existing local `review-failover` service supplies an independent review of the current PR commit through open-code-review and Claude. `/open-code-review` requests it. A successful status means no critical/high findings; it is not a substitute for CI or desktop checks.

## Dependency merges

Dependabot groups weekly patch/minor updates. The workflow waits for required checks and pins the merge to the reviewed head. Major updates remain manual. Missing required checks, failing checks, and timeouts stop the workflow. Repository auto-merge and required checks must be enabled for the workflow to work.
