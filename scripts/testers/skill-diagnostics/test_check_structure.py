#!/usr/bin/env python3
"""Tests for skills-best-practices' check-structure.py (inventory, links, TOC, scripts, paths).

Run: python3 -m unittest discover -s scripts/testers/skill-diagnostics -p 'test_check_*.py' -v
Standard library only. Each case builds a skill folder in a temporary directory and runs the
script on it as a separate process.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, ClassVar, cast, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "plugins" / "skill-diagnostics" / "skills" / "skills-best-practices" / "scripts"
SCRIPT = SCRIPTS / "check-structure.py"
MAX_CHECKS = 200
MAX_DETAIL = 300
HEAD = "---\nname: tiny-skill\ndescription: Formats tiny reports.\n---\n# Tiny\n\n"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


@dataclass(frozen=True)
class Run:
    """One run of the script: exit code, stdout and stderr."""

    code: int
    stdout: str
    stderr: str

    def json(self) -> JsonObject:
        """The JSON object the script printed."""
        value = _decode(self.stdout)
        if not isinstance(value, JsonObject):
            msg = f"no JSON object on stdout: {self.stdout[:200]!r}"
            raise TypeError(msg)
        return value

    def objects(self, key: str) -> list[JsonObject]:
        """The objects of one list-valued key."""
        value = self.json().get(key)
        if not isinstance(value, list):
            msg = f"{key} is not a list"
            raise TypeError(msg)
        return [c for c in cast("list[object]", value) if isinstance(c, JsonObject)]

    def checks(self) -> list[JsonObject]:
        """Every check result."""
        return self.objects("checks")

    def having(self, check: str, status: str | None = None) -> list[JsonObject]:
        """The results of one check id, optionally with one status."""
        return [
            c
            for c in self.checks()
            if c.get("check") == check and (status is None or c.get("status") == status)
        ]

    def failed(self) -> list[str]:
        """'<id> <location>' of every failure."""
        return [
            f"{c.get('check')} {c.get('location')}"
            for c in self.checks()
            if c.get("status") == "fail"
        ]

    def fail_locations(self, check: str) -> list[str]:
        """Locations of one check's failures."""
        return [str(c.get("location")) for c in self.having(check, "fail")]


def run(skill: Path, *args: str) -> Run:
    """Run check-structure.py on a skill folder."""
    cmd = [sys.executable, "-I", str(SCRIPT), str(skill), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
    return Run(proc.returncode, proc.stdout, proc.stderr)


def executable(path: Path) -> None:
    """Set the executable bits."""
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def toc_file(lines: int, *, toc: bool, entries: tuple[str, ...] = ("#first",)) -> str:
    """A reference file of more than `lines` lines, with or without a table of contents."""
    parts = ["# Reference", ""]
    if toc:
        parts += ["## Contents", "", *(f"- [{e[1:]}]({e})" for e in entries), ""]
    parts += ["## First", ""]
    parts += [f"Line {i}." for i in range(lines)]
    return "\n".join(parts) + "\n"


class Base(unittest.TestCase):
    """Builds skills under a temporary root."""

    root: Path = Path()

    @override
    def setUp(self) -> None:
        """Create the temporary root."""
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.root)

    def skill(self, files: dict[str, str], name: str = "tiny-skill") -> Path:
        """Write the files into <root>/<name> and return the folder."""
        folder = self.root / name
        for rel, text in files.items():
            path = folder / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(text, encoding="utf-8")
        return folder

    def check(self, files: dict[str, str], *, exe: tuple[str, ...] = ()) -> Run:
        """Write the skill, set exec bits, run the script, expect exit 0."""
        folder = self.skill(files)
        for rel in exe:
            executable(folder / rel)
        result = run(folder)
        self.assertEqual(result.code, 0, result.stderr)
        return result


