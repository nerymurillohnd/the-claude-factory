#!/usr/bin/env python3
"""Tests for the shared foundation of the frontmatter checks: reader, report and command line.

The reader cases follow what Claude Code 2.1.326 loads (a byte-order mark, CRLF and a trailing
space on a marker read normally; U+2028 stays inside a line), and the report cases follow the
output contract every check prints: one line of compact JSON, keys in a fixed order, findings
sorted, `found` cut at 120 characters, and no absolute path.
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import override
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/auditing-skills/scripts"))

from common import report, skill_file, text
from frontmatter_helpers import SCRIPTS, JsonObject, is_list, parse_json, parse_object, run_python

LINE_SEPARATOR = "\N{LINE SEPARATOR}"
ELLIPSIS = "\N{HORIZONTAL ELLIPSIS}"

DEMO_CHECK = """\
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, {scripts!r})
from common import cli, report

def check(ctx):
    return report.CheckResult(
        check="demo.check",
        status="ran",
        reason=None,
        skill=ctx.folder_name,
        findings=[
            report.Finding(
                check="demo.check",
                rule="demo",
                line=2,
                column=7,
                field="name",
                found="\\N{{LATIN SMALL LETTER E WITH ACUTE}}" + "x" * 130,
                expected="Nothing.",
                basis="official",
                surfaces=("upload", "claude-code"),
            ),
        ],
        data={{"folder_name": ctx.folder_name, "resolved": ctx.resolved_folder_name}},
    )

cli.run("demo.check", check)
"""


def finding(
    rule: str, line: int | None, column: int | None, found: str | None = "x"
) -> report.Finding:
    """A finding with fixed fields apart from its rule, position and found text."""
    return report.Finding(
        check="demo.check",
        rule=rule,
        line=line,
        column=column,
        field="name",
        found=found,
        expected="Nothing.",
        basis="official",
        surfaces=("claude-code",),
    )


def first_finding(data: JsonObject) -> JsonObject:
    """The first finding of a printed result."""
    findings = data.get("findings")
    if is_list(findings) and findings and isinstance(findings[0], JsonObject):
        return findings[0]
    msg = f"no finding in {data!r}"
    raise AssertionError(msg)


def result_of(findings: list[report.Finding]) -> report.CheckResult:
    """A result that ran, holding these findings."""
    return report.CheckResult(
        check="demo.check", status="ran", reason=None, skill="demo", findings=findings, data={}
    )


class ReaderTest(unittest.TestCase):
    """skill_file.read: the frontmatter block, the markers and the file's encoding."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folder each test builds; setUp fills it, tearDown removes it."""
        super().__init__(method_name)
        self.tmp: Path = Path()

    @override
    def setUp(self) -> None:
        """Create the throwaway folder."""
        self.tmp = Path(tempfile.mkdtemp())

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folder."""
        shutil.rmtree(self.tmp)

    def read(self, raw: bytes) -> skill_file.SkillFile:
        """Write these bytes as SKILL.md and read them back."""
        path = self.tmp / "SKILL.md"
        _ = path.write_bytes(raw)
        return skill_file.read(path)

    def block_of(self, got: skill_file.SkillFile) -> skill_file.Block:
        """The file's block, failing the test when there is none."""
        if got.block is None:
            self.fail(f"no block: {got.problem}")
        return got.block

    def test_read_valid(self) -> None:
        """A closed block: no problem, closing marker on line 3, YAML from line 2."""
        got = self.read(b"---\nname: a\n---\nbody")
        self.assertIsNone(got.problem)
        block = self.block_of(got)
        self.assertEqual(
            (block.close_line, block.yaml_text, block.first_yaml_line),
            (3, "name: a", 2),
        )

    def test_blank_first_line(self) -> None:
        """A blank line before the opening marker means there is no frontmatter."""
        self.assertEqual(self.read(b"\n---\nname: a\n---\n").problem, "no-opening-marker")

    def test_unclosed(self) -> None:
        """An opening marker with no closing one."""
        self.assertEqual(self.read(b"---\nname: a\n").problem, "unclosed")

    def test_empty_block(self) -> None:
        """Two markers with nothing between them."""
        got = self.read(b"---\n---\n")
        self.assertEqual(got.problem, "empty")

    def test_bom_crlf(self) -> None:
        """A UTF-8 byte-order mark and CRLF give the same block as clean LF."""
        got = self.read(b"\xef\xbb\xbf---\r\nname: a\r\n---\r\nbody")
        self.assertIsNone(got.problem)
        block = self.block_of(got)
        self.assertEqual((block.close_line, block.yaml_text), (3, "name: a"))
        self.assertTrue(got.had_bom)
        self.assertTrue(got.had_crlf)
        self.assertEqual(got.text, "---\nname: a\n---\nbody")

    def test_lone_cr_is_a_line_break(self) -> None:
        """A lone CR is normalized to LF too."""
        got = self.read(b"---\rname: a\r---\r")
        block = self.block_of(got)
        self.assertEqual(block.close_line, 3)

    def test_marker_trailing_space(self) -> None:
        """A trailing space or tab on either marker still reads as the marker."""
        got = self.read(b"--- \nname: a\n---\t\n")
        self.assertIsNone(got.problem)
        block = self.block_of(got)
        self.assertEqual(block.close_line, 3)

    def test_line_separator_stays_inside_the_line(self) -> None:
        """U+2028 is kept as a character, never treated as a line break."""
        got = self.read(f"---\nname: a{LINE_SEPARATOR}b\n---\n".encode())
        block = self.block_of(got)
        self.assertEqual((block.close_line, block.yaml_text), (3, f"name: a{LINE_SEPARATOR}b"))

    def test_latin1(self) -> None:
        """Bytes that aren't UTF-8 set decode_error and leave no text."""
        got = self.read(b"---\nname: \xe9\n---\n")
        self.assertIsNotNone(got.decode_error)
        self.assertIsNone(got.text)
        self.assertIsNone(got.block)

    def test_utf16(self) -> None:
        """A UTF-16 file is reported as not UTF-8, never decoded."""
        got = self.read("---\nname: a\n---\n".encode("utf-16"))
        self.assertIsNotNone(got.decode_error)
        self.assertIsNone(got.text)


