#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["pyyaml"]
# ///
"""Skill names: every SKILL.md names its skill after its directory, as one flat plain name.

The skills it reads, each `<dir>/SKILL.md` one level under a skills directory:

- plugins/<plugin>/skills/, the default scan
  (https://code.claude.com/docs/en/plugins/manifest-reference#skills);
- each directory that `skills` in plugins/<plugin>/.claude-plugin/plugin.json names, alone or in
  an array; "." or "./" is the plugin root holding a SKILL.md itself, named after the plugin;
- .claude/skills/, the project skills of this repository.

The frontmatter is the YAML between a first line `---` and the next `---` line
(https://code.claude.com/docs/en/skills#frontmatter-reference). Its `name` must be
(https://agentskills.io/specification#name-field):

- present once and equal to the directory name;
- at most 64 characters;
- free of quotes of any kind (' " ` and their typographic forms);
- flattened text: a plain YAML string written on one line, so the text in the file is exactly
  the name a YAML parser reads. A quoted or block scalar (| or >), a value folded over several
  lines, an anchor, alias or tag, or a plain value YAML reads as a boolean, number, date or null
  is an error.

PyYAML's safe loader composes the frontmatter into nodes without constructing any object; each
node keeps its source span, which is compared with the value it reads. It reads files only: it
never imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none) or without
PyYAML.
Maintainer tooling: uv runs it on Python 3.15 from its inline metadata; run it by path or with
`uv run <script>`. Any interpreter named before the path (`python3 <script>`) skips the shebang,
so PyYAML is missing and it says so instead of a traceback.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, Protocol, TypeIs

try:
    import yaml
    from yaml.error import Mark
except ModuleNotFoundError:
    _ = sys.stderr.write("✖ PyYAML is missing: run this script by path or with uv run <script>\n")
    sys.exit(2)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

MAX_NAME = 64
SKILL_FILE = "SKILL.md"
DEFAULT_DIR = "skills"
MANIFEST_FIELD = "skills"
FRONTMATTER = "---"
STR_TAG = "tag:yaml.org,2002:str"
# A top-level `name` key line: unindented, the key, optional spaces, a colon, then a space or EOL.
NAME_KEY = re.compile(r"name[ \t]*:(?:[ \t]|$)")
# Quote characters by code point: ASCII ' " and `; the single and double typographic quotes
# U+2018-U+201F; the guillemets U+00AB, U+00BB, U+2039 and U+203A.
QUOTES = frozenset(map(chr, (0x27, 0x22, 0x60, *range(0x2018, 0x2020), 0xAB, 0xBB, 0x2039, 0x203A)))


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


class DuplicateKeyError(ValueError):
    """A JSON object names the same key twice; the decoder would keep only the last one."""


def _object(pairs: list[tuple[str, object]]) -> JsonObject:
    obj = JsonObject()
    for key, value in pairs:
        if key in obj:
            msg = f'duplicate key "{key}"'
            raise DuplicateKeyError(msg)
        obj[key] = value
    return obj


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_object).decode


def is_array(value: object) -> TypeIs[list[object]]:
    """Narrow a decoded value to a list; its items are still unchecked objects."""
    return isinstance(value, list)


class NodeFields(Protocol):
    """The fields read from a PyYAML node, as unchecked objects: its stubs type them as Any."""

    @property
    def value(self) -> object:
        """A scalar's text, or a mapping's list of (key node, value node) pairs."""
        ...

    @property
    def start_mark(self) -> object:
        """Where the node starts in its source, a yaml.error.Mark."""
        ...

    @property
    def end_mark(self) -> object:
        """Where the node ends in its source, a yaml.error.Mark."""
        ...


def node_value(node: NodeFields) -> object:
    """The value of a PyYAML node, typed as the unchecked object it is."""
    return node.value


def scalar_text(node: NodeFields, source: str) -> tuple[str, str] | None:
    """(the text YAML reads, the text written in `source`) of a scalar node, or None."""
    value, start, end = node.value, node.start_mark, node.end_mark
    if isinstance(value, str) and isinstance(start, Mark) and isinstance(end, Mark):
        return value, source[start.index : end.index]
    return None


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
    except FileNotFoundError:
        report.error(scope, "is missing")
    except (OSError, ValueError) as e:
        report.error(scope, f"cannot be read: {e}")
    return None


def frontmatter(text: str) -> list[str] | None:
    """The lines between the opening and closing `---`, or None when there is no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != FRONTMATTER:
        return None
    for end in range(1, len(lines)):
        if lines[end].rstrip() == FRONTMATTER:
            return lines[1:end]
    return None


def name_entry(lines: list[str]) -> str:
    """The `name` entry alone: its key line and every indented or blank line that continues it.

    Only this entry is parsed: Claude Code reads the other fields more leniently than strict
    YAML (an unquoted ": " inside a description loads), so they are not this script's to judge.
    Raises ValueError when the frontmatter has no top-level `name` key, or more than one.
    """
    starts = [i for i, line in enumerate(lines) if NAME_KEY.match(line)]
    if not starts:
        msg = 'has no "name" field'
        raise ValueError(msg)
    if len(starts) > 1:
        msg = '"name" is defined more than once'
        raise ValueError(msg)
    end = starts[0] + 1
    while end < len(lines) and (lines[end][:1] in {" ", "\t"} or not lines[end].strip()):
        end += 1
    return "\n".join(lines[starts[0] : end]).rstrip() + "\n"


