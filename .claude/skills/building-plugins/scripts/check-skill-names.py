#!/usr/bin/env python3
"""Skill names: every skill of plugins/<plugin> names itself after its directory.

The skills it reads, as Claude Code loads them (https://code.claude.com/docs/en/plugins/components
and manifest-reference, `skills`): each `<dir>/SKILL.md` under plugins/<plugin>/skills/; each
directory that `skills` in .claude-plugin/plugin.json names, either one folder holding SKILL.md
directly, named after that folder ("." or "./" is the plugin root, named after the plugin), or a
directory of `<dir>/SKILL.md` folders; and, with no skills/ and no `skills` key, a SKILL.md at the
plugin root, the plugin's single skill, named after the plugin.

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


def declared_dirs(plugin: Path, errors: list[str]) -> tuple[list[Path], bool]:
    """The directories `skills` in plugin.json names, inside the plugin, and whether it is set."""
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return [], False
    try:
        data = _decode(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errors.append(
            f"[plugins/{plugin.name}/.claude-plugin/plugin.json] cannot be read as JSON: {e}"
        )
        return [], False
    if not isinstance(data, dict) or "skills" not in data:
        return [], False
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
    return found, True


def skill_name(folder: Path, plugin: Path) -> str:
    """The name a skill folder must carry: its directory's, or the plugin's for the plugin root."""
    return plugin.name if folder.resolve() == plugin.resolve() else folder.name


def skills_of(plugin: Path, errors: list[str]) -> list[tuple[Path, str]]:
    """(SKILL.md, the name it must carry) for every skill of the plugin, once each.

    `skills/` holds one folder per skill. Each directory `skills` in plugin.json names is either
    one folder holding SKILL.md directly or a directory of skill folders. With no `skills/` and no
    `skills` key, a SKILL.md at the plugin root loads as the plugin's single skill.
    """
    found: dict[Path, tuple[Path, str]] = {}
    declared, has_key = declared_dirs(plugin, errors)
    default = plugin / "skills"
    if not has_key and not default.is_dir() and (plugin / "SKILL.md").is_file():
        _ = found.setdefault(plugin.resolve(), (plugin / "SKILL.md", plugin.name))
    for root in declared:
        if (root / "SKILL.md").is_file():
            _ = found.setdefault(root.resolve(), (root / "SKILL.md", skill_name(root, plugin)))
    for root in [default, *(d for d in declared if not (d / "SKILL.md").is_file())]:
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                _ = found.setdefault(entry.resolve(), (entry / "SKILL.md", entry.name))
    return list(found.values())


def frontmatter(skill_file: Path) -> list[str] | str:
    """The lines between the opening and closing `---`, or why there are none."""
    missing = 'has no frontmatter between a first line "---" and a closing "---"'
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError) as e:
        return f"cannot be read as UTF-8 text: {e}"
    if not lines or lines[0].rstrip() != "---":
        return missing
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    return missing if end is None else lines[1:end]


def name_problem(skill_file: Path, expected: str) -> str | None:
    """Why the frontmatter `name` of `skill_file` is not `expected`, or None when it is."""
    lines = frontmatter(skill_file)
    if isinstance(lines, str):
        return lines
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
