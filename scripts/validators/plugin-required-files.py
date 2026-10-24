#!/usr/bin/env python3
"""Plugin required files: every plugin ships its manifest, README, changelog and license.

Every real directory in plugins/ is a plugin, and each must hold, as a regular file inside the
repository: .claude-plugin/plugin.json, README.md, CHANGELOG.md and LICENSE. Each error names
the plugin, the file and why it fails: missing, a broken symlink, not a regular file, or a
symlink that leaves the repository. A symlink in plugins/ in place of a plugin directory is an
error too.

It reads the file system only: it never opens the files, imports or runs plugin code, starts a
process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

import os
from pathlib import Path
import sys

REQUIRED = (".claude-plugin/plugin.json", "README.md", "CHANGELOG.md", "LICENSE")


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def file_problem(path: Path, root: Path) -> str | None:
    """Why `path` is not a usable required file, or None when it is."""
    if path.is_symlink() and not path.resolve().is_relative_to(root):
        return "is a symlink that resolves outside the repository"
    if not path.exists():
        return "is a broken symlink" if path.is_symlink() else "is missing"
    if not path.is_file():
        return "is not a regular file"
    return None


def check(root: Path) -> list[str]:
    """Every missing or unusable required file under `root`, in a stable order."""
    root = root.resolve()
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        return ["[plugins/] must be a directory, not a symlink"]
    errors: list[str] = []
    for plugin in sorted(plugins_dir.iterdir()):
        scope = f"plugins/{plugin.name}"
        if plugin.is_symlink():
            errors.append(f"[{scope}] must be a directory, not a symlink")
            continue
        if not plugin.is_dir():
            continue
        for name in REQUIRED:
            problem = file_problem(plugin / name, root)
            if problem is not None:
                errors.append(f"[{scope}] {name} {problem}")
    return errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/plugin-required-files.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Plugin required files check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ Every plugin has {', '.join(REQUIRED)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
