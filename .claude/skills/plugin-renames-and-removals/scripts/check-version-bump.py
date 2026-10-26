#!/usr/bin/env python3
"""Version bump: every plugin whose files changed since <base> has a new version and its entry.

Users get a change only when the plugin.json version changes, so a plugin whose committed files
differ from <base> (`git diff <base>...HEAD`) must carry a version above the one at <base> and a
non-empty CHANGELOG.md section for it. A change limited to the plugin's README.md needs no bump;
every other file does, CHANGELOG.md included. A new plugin (no plugin.json at <base>) and a
removed one are skipped. It reads committed changes only: commit before running it.

It runs `git diff` and `git show` and reads plugin files: it never writes or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments (it takes one: the base ref).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import cast

DOC_ONLY = frozenset({"README.md"})
BUMP = ".claude/skills/plugin-renames-and-removals/scripts/bump-version.py"
_decode: Callable[[str], object] = json.JSONDecoder().decode


class GitError(Exception):
    """A git command that failed where failure is not expected."""

    def __init__(self, command: str, detail: str) -> None:
        """Name the git command and why it failed."""
        super().__init__(f"git {command} failed: {detail}")


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in `root` and return its result; raises GitError when git is not on PATH."""
    exe = shutil.which("git")
    if exe is None:
        raise GitError(args[0] if args else "", "git is not on PATH")
    return subprocess.run(
        [exe, "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def core(version: str) -> tuple[int, int, int]:
    """MAJOR.MINOR.PATCH of a version, pre-release and build metadata dropped."""
    parts = re.split(r"[-+]", version)[0].split(".")
    nums = [int(p) if p.isdigit() else 0 for p in parts[:3]]
    nums += [0] * (3 - len(nums))
    return nums[0], nums[1], nums[2]


def changelog_section(text: str, version: str) -> str | None:
    """Body of the `## [version]` section, stripped; None when there is no such heading."""
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]:|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def manifest_version(text: str) -> str | None:
    """The `version` string of a plugin.json text, or None."""
    try:
        data = _decode(text)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    version = cast("dict[str, object]", data).get("version")
    return version if isinstance(version, str) else None


def changed_by_plugin(root: Path, base: str) -> dict[str, list[str]]:
    """The committed files changed since `base`, grouped by plugin, paths inside the plugin."""
    commits = f"{base}...HEAD"
    diff = git(root, "diff", "--name-only", commits)
    if diff.returncode != 0:
        raise GitError("diff " + commits, diff.stderr.strip())
    by_plugin: dict[str, list[str]] = {}
    for path in diff.stdout.splitlines():
        match = re.match(r"^plugins/([^/]+)/(.+)$", path)
        if match:
            by_plugin.setdefault(match.group(1), []).append(match.group(2))
    return by_plugin


def check(root: Path, base: str) -> tuple[list[str], list[str]]:
    """The errors, and the plugins whose files changed."""
    by_plugin = changed_by_plugin(root, base)
    errors: list[str] = []
    for name, files in by_plugin.items():
        plugin = root / "plugins" / name
        if not plugin.is_dir() or all(f in DOC_ONLY for f in files):
            continue
        shown = git(root, "show", f"{base}:plugins/{name}/.claude-plugin/plugin.json")
        if shown.returncode != 0:
            continue  # new plugin: nothing to compare against
        base_version = manifest_version(shown.stdout) or "0.0.0"
        manifest = plugin / ".claude-plugin" / "plugin.json"
        text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""
        version = manifest_version(text)
        if version is None or core(version) <= core(base_version):
            fix = f"Run {BUMP} {name} <level>."
            changed = f"files changed ({', '.join(files)})"
            errors.append(f"[plugins/{name}] {changed} but version is still {base_version}. {fix}")
            continue
        changelog = plugin / "CHANGELOG.md"
        notes = changelog.read_text(encoding="utf-8") if changelog.is_file() else ""
        if not changelog_section(notes, version):
            errors.append(f"[plugins/{name}] CHANGELOG.md has no entry for {version}")
    return errors, list(by_plugin)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1:
        _ = sys.stderr.write("usage: check-version-bump.py <base-ref>\n")
        return 2
    try:
        errors, checked = check(repo_root(), argv[0])
    except GitError as e:
        _ = sys.stderr.write(f"✖ {e}\n")
        return 1
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ Version bumps OK ({', '.join(checked) or 'no plugin changes'})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
