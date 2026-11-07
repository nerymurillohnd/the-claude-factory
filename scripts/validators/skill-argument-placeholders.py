#!/usr/bin/env python3
r"""Skill argument placeholders: no skill or command body holds a bare `$N` Claude Code replaces.

Claude Code replaces `$N` in a skill's body with the skill's Nth argument, 0-based
(https://code.claude.com/docs/en/skills#available-string-substitutions: "`$N`: Shorthand for
`$ARGUMENTS[N]`"). Inside a code block too, so a shell `$1`, an awk `$0` or a price such as
`$5.00` reaches Claude as whatever the user typed after the skill's name. Checked on Claude Code
2.1.319 with a test skill invoked as `/probe alpha beta`:

- `$1`, `x$1`, `$1.00`, `$1-z`, `($1)`, `$1é` and `$01` expand: a `$`, one or more ASCII digits,
  and no ASCII letter, digit or `_` right after them;
- `$1y` and `$1_` stay as written: they are not placeholders, and this script accepts them;
- `\$1` arrives as `$1`: exactly one backslash right before the `$` escapes it. `\\$1` and
  `\\\$1` still expand, as the docs say for the doubled form;
- `${1}` and `$ARGUMENTS[1]` are never bare: `${1}` stays as written, `$ARGUMENTS[1]` is the
  explicit argument;
- the frontmatter is not substituted, so only the body after the closing `---` is read.

Command files get the same substitution: "Custom commands have been merged into skills"
(https://code.claude.com/docs/en/skills). Checked on Claude Code 2.1.319, invoked with
`alpha beta`: a project command in .claude/commands/, and plugin commands loaded with
`--plugin-dir` from the default commands/ folder, from a subdirectory of it, from a folder and a
file that `commands` in plugin.json names, and from the `source` and inline `content` of its
object map, each turned `$1` into `beta`, `\$1` into `$1` and left `${1}` unchanged.

Every bare `$N` is an error, even one the author meant as an argument, so a reader never has to
guess which is which: write `$ARGUMENTS[N]` for an argument, `\$N` for a literal dollar-digit
(Claude then reads `$N`), or `${N}` for a shell positional parameter.

The skills it reads, each `<dir>/SKILL.md` one level under a skills directory:

- plugins/<plugin>/skills/, the default scan
  (https://code.claude.com/docs/en/plugins/manifest-reference#skills);
- each directory that `skills` in plugins/<plugin>/.claude-plugin/plugin.json names, alone or in
  an array; "." or "./" is the plugin root holding a SKILL.md itself;
- .claude/skills/, the project skills of this repository.

The commands it reads, every `.md` file at any depth of a commands directory, because each
subdirectory becomes a `sub:name` command (https://code.claude.com/docs/en/skills, "How a skill
gets its command name"):

- plugins/<plugin>/commands/, only while plugin.json sets no `commands`: that key replaces the
  default folder, which then does not load
  (https://code.claude.com/docs/en/plugins/manifest-reference#commands);
- each file or directory that `commands` in plugin.json names, alone or in an array, and each
  `source` of its object map, when it resolves inside the plugin (a path outside it does not
  load, and `claude plugin validate` reports it);
- each inline `content` of that object map, read whole: it is the command's body;
- .claude/commands/, the project commands of this repository, when it exists.

Agents and a skill's reference files are not read: they receive no slash-command arguments.

It reads files only: it never imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, TypeIs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

SKILL_FILE = "SKILL.md"
DEFAULT_DIR = "skills"
MANIFEST_FIELD = "skills"
COMMANDS_DIR = "commands"
COMMANDS_FIELD = "commands"
COMMAND_SUFFIX = ".md"
FRONTMATTER = "---"
# What Path.resolve() raises for a path it cannot resolve (an embedded NUL, a symlink loop).
UNRESOLVABLE = (OSError, ValueError)
# A dollar, ASCII digits, and no ASCII word character after them: the form Claude Code replaces.
PLACEHOLDER = re.compile(r"\$[0-9]+(?![A-Za-z0-9_])")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


def _object(pairs: list[tuple[str, object]]) -> JsonObject:
    return JsonObject(pairs)


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_object).decode


def is_array(value: object) -> TypeIs[list[object]]:
    """Narrow a decoded value to a list; its items are still unchecked objects."""
    return isinstance(value, list)


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


class Report:
    """Collects errors as `[scope] message` lines."""

    def __init__(self, root: Path) -> None:
        """Start with no errors; every file read must resolve inside `root`."""
        self.root: Path = root.resolve()
        self.errors: list[str] = []

    def error(self, scope: str, message: str) -> None:
        """Record one error."""
        self.errors.append(f"[{scope}] {message}")

    def rel(self, path: Path) -> str:
        """`path` relative to the repository root when it is inside it, for messages."""
        resolved = path.resolve()
        if resolved.is_relative_to(self.root):
            return resolved.relative_to(self.root).as_posix()
        return str(path)


def read_text(path: Path, report: Report) -> str | None:
    """The UTF-8 text of `path`, or None after recording why it cannot be used."""
    scope = report.rel(path)
    try:
        if not path.resolve().is_relative_to(report.root):
            report.error(scope, "resolves outside the repository")
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, ValueError) as e:
        report.error(scope, f"cannot be read: {e}")
    return None


def body_start(lines: list[str]) -> int:
    """The index of the first body line: after the closing `---`, or 0 with no frontmatter."""
    if lines and lines[0].rstrip() == FRONTMATTER:
        for end in range(1, len(lines)):
            if lines[end].rstrip() == FRONTMATTER:
                return end + 1
    return 0


def escaped(line: str, dollar: int) -> bool:
    """Whether exactly one backslash stands right before the `$` at index `dollar`."""
    run = len(line[:dollar]) - len(line[:dollar].rstrip("\\"))
    return run == 1


def bare_placeholders(text: str, *, whole: bool = False) -> Iterator[tuple[int, int, str]]:
    """(line, column, token), both 1-based, of each bare `$N` in the body of `text`.

    `whole` reads every line, frontmatter or not.
    """
    lines = text.splitlines()
    for index in range(0 if whole else body_start(lines), len(lines)):
        line = lines[index]
        for match in PLACEHOLDER.finditer(line):
            if not escaped(line, match.start()):
                yield index + 1, match.start() + 1, match.group()


def check_text(text: str, scope: str, kind: str, report: Report, *, whole: bool = False) -> None:
    """One body holds no bare `$N`; `scope` prefixes the line and column of each error."""
    for line, column, token in bare_placeholders(text, whole=whole):
        digits = token[1:]
        problem = f'bare "{token}" is replaced by the {kind}\'s argument {int(digits)}'
        argument = f'"$ARGUMENTS[{int(digits)}]" for the argument'
        literal = f'"\\{token}" for a literal "{token}"'
        shell = f'"${{{digits}}}" for a shell parameter'
        fixes = f"write {argument}, {literal}, or {shell}"
        report.error(f"{scope}:{line}:{column}", f"{problem}; {fixes}")


def check_file(path: Path, kind: str, report: Report) -> None:
    """One SKILL.md or command file: its body holds no bare `$N`."""
    text = read_text(path, report)
    if text is not None:
        check_text(text, report.rel(path), kind, report)


def skill_dirs(skills_root: Path) -> Iterator[Path]:
    """Each directory one level under `skills_root` that holds a SKILL.md, in name order."""
    if not skills_root.is_dir():
        return
    for entry in sorted(skills_root.iterdir()):
        if entry.is_dir() and (entry / SKILL_FILE).is_file():
            yield entry


def command_files(target: Path) -> Iterator[Path]:
    """`target` when it is a file, or every `.md` file at any depth under it, in path order."""
    if target.is_file():
        yield target
    elif target.is_dir():
        yield from sorted(p for p in target.rglob(f"*{COMMAND_SUFFIX}") if p.is_file())


def read_manifest(plugin: Path, report: Report) -> JsonObject | None:
    """The plugin's plugin.json as an object, or None when it is missing or not one."""
    manifest_file = plugin / ".claude-plugin" / "plugin.json"
    if not manifest_file.is_file():
        return None
    text = read_text(manifest_file, report)
    if text is None:
        return None
    try:
        manifest = _decode(text)
    except ValueError as e:
        report.error(report.rel(manifest_file), f"cannot be read as JSON: {e}")
        return None
    return manifest if isinstance(manifest, JsonObject) else None


