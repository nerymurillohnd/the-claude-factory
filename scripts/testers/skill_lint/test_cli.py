#!/usr/bin/env python3
"""Tests for the skill-lint report and command line."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
from typing import cast
import unittest
from unittest import mock

from validators.skill_lint.cli import main
from validators.skill_lint.markdown_model import DocBuilder
from validators.skill_lint.model import Family, Finding, Severity
from validators.skill_lint.refs import Resolver
from validators.skill_lint.report import family_status, render_json, render_text

from testers.skill_lint.helpers import VALID_SKILL_MD, build_skill, load

WARNING_MD = VALID_SKILL_MD.replace("Say hello.", "Before March 2026, say hello.")
ERROR_MD = VALID_SKILL_MD.replace("Say hello.", "See [x](missing.md).")
EXIT_USAGE = 2


def _finding(rule: str, severity: Severity) -> Finding:
    """Return a finding for the report tests."""
    return Finding(rule, severity, "SKILL.md", 1, "m", "https://example.com")


def _main(argv: list[str]) -> tuple[int, str]:
    """Run main with stdout and stderr captured; return the code and stdout."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue()


class ReportTest(unittest.TestCase):
    """The report renderer."""

    def test_status_ordering(self) -> None:
        """An error fails; a warning warns, or fails with strict; nothing passes."""
        error = [_finding("CO-07", Severity.ERROR)]
        warning = [_finding("CO-11", Severity.WARNING)]
        self.assertEqual(family_status(error, Family.CONTENT, strict=False), "fail")
        self.assertEqual(family_status(warning, Family.CONTENT, strict=False), "warn")
        self.assertEqual(family_status(warning, Family.CONTENT, strict=True), "fail")
        self.assertEqual(family_status(warning, Family.SCRIPTS, strict=False), "pass")

    def test_table_has_command_names_and_no_ansi(self) -> None:
        """The table names each skill by command; color=False prints no escape codes."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = load(build_skill(Path(tmp), {"SKILL.md": ERROR_MD}))
            text = render_text(
                [(skill, [_finding("CO-07", Severity.ERROR)])], color=False, strict=False
            )
        self.assertIn("demo:demo-skill", text)
        self.assertIn("1 skills · 1 errors · 0 warnings", text)
        self.assertIn("  CO-07 SKILL.md:1 m", text)
        self.assertNotIn("\x1b[", text)

    def test_json_round_trip(self) -> None:
        """The JSON parses and its counts match."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = load(build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD}))
            findings = [_finding("CO-11", Severity.WARNING)]
            data = cast(
                "dict[str, list[dict[str, object]]]",
                json.loads(render_json([(skill, findings)], None, strict=False)),
            )
        self.assertEqual(len(data["skills"]), 1)
        self.assertEqual(data["findings"][0]["rule"], "CO-11")
        self.assertEqual(data["findings"][0]["severity"], "warning")


class CliTest(unittest.TestCase):
    """Exit codes and options."""

    def _skill(self, tmp: str, skill_md: str) -> str:
        """Build a skill and return its folder as a string."""
        return str(build_skill(Path(tmp), {"SKILL.md": skill_md}))

    def test_exit_0_clean(self) -> None:
        """A clean skill exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_main([self._skill(tmp, VALID_SKILL_MD)])[0], 0)

    def test_exit_1_error(self) -> None:
        """A skill with an error exits 1 and the details name the rule."""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = _main([self._skill(tmp, ERROR_MD)])
        self.assertEqual(code, 1)
        self.assertIn("CO-07", out)

    def test_exit_0_warning_only(self) -> None:
        """A skill with only warnings exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_main([self._skill(tmp, WARNING_MD)])[0], 0)

    def test_exit_1_warning_strict(self) -> None:
        """With --strict, a warning exits 1."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_main(["--strict", self._skill(tmp, WARNING_MD)])[0], 1)

    def test_exit_2_missing_path(self) -> None:
        """A path with no SKILL.md exits 2."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_main([str(Path(tmp) / "nope")])[0], EXIT_USAGE)

    def test_only_filters_families(self) -> None:
        """--only PO hides the content error, so the run exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = _main(["--only", "PO", self._skill(tmp, ERROR_MD)])
        self.assertEqual(code, 0)
        self.assertNotIn("CO-07", out)

    def test_bad_only_is_usage_error(self) -> None:
        """An unknown family is a usage error."""
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            _ = main(["--only", "XX"])
        self.assertEqual(raised.exception.code, EXIT_USAGE)

    def test_no_color_env(self) -> None:
        """With NO_COLOR set, a TTY gets no escape codes."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._skill(tmp, ERROR_MD)
            with (
                mock.patch.dict(os.environ, {"NO_COLOR": "1"}),
                mock.patch("sys.stdout.isatty", return_value=True),
            ):
                _, out = _main([folder])
        self.assertNotIn("\x1b[", out)

    def test_markdown_parsed_once_per_file(self) -> None:
        """A full run parses each Markdown file once, however many rules read it."""
        files = {
            "SKILL.md": VALID_SKILL_MD + "\nSee [a](references/a.md) and [b](references/b.md).\n",
            "references/a.md": "# A\n",
            "references/b.md": "# B\n",
        }
        original = DocBuilder.build
        with tempfile.TemporaryDirectory() as tmp:
            folder = str(build_skill(Path(tmp), files))
            with mock.patch.object(
                DocBuilder, "build", autospec=True, side_effect=original
            ) as built:
                code, _ = _main(["--manifest", folder])
        self.assertEqual(code, 0)
        self.assertEqual(built.call_count, len(files))

    def test_resolvers_do_not_grow_with_links(self) -> None:
        """The number of resolvers built does not depend on the number of links."""
        counts: list[int] = []
        original = Resolver.__init__
        for links in (1, 20):
            body = "".join(f"[r](references/r.md#r-{i})\n" for i in range(links))
            files = {"SKILL.md": VALID_SKILL_MD + body, "references/r.md": "# R\n"}
            with tempfile.TemporaryDirectory() as tmp:
                folder = str(build_skill(Path(tmp), files))
                with mock.patch.object(
                    Resolver, "__init__", autospec=True, side_effect=original
                ) as made:
                    _ = _main([folder])
                counts.append(made.call_count)
        self.assertEqual(counts[0], counts[1])

    def test_json_and_manifest(self) -> None:
        """--json --manifest prints JSON with a manifest entry for the skill."""
        with tempfile.TemporaryDirectory() as tmp:
            _, out = _main(["--json", "--manifest", self._skill(tmp, VALID_SKILL_MD)])
        data = cast("dict[str, dict[str, object]]", json.loads(out))
        self.assertIn("demo:demo-skill", data["manifest"])


if __name__ == "__main__":
    _ = unittest.main()