class Inventory(Base):
    """The inventory lists every file, hidden ones included, with lines and the exec bit."""

    def test_inventory_lists_hidden_files_and_exec_bit(self) -> None:
        """Hidden file, script with exec bit, binary file with lines null, sorted."""
        folder = self.skill(
            {
                "SKILL.md": HEAD + "Run `python3 ${CLAUDE_SKILL_DIR}/scripts/run.py`.\n",
                ".hidden": "secret\n",
                "scripts/run.py": "#!/usr/bin/env python3\nprint(1)\n",
            }
        )
        _ = (folder / "assets").mkdir()
        _ = (folder / "assets" / "logo.bin").write_bytes(b"\x00\x01\x02")
        executable(folder / "scripts" / "run.py")
        result = run(folder)
        inventory = result.objects("inventory")
        paths = [str(e.get("path")) for e in inventory]
        self.assertEqual(paths, sorted(paths))
        self.assertIn(".hidden", paths)
        by_path = {str(e.get("path")): e for e in inventory}
        self.assertEqual(by_path["scripts/run.py"].get("executable"), True)
        self.assertEqual(by_path["scripts/run.py"].get("lines"), 2)
        self.assertEqual(by_path[".hidden"].get("executable"), False)
        self.assertIsNone(by_path["assets/logo.bin"].get("lines"))
        self.assertEqual(result.json().get("script"), "check-structure")


class Links(Base):
    """BS-11: links and pointers resolve, relative to the file that holds them."""

    def test_valid_skill_has_no_failure(self) -> None:
        """A skill whose links all resolve and whose files are all used passes."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [the guide](references/guide.md) when formatting.\n",
                "references/guide.md": "# Guide\n\n## Rules\n\nSee [Rules](#rules).\n",
            }
        )
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("S-2", "pass"))

    def test_broken_link(self) -> None:
        """A link to a missing file fails S-2 at its line."""
        result = self.check({"SKILL.md": HEAD + "Read [x](references/missing.md).\n"})
        self.assertEqual(result.fail_locations("S-2"), ["SKILL.md:7"])

    def test_sibling_link_resolves_from_its_own_file(self) -> None:
        """references/a.md linking evaluation.md means references/evaluation.md."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [a](references/a.md) and [e](references/evaluation.md).\n",
                "references/a.md": "# A\n\nSee [evaluation.md](evaluation.md#scores).\n",
                "references/evaluation.md": "# Evaluation\n\n## Scores\n",
            }
        )
        self.assertEqual(result.failed(), [])

    def test_sibling_link_is_not_resolved_from_the_skill_root(self) -> None:
        """A link in references/a.md to guide.md that exists only at the root is broken."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [a](references/a.md) and [g](guide.md).\n",
                "references/a.md": "# A\n\nSee [guide](guide.md).\n",
                "guide.md": "# Guide\n",
            }
        )
        self.assertEqual(result.fail_locations("S-2"), ["references/a.md:3"])

    def test_links_in_code_are_ignored(self) -> None:
        """Example links in fenced blocks and inline code are not checked."""
        body = (
            "Write links like `[FORMS.md](FORMS.md)`.\n\n"
            "```markdown\n[criteria](references/criteria.md)\n```\n\n"
            "~~~\n[x](nowhere.md)\n~~~\n"
        )
        result = self.check({"SKILL.md": HEAD + body})
        self.assertFalse(result.having("S-2", "fail"))

    def test_missing_anchor(self) -> None:
        """A link to a heading that doesn't exist fails S-3."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [g](references/guide.md#nope).\n",
                "references/guide.md": "# Guide\n\n## Rules\n",
            }
        )
        self.assertEqual(result.fail_locations("S-3"), ["SKILL.md:7"])

    def test_github_anchor_rules(self) -> None:
        """Backticks and punctuation are dropped, spaces become -, duplicates get -1."""
        guide = (
            "# Guide\n\n## The `foo` bar\n\n## What's new?\n\n## Setup\n\n## Setup\n\n"
            "## snake_case and-dash\n"
        )
        links = "".join(
            f"[x](references/guide.md#{a})\n"
            for a in ("the-foo-bar", "whats-new", "setup", "setup-1", "snake_case-and-dash")
        )
        result = self.check({"SKILL.md": HEAD + links, "references/guide.md": guide})
        self.assertEqual(result.failed(), [])

    def test_headings_in_code_are_not_anchors(self) -> None:
        """A '## Heading' line inside a fence is no heading."""
        result = self.check(
            {
                "SKILL.md": HEAD + "[g](references/guide.md#fake)\n",
                "references/guide.md": "# Guide\n\n```\n## Fake\n```\n",
            }
        )
        self.assertTrue(result.having("S-3", "fail"))

    def test_pointer_in_text_to_missing_heading(self) -> None:
        """A bare `file.md#anchor` pointer in a reference whose heading is missing fails S-3."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [l](references/lens.md) and [a](references/area.md).\n",
                "references/lens.md": (
                    "# Lens\n\n- Rule: `area.md#missing-rule`\n- Ok: area.md#rule\n"
                ),
                "references/area.md": "# Area\n\n## Rule\n",
            }
        )
        self.assertEqual(result.fail_locations("S-3"), ["references/lens.md:3"])


class Depth(Base):
    """BS-1: every file is linked from SKILL.md, one level deep."""

    def test_file_linked_only_from_a_reference(self) -> None:
        """b.md is linked from a.md but not from SKILL.md: S-4 fails."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [a](references/a.md).\n",
                "references/a.md": "# A\n\nThen read [b](b.md).\n",
                "references/b.md": "# B\n",
            }
        )
        self.assertEqual(result.fail_locations("S-4"), ["references/a.md:3"])