def name_node(entry: str) -> yaml.Node | str:
    """The value node of the `name` entry, or why YAML cannot read the entry."""
    try:
        root = yaml.SafeLoader(entry).get_single_node()
    except yaml.YAMLError as e:
        return f'"name" is not valid YAML: {" ".join(str(e).split())}'
    pairs = node_value(root) if isinstance(root, yaml.MappingNode) else None
    if is_array(pairs) and len(pairs) == 1:
        match pairs[0]:
            case (yaml.ScalarNode(), yaml.Node() as value):
                return value
            case _:
                pass
    return '"name" is not one key and its value'


def text_problems(value: str) -> list[str]:
    """Why the text of a `name` is too long, quoted or holds control characters."""
    problems: list[str] = []
    if len(value) > MAX_NAME:
        problems.append(f'"name" has {len(value)} characters; the limit is {MAX_NAME}')
    quotes = sorted({c for c in value if c in QUOTES})
    if quotes:
        problems.append(f'"name" contains quotes ({" ".join(quotes)})')
    if not value.isprintable():
        problems.append('"name" contains a tab or another control character')
    return problems


def name_problems(source: str, node: yaml.Node) -> tuple[str | None, list[str]]:
    """(the name, None when unreadable) and why it is not a flat, unquoted, short name."""
    if not isinstance(node, yaml.ScalarNode):
        return None, ['"name" must be a string, not a list or a mapping']
    texts = scalar_text(node, source)
    if texts is None:
        return None, ['"name" is a scalar with no text or source position']
    value, written = texts
    if value == "":
        return value, ['"name" is empty']
    if written != value:
        flat = " ".join(written.split())
        return value, [f'"name" is written as `{flat}`; write the name alone, plain, on one line']
    if node.tag != STR_TAG:
        kind = node.tag.rsplit(":", 1)[-1]
        return value, [f'"name" "{value}" reads as a YAML {kind}, not as text']
    return value, text_problems(value)


def check_skill(skill_dir: Path, expected: str, report: Report) -> None:
    """One skill directory: its SKILL.md names it `expected` as flat plain text."""
    skill_file = skill_dir / SKILL_FILE
    scope = report.rel(skill_file)
    text = read_text(skill_file, report)
    if text is None:
        return
    lines = frontmatter(text)
    if lines is None:
        report.error(scope, 'has no frontmatter between a first line "---" and a closing "---"')
        return
    try:
        entry = name_entry(lines)
    except ValueError as e:
        report.error(scope, str(e))
        return
    node = name_node(entry)
    if isinstance(node, str):
        report.error(scope, node)
        return
    value, problems = name_problems(entry, node)
    for p in problems:
        report.error(scope, p)
    if value is not None and not problems and value != expected:
        report.error(scope, f'"name" "{value}" must equal its directory name "{expected}"')


def skill_dirs(skills_root: Path) -> Iterator[Path]:
    """Each directory one level under `skills_root` that holds a SKILL.md, in name order."""
    if not skills_root.is_dir():
        return
    for entry in sorted(skills_root.iterdir()):
        if entry.is_dir() and (entry / SKILL_FILE).exists():
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
        report.error(report.rel(manifest_file), "must hold a JSON object")
        return []
    value = manifest.get(MANIFEST_FIELD)
    items: list[object] = value if is_array(value) else [value]
    return [v for v in items if isinstance(v, str)]


def skill_roots(plugin: Path, report: Report) -> list[Path]:
    """The default skills directory, then each directory the manifest names inside the plugin."""
    roots = [plugin / DEFAULT_DIR]
    for declared in manifest_paths(plugin, report):
        scope = f"{report.rel(plugin)} plugin.json {MANIFEST_FIELD}"
        target = plugin / declared
        if not target.resolve().is_relative_to(plugin.resolve()):
            report.error(scope, f'"{declared}" resolves outside the plugin')
        elif not target.is_dir():
            report.error(scope, f'"{declared}" names a directory that does not exist')
        else:
            roots.append(target)
    return roots


def plugin_skills(plugin: Path, report: Report) -> list[tuple[Path, str]]:
    """(skill directory, the name it must carry) for every skill the plugin holds, once each."""
    found: dict[Path, tuple[Path, str]] = {}
    for root in skill_roots(plugin, report):
        if root.resolve() == plugin.resolve():
            if (plugin / SKILL_FILE).exists():
                _ = found.setdefault(plugin.resolve(), (plugin, plugin.name))
            continue
        for skill_dir in skill_dirs(root):
            _ = found.setdefault(skill_dir.resolve(), (skill_dir, skill_dir.name))
    return list(found.values())


def check(root: Path) -> tuple[list[str], int]:
    """Every error under `root`, and how many skills were checked."""
    report = Report(root)
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        report.error("plugins/", "must be a directory, not a symlink")
        return report.errors, 0
    skills: list[tuple[Path, str]] = []
    for plugin in sorted(p for p in plugins_dir.iterdir() if p.is_dir() and not p.is_symlink()):
        skills.extend(plugin_skills(plugin, report))
    skills.extend((d, d.name) for d in skill_dirs(root / ".claude" / "skills"))
    for skill_dir, expected in skills:
        check_skill(skill_dir, expected, report)
    return report.errors, len(skills)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/skill-names-consistency.py\n")
        return 2
    errors, count = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill name checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {count} skill name(s) are flat, unquoted and match their directory\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
