# Review scope

CI tests the Python package across Python 3.10–3.14 on macOS, Windows, and Linux. It checks formatting, package construction, plugin manifests, and dependencies on pull requests. A zizmor job scans the workflows and fails on high-severity findings. Static analysis and unit tests cannot establish every real desktop interaction.

## CodeAndConfirm

```bash
codeandconfirm review --branch chore/open-source --base main --criteria-file /tmp/criteria.md
```

The `desktop-static` profile runs an independent Claude static worker and a required Python suite with JUnit evidence in an isolated worktree. There are no mobile apps to build. A PASS covers this review scope only; it does not certify the macOS menu, Windows tray, notifications, installers, or physical-device performance. macOS live quota access was checked separately; Windows desktop verification remains on the roadmap.

Source and review context reach the configured model provider. No quota authentication files are needed by these tests. The suite uses `QUOTASIGNAL_QA_PYTHON` when set; it must point to Python 3.10+. Machine overrides belong in `.codeandconfirm.local.toml`, which is ignored.

## Backup PR reviewer

The owner's existing local `review-failover` service supplies an independent review of the current PR commit through open-code-review and Claude. `/open-code-review` requests it. A successful status means no critical/high findings; it is not a substitute for CI or desktop checks.

## Dependency merges

Dependabot groups monthly patch/minor updates and waits 7 days after a release before it proposes it (security updates do not wait). `merge-when-clean.yml` merges a Dependabot PR, or the owner's `security/*` or `automerge`-labelled PR, once at least one check run exists and every check finished as `success`, `neutral` or `skipped`, every other commit status is `success`, a real review ran on its head, no review requests changes, no threads are open, and there are no merge conflicts. It pins the merge to that head commit. Major updates (including `0.x` minor bumps) stay manual, as do PRs labelled `needs-owner` or `do-not-merge`, PRs that touch database rules, migrations, infra or the workflow itself, and paths listed in `.github/merge-hold-paths` (none in this repo).