class Unused(Base):
    """BS-11: no unused file; evals/ is exempt; a path mention in code counts as use."""

    def test_unused_file(self) -> None:
        """A file nothing mentions fails S-5."""
        result = self.check({"SKILL.md": HEAD + "Nothing.\n", "assets/unused.txt": "x\n"})
        self.assertEqual(result.fail_locations("S-5"), ["assets/unused.txt:1"])

    def test_evals_are_exempt(self) -> None:
        """Files under evals/ are never unused."""
        result = self.check({"SKILL.md": HEAD + "Nothing.\n", "evals/evals.json": "{}\n"})
        self.assertFalse(result.having("S-5", "fail"))

    def test_mention_in_code_counts_as_use(self) -> None:
        """A script named only in a fenced command is used, and so is what it names."""
        result = self.check(
            {
                "SKILL.md": HEAD + "```bash\npython3 ${CLAUDE_SKILL_DIR}/scripts/run.py\n```\n",
                "scripts/run.py": "#!/usr/bin/env python3\nDATA = 'assets/data.json'\n",
                "assets/data.json": "{}\n",
            },
            exe=("scripts/run.py",),
        )
        self.assertEqual(result.failed(), [])

    def test_file_mentioned_only_by_an_unused_file_is_unused(self) -> None:
        """Use flows from SKILL.md; an orphan's mentions don't count."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Nothing.\n",
                "assets/orphan.md": "See data.json\n",
                "assets/data.json": "{}\n",
            }
        )
        self.assertEqual(
            sorted(result.fail_locations("S-5")), ["assets/data.json:1", "assets/orphan.md:1"]
        )


class TableOfContents(Base):
    """BS-9: reference files over 100 lines open with a TOC whose entries match headings."""

    def test_long_reference_without_toc(self) -> None:
        """Over 100 lines and no Contents heading fails S-6."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [r](references/long.md).\n",
                "references/long.md": toc_file(110, toc=False),
            }
        )
        self.assertEqual(result.fail_locations("S-6"), ["references/long.md:1"])

    def test_long_reference_with_toc(self) -> None:
        """Over 100 lines with a matching Contents list passes S-6 and S-7."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [r](references/long.md).\n",
                "references/long.md": toc_file(110, toc=True),
            }
        )
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("S-6", "pass"))

    def test_toc_entry_without_heading(self) -> None:
        """A TOC entry whose heading doesn't exist fails S-7."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [r](references/long.md).\n",
                "references/long.md": toc_file(110, toc=True, entries=("#first", "#second")),
            }
        )
        self.assertEqual(result.fail_locations("S-7"), ["references/long.md:6"])


