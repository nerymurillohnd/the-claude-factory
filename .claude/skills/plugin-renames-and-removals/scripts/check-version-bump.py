#!/usr/bin/env python3
"""Version bump: every plugin whose files changed since <base> has a new version and its entry.

Users get a change only when the plugin.json version changes, so a plugin whose committed files
differ from <base> (`git diff <base>...HEAD`) must carry the next version of the one at <base>,
exactly one patch, minor or major step above it, and a non-empty CHANGELOG.md section for it. A
jump that skips a version fails. A step from 0.x to 1.0.0 passes with a note: it needs Nery's
explicit authorization (release-and-versioning, rule 4). A change limited to the plugin's
documentation (README.md, LICENSE, NOTICE.txt) needs no bump; every other file does,
CHANGELOG.md included. A renamed plugin is
compared with its old name's version at <base>: the rename is a `renames` entry that HEAD adds to
.claude-plugin/marketplace.json, or a plugin.json that git sees moved from plugins/<old>/. A rename
breaks the commands users type, so its patch step fails (plugin-renames-and-removals, rule 3), and
a move git sees without its `renames` entry fails too. A new plugin (no plugin.json at <base> under
its name or an old one) and a removed one are skipped. It reads committed changes only: commit
before running it.

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

DOC_ONLY = frozenset({"README.md", "LICENSE", "NOTICE.txt"})
BUMP = ".claude/skills/release-and-versioning/scripts/bump-version.py"
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


def next_versions(version: str) -> tuple[str, str, str]:
    """The patch, minor and major versions one step above `version`."""
    major, minor, patch = core(version)
    return f"{major}.{minor}.{patch + 1}", f"{major}.{minor + 1}.0", f"{major + 1}.0.0"


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


def renames_map(root: Path, ref: str) -> dict[str, str | None]:
    """The `renames` map of .claude-plugin/marketplace.json at `ref`; empty when it has none."""
    shown = git(root, "show", f"{ref}:.claude-plugin/marketplace.json")
    try:
        data = _decode(shown.stdout) if shown.returncode == 0 else None
    except ValueError:
        data = None
    renames = cast("dict[str, object]", data).get("renames") if isinstance(data, dict) else None
    if not isinstance(renames, dict):
        return {}
    entries = cast("dict[object, object]", renames).items()
    return {k: v for k, v in entries if isinstance(k, str) and (v is None or isinstance(v, str))}


def renamed_since(root: Path, base: str) -> tuple[dict[str, str], set[str]]:
    """The plugins renamed since `base`, and those of them missing their `renames` entry.

    The first is new name -> old name: each `renames` entry HEAD adds, then each plugin.json git
    sees moved from one plugin directory to another. The second holds the new names git sees moved
    whose `renames` entry HEAD does not add.
    """
    before = renames_map(root, base)
    added = {old: new for old, new in renames_map(root, "HEAD").items() if old not in before}
    renamed = {new: old for old, new in added.items() if new is not None}
    commits = f"{base}...HEAD"
    manifests = "plugins/*/.claude-plugin/plugin.json"
    diff = git(root, "diff", "-M", "--name-status", commits, "--", manifests)
    if diff.returncode != 0:
        raise GitError("diff -M " + commits, diff.stderr.strip())
    unregistered: set[str] = set()
    for line in diff.stdout.splitlines():
        status, *paths = line.split("\t")
        if not status.startswith("R") or len(paths) != len(("old", "new")):
            continue
        old, new = (re.match(r"^plugins/([^/]+)/", f) for f in paths)
        if old is None or new is None or old.group(1) == new.group(1):
            continue
        if new.group(1) not in renamed and old.group(1) not in added:
            renamed[new.group(1)] = old.group(1)
            unregistered.add(new.group(1))
    return renamed, unregistered


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


def base_manifest(root: Path, base: str, name: str, old: str | None) -> str | None:
    """The plugin.json text at `base`, under the plugin's old name when it was renamed."""
    for plugin in (name, old):
        if plugin is not None:
            shown = git(root, "show", f"{base}:plugins/{plugin}/.claude-plugin/plugin.json")
            if shown.returncode == 0:
                return shown.stdout
    return None


def bump_error(
    name: str, files: list[str], base_version: str, version: str, old: str | None
) -> str | None:
    """Why `version` is not the next version of `base_version`, or None when it is."""
    if core(version) <= core(base_version):
        fix = f"Run {BUMP} {name} <level>."
        changed = f"files changed ({', '.join(files)})"
        return f"[plugins/{name}] {changed} but version is still {base_version}. {fix}"
    allowed = next_versions(base_version)
    if "{}.{}.{}".format(*core(version)) not in allowed:
        steps = f"{allowed[0]}, {allowed[1]} or {allowed[2]}"
        fix = f"Run {BUMP} {name} <level> once from {base_version}."
        jump = f"version jumps from {base_version} to {version}"
        return f"[plugins/{name}] {jump}; one step above is {steps}. {fix}"
    if old is not None and "{}.{}.{}".format(*core(version)) == allowed[0]:
        level = "minor" if core(base_version)[0] == 0 else "major"
        fix = f"Run {BUMP} {name} {level} once from {base_version}."
        breaking = f"renamed from {old}, a breaking change, but {version} is a patch"
        return f"[plugins/{name}] {breaking}. {fix}"
    return None


def check(root: Path, base: str) -> tuple[list[str], list[str], list[str]]:
    """The errors, the cautions that do not fail, and the plugins whose files changed."""
    by_plugin = changed_by_plugin(root, base)
    renamed, unregistered = renamed_since(root, base)
    errors: list[str] = []
    cautions: list[str] = []
    for name, files in by_plugin.items():
        plugin = root / "plugins" / name
        if not plugin.is_dir() or all(f in DOC_ONLY for f in files):
            continue
        old = renamed.get(name)
        shown = base_manifest(root, base, name, old)
        if shown is None:
            continue  # new plugin: nothing to compare against
        if name in unregistered:
            entry = f'"{old}": "{name}"'
            errors.append(f"[plugins/{name}] moved from plugins/{old}; add renames entry {entry}")
        base_version = manifest_version(shown) or "0.0.0"
        manifest = plugin / ".claude-plugin" / "plugin.json"
        text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""
        version = manifest_version(text) or "0.0.0"
        error = bump_error(name, files, base_version, version, old)
        if error is not None:
            errors.append(error)
            continue
        if core(base_version)[0] == 0 and core(version)[0] == 1:
            promise = f"{base_version} → {version} promises a stable interface"
            rule = "Nery's explicit authorization (release-and-versioning, rule 4)"
            cautions.append(f"[plugins/{name}] {promise}: it needs {rule}.")
        changelog = plugin / "CHANGELOG.md"
        notes = changelog.read_text(encoding="utf-8") if changelog.is_file() else ""
        if not changelog_section(notes, version):
            errors.append(f"[plugins/{name}] CHANGELOG.md has no entry for {version}")
    return errors, cautions, list(by_plugin)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1:
        _ = sys.stderr.write("usage: check-version-bump.py <base-ref>\n")
        return 2
    try:
        errors, cautions, checked = check(repo_root(), argv[0])
    except GitError as e:
        _ = sys.stderr.write(f"✖ {e}\n")
        return 1
    if cautions:
        _ = sys.stderr.write("\n".join(f"! {c}" for c in cautions) + "\n")
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ Version bumps OK ({', '.join(checked) or 'no plugin changes'})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
