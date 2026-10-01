"""Check the copied docs gate against real Git path quoting and branch slugs."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

BASH = shutil.which("bash")
if os.name == "nt":
    git_binary = shutil.which("git")
    git_bash = Path(git_binary).resolve().parent.parent / "bin/bash.exe" if git_binary else None
    BASH = str(git_bash) if git_bash and git_bash.is_file() else None

SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/require-docs-entry.sh"


@pytest.mark.skipif(BASH is None, reason="docs gate requires native bash, not the WSL launcher")
@pytest.mark.parametrize("slug", ["café", "c++parser", "x(1)"])
def test_gate_matches_literal_branch_slug(tmp_path, slug):
    def git(*args):
        return subprocess.run(
            ["git", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    git("init", "-b", "main")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    git("commit", "--allow-empty", "-m", "base")
    git("switch", "-c", f"feat/{slug}")
    entry = tmp_path / "docs/features" / f"2026-10-01-{slug}.md"
    entry.parent.mkdir(parents=True)
    entry.write_text("# Feature: Docs gate regression\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "docs: add feature")
    result = subprocess.run(
        [BASH, SCRIPT.as_posix(), "docs/features", slug, "main...HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    wrong = subprocess.run(
        [BASH, SCRIPT.as_posix(), "docs/features", "unrelated", "main...HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert wrong.returncode == 1