class Paths(Base):
    """BS-9 backslashes, BS-3 the skill-dir variable in links, SU-2 paths outside the skill."""

    def test_backslash_in_link(self) -> None:
        """A link target with a backslash fails S-8."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [g](references\\guide.md).\n",
                "references/guide.md": "# G\n",
            }
        )
        self.assertTrue(result.having("S-8", "fail"))

    def test_backslash_in_script_path(self) -> None:
        """A script path with a backslash fails S-8."""
        result = self.check({"SKILL.md": HEAD + "Run `python3 scripts\\run.py`.\n"})
        self.assertTrue(result.having("S-8", "fail"))

    def test_skill_dir_in_link(self) -> None:
        """${CLAUDE_SKILL_DIR} inside a link target fails S-9."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [g](${CLAUDE_SKILL_DIR}/references/guide.md).\n",
                "references/guide.md": "# G\n",
            }
        )
        self.assertEqual(result.fail_locations("S-9"), ["SKILL.md:7"])

    def test_link_leaving_the_skill(self) -> None:
        """A link that climbs out of the skill folder fails S-12."""
        _ = self.skill({"shared.md": "# Shared\n"}, name="other")
        result = self.check({"SKILL.md": HEAD + "Read [s](../other/shared.md).\n"})
        self.assertEqual(result.fail_locations("S-12"), ["SKILL.md:7"])

    def test_plugin_root_path_outside_the_skill(self) -> None:
        """${CLAUDE_PLUGIN_ROOT}/agents/... leaves the skill folder."""
        result = self.check(
            {"SKILL.md": HEAD + "Read `${CLAUDE_PLUGIN_ROOT}/agents/x.md` for agents.\n"}
        )
        self.assertTrue(result.having("S-12", "fail"))

    def test_plugin_root_path_inside_the_skill(self) -> None:
        """${CLAUDE_PLUGIN_ROOT}/skills/<this skill>/... stays in the skill folder."""
        plugin = self.root / "plug"
        folder = plugin / "skills" / "tiny-skill"
        (plugin / ".claude-plugin").mkdir(parents=True)
        _ = (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "plug"}\n')
        folder.mkdir(parents=True)
        _ = (folder / "SKILL.md").write_text(
            HEAD + "Agents read `${CLAUDE_PLUGIN_ROOT}/skills/tiny-skill/SKILL.md`.\n"
        )
        result = run(folder)
        self.assertFalse(result.having("S-12", "fail"))


class ExamplesInReferences(Base):
    """Paths in a reference's examples are documentation, not files the skill reads or runs."""

    def test_reference_examples_are_not_paths(self) -> None:
        """A plugin-root path and a backslash path shown in a reference don't fail S-8 or S-12."""
        reference = (
            "# R\n\n- Avoid: `scripts\\helper.py`\n\n"
            '```json\n{"command": "${CLAUDE_PLUGIN_ROOT}/server.js"}\n```\n\n'
            "Use `../shared/x.md` in your own plugin.\n"
        )
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [r](references/r.md).\n",
                "references/r.md": reference,
                "assets/example.json": '{"command": "${CLAUDE_PLUGIN_ROOT}/server.js"}\n',
            }
        )
        self.assertFalse(result.having("S-8", "fail"))
        self.assertFalse(result.having("S-12", "fail"))

    def test_script_reading_outside_the_skill(self) -> None:
        """A script that opens a plugin-root path outside the skill fails S-12."""
        result = self.check(
            {
                "SKILL.md": HEAD + "Run `bash ${CLAUDE_SKILL_DIR}/scripts/run.sh`.\n",
                "scripts/run.sh": '#!/usr/bin/env bash\ncat "${CLAUDE_PLUGIN_ROOT}/agents/x.md"\n',
            },
            exe=("scripts/run.sh",),
        )
        self.assertEqual(result.fail_locations("S-12"), ["scripts/run.sh:2"])

    def test_link_in_reference_leaving_the_skill(self) -> None:
        """A link in a reference that climbs out of the skill still fails S-12."""
        _ = self.skill({"shared.md": "# Shared\n"}, name="other")
        result = self.check(
            {
                "SKILL.md": HEAD + "Read [r](references/r.md).\n",
                "references/r.md": "# R\n\nSee [s](../../other/shared.md).\n",
            }
        )
        self.assertEqual(result.fail_locations("S-12"), ["references/r.md:3"])


class Scripts(Base):
    """SC-9: every script has a #!/usr/bin/env line and the executable bit."""

    FILES: ClassVar[dict[str, str]] = {
        "SKILL.md": HEAD + "Run `python3 ${CLAUDE_SKILL_DIR}/scripts/run.py`.\n",
    }

    def test_script_without_shebang(self) -> None:
        """No shebang fails S-10."""
        files = {**self.FILES, "scripts/run.py": "print(1)\n"}
        result = self.check(files, exe=("scripts/run.py",))
        self.assertEqual(result.fail_locations("S-10"), ["scripts/run.py:1"])

    def test_script_with_absolute_interpreter(self) -> None:
        """#!/usr/bin/python3 is not the env form."""
        files = {**self.FILES, "scripts/run.py": "#!/usr/bin/python3\nprint(1)\n"}
        result = self.check(files, exe=("scripts/run.py",))
        self.assertTrue(result.having("S-10", "fail"))

    def test_script_without_exec_bit(self) -> None:
        """No executable bit fails S-11."""
        files = {**self.FILES, "scripts/run.py": "#!/usr/bin/env python3\nprint(1)\n"}
        result = self.check(files)
        self.assertEqual(result.fail_locations("S-11"), ["scripts/run.py:1"])

    def test_good_script(self) -> None:
        """Shebang and exec bit pass."""
        files = {**self.FILES, "scripts/run.py": "#!/usr/bin/env python3\nprint(1)\n"}
        result = self.check(files, exe=("scripts/run.py",))
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("S-10", "pass"))
        self.assertTrue(result.having("S-11", "pass"))


