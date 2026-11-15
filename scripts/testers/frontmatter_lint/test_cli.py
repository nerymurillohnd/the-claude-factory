#!/usr/bin/env python3
"""Tests for the discovery and command line of frontmatter-lint."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
from typing import cast
import unittest
from unittest import mock

from validators.frontmatter_lint.cli import main
from validators.frontmatter_lint.discover import discover

GOOD = "---\nname: demo\ndescription: Plain text\n---\nbody\n"
BAD = '---\nname: demo\ndescription: "Quoted"\n---\nbody\n'
EXIT_USAGE = 2


def _write(root: Path, relative: str, text: str) -> Path:
    """Write a file under root, creating its folders."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")
    return path


def _main(argv: list[str]) -> tuple[int, str, str]:
    """Run main with stdout and stderr captured."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class DiscoverTest(unittest.TestCase):
    """Which files are checked."""

    def test_finds_skills_agents_and_commands_only(self) -> None:
        """Skills, agents (nested too) and commands in plugins/ and .claude/ are found."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wanted = [
                "plugins/p/skills/s/SKILL.md",
                "plugins/p/agents/a.md",
                "plugins/p/agents/group/b.md",
                "plugins/p/commands/c.md",
                ".claude/skills/s/SKILL.md",
                ".claude/agents/group/d.md",
                ".claude/commands/e.md",
            ]
            ignored = [
                "plugins/p/skills/s/references/r.md",
                "plugins/p/skills/s/assets/agents/x.md",
                "plugins/p/evals/case/agents/y.md",
                "plugins/p/README.md",
                ".claude/templates/agent-template.md",
                "plugins/p/node_modules/q/agents/z.md",
            ]
            for relative in wanted + ignored:
                _ = _write(root, relative, GOOD)
            found = sorted(path.relative_to(root).as_posix() for path in discover(root))
            self.assertEqual(found, sorted(wanted))


class CliTest(unittest.TestCase):
    """Output and exit codes."""

    def test_clean_files_exit_zero(self) -> None:
        """No finding exits 0 and says how many files were checked."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "plugins/p/agents/a.md", GOOD)
            code, out, _ = _main([str(path)])
            self.assertEqual(code, 0)
            self.assertIn("1 file checked, 0 findings", out)

    def test_finding_exits_one_with_location(self) -> None:
        """A finding exits 1 and prints path:line: rule."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "plugins/p/agents/a.md", BAD)
            code, out, _ = _main([str(path)])
            self.assertEqual(code, 1)
            self.assertIn(f"{path}:3: FM-03", out)

    def test_json_output(self) -> None:
        """--json prints one object with every finding."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "plugins/p/agents/a.md", BAD)
            code, out, _ = _main(["--json", str(path)])
            self.assertEqual(code, 1)
            report = cast("dict[str, object]", json.loads(out))
            findings = cast("list[dict[str, object]]", report["findings"])
            self.assertEqual(report["checked"], 1)
            self.assertEqual(findings[0]["rule"], "FM-03")
            self.assertEqual(findings[0]["line"], 3)

    def test_folder_argument_is_discovered(self) -> None:
        """A folder argument is searched with the same globs as the repository root."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ = _write(root, "plugins/p/agents/a.md", BAD)
            _ = _write(root, "plugins/p/README.md", BAD)
            code, out, _ = _main([str(root)])
            self.assertEqual(code, 1)
            self.assertIn("1 file checked, 1 finding", out)

    def test_subfolder_of_the_repository_is_checked(self) -> None:
        """A folder inside the repository gets the repository's files under it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ = _write(root, "plugins/p/agents/group/a.md", BAD)
            _ = _write(root, "plugins/p/skills/s/references/r.md", BAD)
            _ = _write(root, "plugins/q/agents/b.md", BAD)
            with mock.patch("validators.frontmatter_lint.cli.ROOT", root):
                code, out, _ = _main([str(root / "plugins" / "p")])
            self.assertEqual(code, 1)
            self.assertIn("1 file checked, 1 finding", out)

    def test_missing_path_is_usage_error(self) -> None:
        """A path that doesn't exist exits 2."""
        code, _, err = _main(["/nonexistent/frontmatter-lint"])
        self.assertEqual(code, EXIT_USAGE)
        self.assertIn("frontmatter-lint:", err)


if __name__ == "__main__":
    _ = unittest.main()