class TextTest(unittest.TestCase):
    """The text helpers the checks measure and quote with."""

    def test_utf16_len(self) -> None:
        """An emoji outside the Basic Multilingual Plane counts as two UTF-16 units."""
        self.assertEqual(text.utf16_len("a\U0001f600"), 3)

    def test_snippet(self) -> None:
        """The snippet shows width characters on each side of the index, split by '|'."""
        self.assertEqual(text.snippet("abcdef", 3, 2), "bc|de")


class ReportTest(unittest.TestCase):
    """report.to_json: the output contract of every check."""

    def test_emit_order_and_truncation(self) -> None:
        """Keys come in the contract's order and found is cut at 120 characters plus an ellipsis."""
        data = parse_object(report.to_json(result_of([finding("demo", 2, 1, "x" * 200)])))
        self.assertEqual(list(data), ["check", "status", "reason", "skill", "findings", "data"])
        first = first_finding(data)
        self.assertEqual(
            list(first),
            [
                "check",
                "rule",
                "file",
                "line",
                "column",
                "field",
                "found",
                "found_length",
                "expected",
                "basis",
                "surfaces",
                "condition",
            ],
        )
        found = str(first["found"])
        self.assertEqual(len(found), 121)
        self.assertTrue(found.endswith(ELLIPSIS))
        self.assertEqual(first["found_length"], 200)

    def test_found_at_the_limit_is_kept_whole(self) -> None:
        """A found value of exactly 120 characters gets no ellipsis."""
        data = parse_object(report.to_json(result_of([finding("demo", 2, 1, "x" * 120)])))
        first = first_finding(data)
        self.assertEqual(first["found"], "x" * 120)

    def test_null_found_has_null_length(self) -> None:
        """A finding with no found value prints null for found and found_length."""
        data = parse_object(report.to_json(result_of([finding("demo", None, None, None)])))
        first = first_finding(data)
        self.assertEqual((first["found"], first["found_length"]), (None, None))

    def test_json_compact_one_line(self) -> None:
        """One line, compact separators, and non-ASCII characters written as themselves."""
        cafe = "caf\N{LATIN SMALL LETTER E WITH ACUTE}"
        out = report.to_json(result_of([finding("demo", 2, 1, cafe)]))
        self.assertNotIn("\n", out)
        self.assertNotIn('", "', out)
        self.assertNotIn('": "', out)
        self.assertIn(cafe, out)

    def test_findings_sorted(self) -> None:
        """Findings sort by line, column and rule, with unpositioned findings last."""
        given = [
            finding("b", 3, 1),
            finding("z", None, None),
            finding("a", 3, 1),
            finding("c", 2, 9),
            finding("d", 3, None),
        ]
        data = parse_object(report.to_json(result_of(given)))
        findings = data["findings"]
        items = findings if is_list(findings) else []
        order = [f["rule"] for f in items if isinstance(f, JsonObject)]
        self.assertEqual(order, ["c", "a", "b", "d", "z"])

    def test_surfaces_in_contract_order(self) -> None:
        """Surfaces print as claude-code, open-spec, upload, whatever order they were given."""
        given = report.Finding(
            check="demo.check",
            rule="demo",
            line=1,
            column=1,
            field=None,
            found=None,
            expected="Nothing.",
            basis="official",
            surfaces=("upload", "claude-code", "open-spec"),
        )
        data = parse_object(report.to_json(result_of([given])))
        first = first_finding(data)
        self.assertEqual(first["surfaces"], ["claude-code", "open-spec", "upload"])


