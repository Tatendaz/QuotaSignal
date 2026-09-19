"""Check that every manifest agrees with the package name and version."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    init = (ROOT / "src/quotasignal/__init__.py").read_text(encoding="utf-8")
    version = re.search(r'__version__ = "([^"]+)"', init).group(1)
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    problems = []
    if f'version = "{version}"' not in project:
        problems.append("pyproject.toml version differs from quotasignal.__version__")
    for name in ("plugin.json", ".codex-plugin/plugin.json"):
        manifest = json.loads((ROOT / name).read_text(encoding="utf-8"))
        if manifest.get("name") != "quotasignal":
            problems.append(f"{name}: name is not quotasignal")
        if manifest.get("version") != version:
            problems.append(f"{name}: version differs from {version}")
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text("utf-8"))
    if marketplace["plugins"][0]["name"] != "quotasignal":
        problems.append("marketplace.json: plugin name is not quotasignal")
    if not (ROOT / "skills/quotasignal/SKILL.md").is_file():
        problems.append("skills/quotasignal/SKILL.md is missing")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