class Contract(Base):
    """Exit codes, help, bounded output and the result shape."""

    def test_findings_exit_zero(self) -> None:
        """A skill with failures still exits 0 and prints one JSON object."""
        result = self.check({"SKILL.md": HEAD + "[x](missing.md)\n", "junk.txt": "x\n"})
        self.assertTrue(result.failed())
        for check in result.checks():
            self.assertIn(check.get("kind"), ("proved", "lead"))
            self.assertLessEqual(len(str(check.get("detail"))), MAX_DETAIL)

    def test_usage_exit_2(self) -> None:
        """No such folder, or no SKILL.md, is a usage error."""
        self.assertEqual(run(self.root / "nope").code, 2)
        empty = self.root / "empty"
        empty.mkdir()
        result = run(empty)
        self.assertEqual(result.code, 2)
        self.assertIn("SKILL.md", result.stderr)

    def test_binary_skill_md_exits_1(self) -> None:
        """A SKILL.md that isn't text can't be checked: exit 1 with a message, no traceback."""
        folder = self.root / "binary"
        folder.mkdir()
        _ = (folder / "SKILL.md").write_bytes(b"---\nname: binary\n---\n\0\n")
        result = run(folder)
        self.assertEqual(result.code, 1)
        self.assertIn("SKILL.md is not readable", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_help(self) -> None:
        """--help exits 0."""
        result = run(self.root, "--help")
        self.assertEqual(result.code, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_output_is_bounded(self) -> None:
        """250 broken links: at most 200 checks, the rest counted in truncated."""
        links = "".join(f"[x](missing{i}.md)\n" for i in range(250))
        result = self.check({"SKILL.md": HEAD + links})
        self.assertLessEqual(len(result.checks()), MAX_CHECKS)
        truncated = result.json().get("truncated")
        self.assertIsInstance(truncated, int)
        self.assertGreater(truncated if isinstance(truncated, int) else 0, 0)

    def test_output_file_matches_stdout(self) -> None:
        """--output writes the same JSON object as stdout, creating parent folders."""
        folder = self.skill({"SKILL.md": HEAD})
        out = self.root / "results" / "nested" / "structure.json"
        result = run(folder, "--output", str(out))
        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(out.read_text(encoding="utf-8"), result.stdout)
        self.assertEqual(result.json().get("script"), "check-structure")

    def test_unwritable_output_exits_1(self) -> None:
        """An --output path that can't be written exits 1 and names the path on stderr."""
        folder = self.skill({"SKILL.md": HEAD})
        blocker = self.root / "a-file"
        _ = blocker.write_text("x", encoding="utf-8")
        out = blocker / "structure.json"
        result = run(folder, "--output", str(out))
        self.assertEqual(result.code, 1)
        self.assertIn("--output", result.stderr)
        self.assertIn(str(out), result.stderr)

    def test_proved_checks_only_on_owned_items(self) -> None:
        """check-structure proves only BS-1, BS-3, BS-9, BS-11, SC-9 and SU-2."""
        result = self.check({"SKILL.md": HEAD + "[x](missing.md)\n", "junk.txt": "x\n"})
        owned = ("BS-1", "BS-3", "BS-9", "BS-11", "SC-9", "SU-2")
        for check in result.checks():
            if check.get("kind") == "proved":
                self.assertIn(check.get("item"), owned)

    def test_environment_is_not_needed(self) -> None:
        """The script reads no environment variable to run."""
        env = {"PATH": os.environ.get("PATH", "")}
        folder = self.skill({"SKILL.md": HEAD})
        proc = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(folder)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    _ = unittest.main()