class CommandLineTest(unittest.TestCase):
    """cli.run, through a throwaway check script that uses it."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folder each test builds; setUp fills it, tearDown removes it."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.script: Path = Path()

    @override
    def setUp(self) -> None:
        """Write the throwaway check script and one skill folder named real."""
        self.tmp = Path(tempfile.mkdtemp())
        self.script = self.tmp / "tools" / "demo_check.py"
        self.script.parent.mkdir()
        _ = self.script.write_text(DEMO_CHECK.format(scripts=str(SCRIPTS)), encoding="utf-8")
        real = self.tmp / "real"
        real.mkdir()
        _ = (real / "SKILL.md").write_text("---\nname: real\n---\n", encoding="utf-8")

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folder."""
        shutil.rmtree(self.tmp)

    def test_missing_path_exits_2(self) -> None:
        """A path that doesn't exist: exit 2, one stderr line, nothing on stdout."""
        done = run_python([str(self.script), str(self.tmp / "nope" / "SKILL.md")])
        self.assertEqual((done.returncode, done.stdout), (2, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1)

    def test_broken_symlink_exits_2(self) -> None:
        """A symlink whose target is gone counts as a missing path."""
        link = self.tmp / "broken.md"
        link.symlink_to(self.tmp / "gone.md")
        done = run_python([str(self.script), str(link)])
        self.assertEqual((done.returncode, done.stdout), (2, ""))

    def test_directory_exits_2(self) -> None:
        """A folder instead of a file: exit 2, nothing on stdout."""
        done = run_python([str(self.script), str(self.tmp / "real")])
        self.assertEqual((done.returncode, done.stdout), (2, ""))

    def test_usage_error_exits_2(self) -> None:
        """No path at all is a usage error: exit 2, one stderr line, nothing on stdout."""
        done = run_python([str(self.script)])
        self.assertEqual((done.returncode, done.stdout), (2, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)

    def test_symlinked_folder_names(self) -> None:
        """folder_name is the name as given; resolved_folder_name follows the symlink."""
        (self.tmp / "link").symlink_to(self.tmp / "real", target_is_directory=True)
        done = run_python([str(self.script), str(self.tmp / "link" / "SKILL.md")])
        self.assertEqual(done.returncode, 0, done.stderr)
        data = parse_object(done.stdout)
        self.assertEqual(data["skill"], "link")
        self.assertEqual(data["data"], {"folder_name": "link", "resolved": "real"})

    def test_deterministic(self) -> None:
        """Two runs print the same bytes, with no absolute path in them."""
        skill = str(self.tmp / "real" / "SKILL.md")
        first = run_python([str(self.script), skill])
        second = run_python([str(self.script), skill])
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertNotIn(str(self.tmp), first.stdout)
        self.assertTrue(first.stdout.endswith("}\n"))
        self.assertEqual(len(first.stdout.splitlines()), 1)

    def test_stdout_is_utf8_whatever_the_locale(self) -> None:
        """With an ASCII stdout encoding forced, the output is still UTF-8."""
        env = {**os.environ, "PYTHONIOENCODING": "ascii"}
        done = run_python([str(self.script), str(self.tmp / "real" / "SKILL.md")], env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("\N{LATIN SMALL LETTER E WITH ACUTE}", done.stdout)
        self.assertIsInstance(parse_json(done.stdout), JsonObject)


if __name__ == "__main__":
    _ = unittest.main()
