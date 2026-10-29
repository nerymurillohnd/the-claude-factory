"""scripts/validators/skill-names-consistency.py: only a flat, plain name of its directory passes.

The validator is a PEP 723 script, so each test runs it by path, in its own uv environment, on a
small repository under a temporary directory (TCF_ROOT); the last one runs it on this repository,
which must pass.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import override
import unittest

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "scripts" / "validators" / "skill-names-consistency.py"
ERROR = "✖ ["
QUOTE = "\u2019"  # RIGHT SINGLE QUOTATION MARK
NBSP = "\u00a0"  # NO-BREAK SPACE, which str.isprintable() rejects

# Each plugin skill directory and the `name` entry of its SKILL.md frontmatter.
NAMES = {
    "plain": "name: plain",
    "commented": "name: commented # a note",
    "mismatch": "name: other",
    "single-quoted": "name: 'single-quoted'",
    "double-quoted": 'name: "double-quoted"',
    "block": "name: |\n  block",
    "folded": "name: folded\n  over-lines",
    "anchor": "name: &a anchor",
    "tagged": "name: !!str tagged",
    "alias": "name: *missing",
    "yes": "name: yes",
    "on": "name: on",
    "123": "name: 123",
    "1.5": "name: 1.5",
    "2026-10-29": "name: 2026-10-29",
    "null": "name: null",
    "empty": "name:",
    "a" * 65: "name: " + "a" * 65,
    f"it{QUOTE}s": f"name: it{QUOTE}s",
    "spaced": f"name: no{NBSP}break",
    "tabbed": "name: tab\tbed",
    "flow-list": "name: [flow-list]",
    "mapping": "name:\n  key: mapping",
    "unclosed": "name: [unclosed",
}
# The one error each directory not listed here must not have: the start of its message, or the
# starts that are each acceptable.
EXPECTED: dict[str, str | tuple[str, ...]] = {
    "mismatch": '"name" "other" must equal its directory name "mismatch"',
    "single-quoted": "\"name\" is written as `'single-quoted'`",
    "double-quoted": '"name" is written as `"double-quoted"`',
    "block": '"name" is written as `| block`',
    "folded": '"name" is written as `folded over-lines`',
    "anchor": '"name" is written as `&a anchor`',
    "tagged": '"name" is written as `!!str tagged`',
    "alias": '"name" is not valid YAML',
    "yes": '"name" "yes" reads as a YAML bool, not as text',
    "on": '"name" "on" reads as a YAML bool, not as text',
    "123": '"name" "123" reads as a YAML int, not as text',
    "1.5": '"name" "1.5" reads as a YAML float, not as text',
    "2026-10-29": '"name" "2026-10-29" reads as a YAML timestamp, not as text',
    "null": '"name" "null" reads as a YAML null, not as text',
    "empty": '"name" is empty',
    "a" * 65: '"name" has 65 characters; the limit is 64',
    f"it{QUOTE}s": f'"name" contains quotes ({QUOTE})',
    "spaced": '"name" contains a tab or another control character',
    # A tab inside a plain scalar: a YAML error, or read as text holding a tab.
    "tabbed": ('"name" is not valid YAML', '"name" contains a tab or another control character'),
    "flow-list": '"name" must be a string, not a list or a mapping',
    "mapping": '"name" must be a string, not a list or a mapping',
    "unclosed": '"name" is not valid YAML',
}


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """The validator's run on `root`, with its output as text."""
    env = {**os.environ, "TCF_ROOT": str(root)}
    return subprocess.run(
        [str(VALIDATOR), *args], capture_output=True, text=True, env=env, check=False
    )


def errors(stderr: str) -> dict[str, list[str]]:
    """Each error line of `stderr` as {file: [message, ...]}."""
    found: dict[str, list[str]] = {}
    for line in stderr.splitlines():
        if line.startswith(ERROR):
            scope, _, message = line.removeprefix(ERROR).partition("] ")
            found.setdefault(scope, []).append(message)
    return found


