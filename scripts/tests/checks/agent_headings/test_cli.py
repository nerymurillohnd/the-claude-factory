"""Tests for the discovery and command line of agent-headings."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from scripts.checks.agent_headings.cli import main
from scripts.checks.agent_headings.discover import discover

GOOD = "---\nname: demo\ndescription: Plain\n---\n\nYou are a demo.\n\nGOAL:\nWork.\n"
BAD = "---\nname: demo\ndescription: Plain\n---\n\n## Goal\n\nWork.\n"
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

    def test_finds_agents_only(self) -> None:
        """Plugin and project agents, nested too, are found; nothing else is."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wanted = [
                "plugins/p/agents/a.md",
                "plugins/p/agents/group/b.md",
                ".claude/agents/group/c.md",
            ]
            ignored = [
                "plugins/p/skills/s/SKILL.md",
                "plugins/p/commands/c.md",
                "plugins/p/skills/s/assets/agents/x.md",
                "plugins/p/node_modules/q/agents/y.md",
                ".claude/templates/agent-template.md",
            ]
            for relative in wanted + ignored:
                _ = _write(root, relative, GOOD)
            self.assertEqual(discover(root), sorted(root / relative for relative in wanted))


class CliTest(unittest.TestCase):
    """The report and the exit code."""

    def test_clean_file_exits_zero(self) -> None:
        """No finding: exit 0 and a summary."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "agents/a.md", GOOD)
            code, out, _ = _main([str(path)])
        self.assertEqual(code, 0)
        self.assertIn("1 file checked, 0 findings", out)

    def test_finding_exits_one_with_location(self) -> None:
        """A heading: exit 1, and the report names the file, line and rule."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "agents/a.md", BAD)
            code, out, _ = _main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn(f"{path}:6: AH-01", out)

    def test_folder_argument_is_searched(self) -> None:
        """A folder outside the repository is searched with the agent globs."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ = _write(root, "plugins/p/agents/a.md", BAD)
            _ = _write(root, "plugins/p/skills/s/SKILL.md", BAD)
            code, out, _ = _main([str(root)])
        self.assertEqual(code, 1)
        self.assertIn("1 file checked, 1 finding", out)

    def test_json_report(self) -> None:
        """--json prints the count and each finding."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp), "agents/a.md", BAD)
            code, out, _ = _main(["--json", str(path)])
        self.assertEqual(code, 1)
        self.assertIn('"checked": 1', out)
        self.assertIn('"line": 6', out)
        self.assertIn('"rule": "AH-01"', out)
        self.assertIn(f'"path": "{path}"', out)

    def test_missing_path_is_a_usage_error(self) -> None:
        """A path that names nothing exits 2."""
        code, _, err = _main(["/no/such/agent.md"])
        self.assertEqual(code, EXIT_USAGE)
        self.assertIn("no such file or folder", err)


if __name__ == "__main__":
    _ = unittest.main()
