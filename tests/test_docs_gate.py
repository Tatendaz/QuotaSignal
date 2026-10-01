"""Check the copied docs gate against real Git path quoting and branch slugs."""

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/require-docs-entry.sh"


@pytest.mark.skipif(shutil.which("bash") is None, reason="docs gate requires bash")
@pytest.mark.parametrize("slug", ["café", "c++parser", "x[1]"])
def test_gate_matches_literal_branch_slug(tmp_path, slug):
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True
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
        ["bash", str(SCRIPT), "docs/features", slug, "main...HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    wrong = subprocess.run(
        ["bash", str(SCRIPT), "docs/features", "unrelated", "main...HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert wrong.returncode == 1