def string_items(value: object) -> list[str]:
    """`value` alone or as an array, keeping its strings, in order."""
    items: list[object] = value if is_array(value) else [value]
    return [v for v in items if isinstance(v, str)]


def inside(plugin: Path, declared: str) -> Path | None:
    """`plugin`/`declared` when it resolves inside the plugin, else None.

    A path that cannot be resolved at all (an embedded NUL, a symlink loop) is treated as one
    that does not resolve inside the plugin.
    """
    target = plugin / declared
    try:
        return target if target.resolve().is_relative_to(plugin.resolve()) else None
    except UNRESOLVABLE:
        return None


def plugin_skill_files(plugin: Path, manifest: JsonObject | None) -> list[Path]:
    """Every SKILL.md the plugin holds, once each: the default directory, then the manifest's."""
    found: dict[Path, Path] = {}
    roots = [plugin / DEFAULT_DIR]
    declared = string_items(manifest.get(MANIFEST_FIELD)) if manifest is not None else []
    for path in declared:
        target = inside(plugin, path)
        # A path outside the plugin or missing is skill-names-consistency.py's error to report.
        if target is not None and target.is_dir():
            roots.append(target)
    for root in roots:
        if root.resolve() == plugin.resolve():
            if (plugin / SKILL_FILE).is_file():
                _ = found.setdefault((plugin / SKILL_FILE).resolve(), plugin / SKILL_FILE)
            continue
        for skill_dir in skill_dirs(root):
            path = skill_dir / SKILL_FILE
            _ = found.setdefault(path.resolve(), path)
    return list(found.values())


