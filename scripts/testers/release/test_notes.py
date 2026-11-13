#!/usr/bin/env python3
"""Tests for release-notes: the tag name and the GitHub Release body."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from release.release_tools import notes
from release.release_tools.repo import changelog_section, plugin_names, remote_tags

from testers.release.helpers import Marketplace, changelog

BODY = "### Fixed\n\n- A fix."


class NotesTest(unittest.TestCase):
    """tag_name, release_body and the command line."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Build a marketplace with demo 1.2.0 and its changelog section for each test."""
        super().__init__(method_name)
        self._tmp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.m: Marketplace = Marketplace(Path(self._tmp.name))
        self.m.add_plugin("demo", "1.2.0", changelog_text=changelog("demo", {"1.2.0": BODY}))
        self.m.commit()
        self.addCleanup(self._tmp.cleanup)

    def _main(self, *args: str) -> tuple[int, str, str]:
        """Run the command line and return (exit code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = notes.main([*args, "--root", str(self.m.root)])
        return code, out.getvalue(), err.getvalue()

    def test_tag_name(self) -> None:
        """The tag is <plugin>--v<version>, as claude plugin tag names it."""
        self.assertEqual(notes.tag_name(self.m.root, "demo"), "demo--v1.2.0")

    def test_body_is_section_then_update_command(self) -> None:
        """The body is the version's section, a rule, then the update command."""
        update = "```bash\nclaude plugin update demo@the-claude-factory\n```\n"
        expected = BODY + "\n\n---\n\n**Update:**\n\n" + update
        self.assertEqual(notes.release_body(self.m.root, "demo"), expected)

    def test_cli_tag(self) -> None:
        """--tag prints only the tag."""
        self.assertEqual(self._main("demo", "--tag"), (0, "demo--v1.2.0\n", ""))

    def test_missing_section_exits_1(self) -> None:
        """A version with no changelog section never gets an empty body."""
        self.m.add_plugin("demo", "1.3.0", changelog_text=changelog("demo", {"1.2.0": BODY}))
        code, out, err = self._main("demo")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("demo", err)
        self.assertIn("1.3.0", err)

    def test_unknown_plugin_exits_2(self) -> None:
        """A plugin the marketplace doesn't list is a usage error."""
        self.assertEqual(self._main("nope")[0], 2)


class RepoReadersTest(unittest.TestCase):
    """The shared readers in release_tools.repo."""

    def test_changelog_section_stops_at_next_heading_and_links(self) -> None:
        """A section ends at the next version heading or at the link references."""
        text = changelog("demo", {"2.0.0": "new", "1.0.0": "old"})
        self.assertEqual(changelog_section(text, "2.0.0"), "new")
        self.assertEqual(changelog_section(text, "1.0.0"), "old")
        self.assertIsNone(changelog_section(text, "3.0.0"))

    def test_plugin_names_in_marketplace_order(self) -> None:
        """Names come from marketplace.json, in order."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("zeta", "0.1.0")
            m.add_plugin("alpha", "0.1.0")
            self.assertEqual(plugin_names(m.root), ["zeta", "alpha"])

    def test_remote_tags_drop_peeled_refs(self) -> None:
        """An annotated tag is listed once, not again as <tag>^{}."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.1.0")
            m.commit()
            m.push()
            m.tag("demo--v0.1.0")
            self.assertEqual(remote_tags(m.root), {"demo--v0.1.0"})


if __name__ == "__main__":
    _ = unittest.main()