def skill(directory: Path, frontmatter: str, body: str = "Body.\n") -> None:
    """Write `directory`/SKILL.md with `frontmatter` between the two `---` lines."""
    directory.mkdir(parents=True)
    _ = (directory / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")


def manifest(plugin: Path, skills: object) -> None:
    """Write the plugin's plugin.json with `skills` as its skills field."""
    (plugin / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    text = json.dumps({"name": plugin.name, "skills": skills})
    _ = (plugin / ".claude-plugin" / "plugin.json").write_text(text, encoding="utf-8")


class SkillNamesTests(unittest.TestCase):
    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name).resolve()
        (self.tmp / "plugins").mkdir()

    def test_each_name_form(self) -> None:
        skills = self.tmp / "plugins" / "forms" / "skills"
        for directory, entry in NAMES.items():
            skill(skills / directory, f"{entry}\ndescription: A skill.")
        result = run(self.tmp)
        assert result.returncode == 1, result.stderr
        found = errors(result.stderr)
        for directory in NAMES:
            scope = f"plugins/forms/skills/{directory}/SKILL.md"
            got = found.pop(scope, [])
            want = EXPECTED.get(directory)
            if want is None:
                assert got == [], (directory, got)
            else:
                assert len(got) == 1, (directory, got)
                assert got[0].startswith(want), (directory, got[0])
        assert found == {}, found

    def test_frontmatter_shape(self) -> None:
        skills = self.tmp / "plugins" / "shape" / "skills"
        skill(skills / "unnamed", "description: No name.")
        skill(skills / "twice", "name: twice\nname: twice")
        (skills / "bare").mkdir(parents=True)
        _ = (skills / "bare" / "SKILL.md").write_text("# No frontmatter\n", encoding="utf-8")
        (skills / "open").mkdir(parents=True)
        _ = (skills / "open" / "SKILL.md").write_text("---\nname: open\n", encoding="utf-8")
        found = errors(run(self.tmp).stderr)
        assert found == {
            "plugins/shape/skills/unnamed/SKILL.md": ['has no "name" field'],
            "plugins/shape/skills/twice/SKILL.md": ['"name" is defined more than once'],
            "plugins/shape/skills/bare/SKILL.md": [
                'has no frontmatter between a first line "---" and a closing "---"'
            ],
            "plugins/shape/skills/open/SKILL.md": [
                'has no frontmatter between a first line "---" and a closing "---"'
            ],
        }, found

    def test_other_fields_are_not_parsed(self) -> None:
        text = "name: lenient\ndescription: Use it: whenever, even with: colons\nmetadata:\n  a: b"
        skill(self.tmp / "plugins" / "p" / "skills" / "lenient", text)
        result = run(self.tmp)
        assert result.returncode == 0, result.stderr

    def test_manifest_paths(self) -> None:
        rooted = self.tmp / "plugins" / "rooted"
        skill(rooted, "name: rooted")
        manifest(rooted, "./")
        listed = self.tmp / "plugins" / "listed"
        skill(listed / "extra" / "inner", "name: inner")
        manifest(listed, ["./extra", "../outside", "./missing"])
        skill(self.tmp / ".claude" / "skills" / "project", "name: project")
        result = run(self.tmp)
        found = errors(result.stderr)
        assert found == {
            "plugins/listed plugin.json skills": [
                '"../outside" resolves outside the plugin',
                '"./missing" names a directory that does not exist',
            ]
        }, found

    def test_passing_repository_counts_its_skills(self) -> None:
        skill(self.tmp / "plugins" / "p" / "skills" / "one", "name: one")
        skill(self.tmp / ".claude" / "skills" / "two", "name: two")
        result = run(self.tmp)
        assert result.returncode == 0, result.stderr
        assert result.stdout == "✔ 2 skill name(s) are flat, unquoted and match their directory\n"

    def test_arguments_are_refused(self) -> None:
        result = run(self.tmp, "extra")
        assert result.returncode == 2
        assert result.stderr.splitlines()[-1].startswith("usage:"), result.stderr

    def test_repository_passes(self) -> None:
        result = run(ROOT)
        assert result.returncode == 0, result.stderr