def declared_commands(value: object) -> tuple[list[str], list[tuple[str, str]]]:
    """The paths a plugin.json `commands` value names, and its (key, inline content) pairs.

    No value means the default commands/ folder; any value replaces it.
    """
    if value is None:
        return [f"./{COMMANDS_DIR}"], []
    if not isinstance(value, JsonObject):
        return string_items(value), []
    paths: list[str] = []
    inline: list[tuple[str, str]] = []
    for key, entry in value.items():
        if isinstance(entry, JsonObject):
            paths += string_items(entry.get("source"))
            content = entry.get("content")
            if isinstance(content, str):
                inline.append((key, content))
    return paths, inline


def plugin_commands(
    plugin: Path, manifest: JsonObject | None
) -> tuple[list[Path], list[tuple[str, str]]]:
    """The plugin's command files, once each, and its inline (key, content) commands."""
    value = manifest.get(COMMANDS_FIELD) if manifest is not None else None
    declared, inline = declared_commands(value)
    found: dict[Path, Path] = {}
    for path in declared:
        # A path outside the plugin does not load; claude plugin validate reports it.
        target = inside(plugin, path)
        if target is not None:
            for command in command_files(target):
                _ = found.setdefault(command.resolve(), command)
    return list(found.values()), inline


def check(root: Path) -> tuple[list[str], int, int]:
    """Every error under `root`, and how many skills and commands were read."""
    report = Report(root)
    skills: list[Path] = []
    commands: list[Path] = []
    inline_count = 0
    plugins_dir = root / "plugins"
    if plugins_dir.is_dir() and not plugins_dir.is_symlink():
        for plugin in sorted(p for p in plugins_dir.iterdir() if p.is_dir() and not p.is_symlink()):
            manifest = read_manifest(plugin, report)
            skills.extend(plugin_skill_files(plugin, manifest))
            files, inline = plugin_commands(plugin, manifest)
            commands.extend(files)
            rel = report.rel(plugin / ".claude-plugin" / "plugin.json")
            for key, content in inline:
                scope = f"{rel}:{COMMANDS_FIELD}.{key}"
                check_text(content, scope, "command", report, whole=True)
            inline_count += len(inline)
    skills.extend(d / SKILL_FILE for d in skill_dirs(root / ".claude" / "skills"))
    commands.extend(command_files(root / ".claude" / COMMANDS_DIR))
    for skill_file in skills:
        check_file(skill_file, "skill", report)
    for command_file in commands:
        check_file(command_file, "command", report)
    return report.errors, len(skills), len(commands) + inline_count


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/skill-argument-placeholders.py\n")
        return 2
    errors, skills, commands = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill argument placeholder checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    counts = f"{skills} SKILL.md body(ies) and {commands} command(s)"
    _ = sys.stdout.write(f"✔ {counts} hold no bare $N argument placeholder\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
