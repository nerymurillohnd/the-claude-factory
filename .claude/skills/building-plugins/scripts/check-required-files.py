#!/usr/bin/env python3
"""Required files: plugins/<plugin>/ ships its manifest, README, changelog and license.

plugins/<plugin> must be a real directory, and it must hold, each as a regular file inside the
repository: .claude-plugin/plugin.json, README.md, CHANGELOG.md and LICENSE. Each error names the
file and why it fails: missing, a broken symlink, not a regular file, or a symlink that leaves
the repository.

It reads the file system only: it never opens the files, imports or runs plugin code, starts a
process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments.
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

import os
from pathlib import Path
import sys

REQUIRED = (".claude-plugin/plugin.json", "README.md", "CHANGELOG.md", "LICENSE")
USAGE = "usage: .claude/skills/building-plugins/scripts/check-required-files.py <plugin>\n"


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def file_problem(path: Path, root: Path) -> str | None:
    """Why `path` is not a usable required file, or None when it is."""
    if path.is_symlink() and not path.resolve().is_relative_to(root):
        return "is a symlink that resolves outside the repository"
    if not path.exists():
        return "is a broken symlink" if path.is_symlink() else "is missing"
    if not path.is_file():
        return "is not a regular file"
    return None


def check(root: Path, name: str) -> list[str]:
    """Every missing or unusable required file of plugins/<name>, in REQUIRED order."""
    root = root.resolve()
    plugin = root / "plugins" / name
    scope = f"plugins/{name}"
    if plugin.is_symlink():
        return [f"[{scope}] must be a directory, not a symlink"]
    if not plugin.is_dir():
        return [f"[{scope}] is not a plugin directory"]
    errors: list[str] = []
    for required in REQUIRED:
        problem = file_problem(plugin / required, root)
        if problem is not None:
            errors.append(f"[{scope}] {required} {problem}")
    return errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1 or not argv[0] or "/" in argv[0]:
        _ = sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    errors = check(repo_root(), name)
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Required files check failed for {name}: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ plugins/{name} has {', '.join(REQUIRED)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
