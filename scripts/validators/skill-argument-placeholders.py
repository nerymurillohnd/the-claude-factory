#!/usr/bin/env python3
r"""Skill argument placeholders: no SKILL.md body holds a bare `$N` that Claude Code would replace.

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

Every bare `$N` is an error, even one the author meant as an argument, so a reader never has to
guess which is which: write `$ARGUMENTS[N]` for an argument, `\$N` for a literal dollar-digit
(Claude then reads `$N`), or `${N}` for a shell positional parameter.

The skills it reads, each `<dir>/SKILL.md` one level under a skills directory:

- plugins/<plugin>/skills/, the default scan
  (https://code.claude.com/docs/en/plugins/manifest-reference#skills);
- each directory that `skills` in plugins/<plugin>/.claude-plugin/plugin.json names, alone or in
  an array; "." or "./" is the plugin root holding a SKILL.md itself;
- .claude/skills/, the project skills of this repository.

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
FRONTMATTER = "---"
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


def bare_placeholders(text: str) -> Iterator[tuple[int, int, str]]:
    """(line, column, token), both 1-based, of each bare `$N` in the body of `text`."""
    lines = text.splitlines()
    for index in range(body_start(lines), len(lines)):
        line = lines[index]
        for match in PLACEHOLDER.finditer(line):
            if not escaped(line, match.start()):
                yield index + 1, match.start() + 1, match.group()


def check_skill(skill_file: Path, report: Report) -> None:
    """One SKILL.md: its body holds no bare `$N`."""
    text = read_text(skill_file, report)
    if text is None:
        return
    rel = report.rel(skill_file)
    for line, column, token in bare_placeholders(text):
        digits = token[1:]
        problem = f'bare "{token}" is replaced by the skill\'s argument {int(digits)}'
        argument = f'"$ARGUMENTS[{int(digits)}]" for the argument'
        literal = f'"\\{token}" for a literal "{token}"'
        shell = f'"${{{digits}}}" for a shell parameter'
        report.error(
            f"{rel}:{line}:{column}", f"{problem}; write {argument}, {literal}, or {shell}"
        )


def skill_dirs(skills_root: Path) -> Iterator[Path]:
    """Each directory one level under `skills_root` that holds a SKILL.md, in name order."""
    if not skills_root.is_dir():
        return
    for entry in sorted(skills_root.iterdir()):
        if entry.is_dir() and (entry / SKILL_FILE).is_file():
            yield entry


def manifest_paths(plugin: Path, report: Report) -> list[str]:
    """The paths MANIFEST_FIELD in the plugin's plugin.json names, in order."""
    manifest_file = plugin / ".claude-plugin" / "plugin.json"
    if not manifest_file.is_file():
        return []
    text = read_text(manifest_file, report)
    if text is None:
        return []
    try:
        manifest = _decode(text)
    except ValueError as e:
        report.error(report.rel(manifest_file), f"cannot be read as JSON: {e}")
        return []
    if not isinstance(manifest, JsonObject):
        return []
    value = manifest.get(MANIFEST_FIELD)
    items: list[object] = value if is_array(value) else [value]
    return [v for v in items if isinstance(v, str)]


def plugin_skill_files(plugin: Path, report: Report) -> list[Path]:
    """Every SKILL.md the plugin holds, once each: the default directory, then the manifest's."""
    found: dict[Path, Path] = {}
    roots = [plugin / DEFAULT_DIR]
    for declared in manifest_paths(plugin, report):
        target = plugin / declared
        # A path outside the plugin or missing is skill-names-consistency.py's error to report.
        if target.resolve().is_relative_to(plugin.resolve()) and target.is_dir():
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


def check(root: Path) -> tuple[list[str], int]:
    """Every error under `root`, and how many SKILL.md files were read."""
    report = Report(root)
    files: list[Path] = []
    plugins_dir = root / "plugins"
    if plugins_dir.is_dir() and not plugins_dir.is_symlink():
        for plugin in sorted(p for p in plugins_dir.iterdir() if p.is_dir() and not p.is_symlink()):
            files.extend(plugin_skill_files(plugin, report))
    files.extend(d / SKILL_FILE for d in skill_dirs(root / ".claude" / "skills"))
    for skill_file in files:
        check_skill(skill_file, report)
    return report.errors, len(files)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/skill-argument-placeholders.py\n")
        return 2
    errors, count = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill argument placeholder checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {count} SKILL.md body(ies) hold no bare $N argument placeholder\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
