#!/usr/bin/env python3
"""Skill names: every skill of plugins/<plugin> names itself after its directory.

The skills it reads: each `<dir>/SKILL.md` under plugins/<plugin>/skills/, and under each
directory that `skills` in the plugin's .claude-plugin/plugin.json names; "." or "./" is the plugin
root holding a SKILL.md itself, named after the plugin.

For each SKILL.md, the `name:` line of its frontmatter (the lines between a first line `---` and
the next `---`) must appear once, and its value, written alone on that line, must equal the
directory name: kebab-case and at most 64 characters. A value that equals the kebab-case directory
name is already plain text with no quotes, no YAML syntax and nothing on later lines.

It reads files only: it never imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments.
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import re
import sys
from typing import cast

MAX_NAME = 64
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME_LINE = re.compile(r"name[ \t]*:(.*)")
USAGE = "usage: .claude/skills/building-plugins/scripts/check-skill-names.py <plugin>\n"
_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def declared_dirs(plugin: Path, errors: list[str]) -> list[Path]:
    """The directories `skills` in plugin.json names, inside the plugin."""
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return []
    try:
        data = _decode(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errors.append(f"[{manifest}] cannot be read as JSON: {e}")
        return []
    if not isinstance(data, dict):
        return []
    value = cast("dict[str, object]", data).get("skills")
    items = cast("list[object]", value) if isinstance(value, list) else [value]
    found: list[Path] = []
    for item in items:
        if not isinstance(item, str):
            continue
        target = plugin / item
        if not target.resolve().is_relative_to(plugin.resolve()):
            errors.append(f'[plugin.json skills] "{item}" resolves outside the plugin')
        elif not target.is_dir():
            errors.append(f'[plugin.json skills] "{item}" names a directory that does not exist')
        else:
            found.append(target)
    return found


def skills_of(plugin: Path, errors: list[str]) -> list[tuple[Path, str]]:
    """(SKILL.md, the name it must carry) for every skill of the plugin, once each."""
    found: dict[Path, tuple[Path, str]] = {}
    for root in [plugin / "skills", *declared_dirs(plugin, errors)]:
        if root.resolve() == plugin.resolve():
            if (plugin / "SKILL.md").is_file():
                _ = found.setdefault(plugin.resolve(), (plugin / "SKILL.md", plugin.name))
            continue
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                _ = found.setdefault(entry.resolve(), (entry / "SKILL.md", entry.name))
    return list(found.values())


def frontmatter(skill_file: Path) -> list[str] | None:
    """The lines between the opening and closing `---`, or None when there is no frontmatter."""
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    return None if end is None else lines[1:end]


def name_problem(skill_file: Path, expected: str) -> str | None:
    """Why the frontmatter `name` of `skill_file` is not `expected`, or None when it is."""
    lines = frontmatter(skill_file)
    if lines is None:
        return 'has no frontmatter between a first line "---" and a closing "---"'
    values = [m.group(1).strip() for line in lines if (m := NAME_LINE.match(line))]
    if not values:
        return 'has no "name" field'
    if len(values) > 1:
        return '"name" is defined more than once'
    if not KEBAB.fullmatch(expected) or len(expected) > MAX_NAME:
        return (
            f'its directory "{expected}" is not a kebab-case name of at most {MAX_NAME} characters'
        )
    if values[0] != expected:
        return f'"name" is `{values[0]}`; write `{expected}`, its directory name, alone and plain'
    return None


def check(root: Path, name: str) -> tuple[list[str], int]:
    """Every error for plugins/<name>, and how many skills were checked."""
    plugin = root / "plugins" / name
    if plugin.is_symlink() or not plugin.is_dir():
        return [f"[plugins/{name}] is not a plugin directory"], 0
    errors: list[str] = []
    skills = skills_of(plugin, errors)
    for skill_file, expected in skills:
        problem = name_problem(skill_file, expected)
        if problem is not None:
            errors.append(f"[{skill_file.relative_to(root).as_posix()}] {problem}")
    return errors, len(skills)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1 or not argv[0] or "/" in argv[0]:
        _ = sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    errors, count = check(repo_root().resolve(), name)
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill name check failed for {name}: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {count} skill name(s) of {name} match their directory\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
