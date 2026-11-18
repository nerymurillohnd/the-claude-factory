#!/usr/bin/env python3
"""Tests for the restructuring-documents skill's verification script."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "restructuring-documents"
    / "scripts"
    / "restructure.py"
)
SOURCE = (
    "# Guide\n\nIntro line.\n\n"
    "## Alpha\n\nAlpha rule one.\nAlpha rule two.\n\n"
    "## Beta\n\nBeta rule.\n"
)
ALPHA = "# Alpha\n\n## Alpha\n\nAlpha rule one.\nAlpha rule two.\n"
BETA = "# Beta\n\nIntro line.\n\n## Beta\n\nBeta rule.\n"
TITLE = "struct\tguide.md\t1\t2\t-\ttitle of the old file; each new file has its own"
INTRO = "move\tguide.md\t3\t4\tbeta.md\t"
ALPHA_ROWS = "move\tguide.md\t5\t9\talpha.md\t"
BETA_ROWS = "move\tguide.md\t10\t12\tbeta.md\t"
GOOD_ROWS = (TITLE, INTRO, ALPHA_ROWS, BETA_ROWS)


def run(*args: str) -> tuple[int, str]:
    """Run the script with arguments; return its exit code and combined output."""
    done = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )
    return done.returncode, done.stdout + done.stderr


class Workspace:
    """A baseline folder, a current folder and a ledger, in a temporary directory."""

    def __init__(self, root: Path) -> None:
        """Create the two folders, the source in the baseline and its split in current."""
        self.base: Path = root / "base"
        self.cur: Path = root / "cur"
        self.ledger: Path = root / "ledger.tsv"
        for folder in (self.base, self.cur):
            folder.mkdir()
        _ = (self.base / "guide.md").write_text(SOURCE, encoding="utf-8")
        self.write("alpha.md", ALPHA)
        self.write("beta.md", BETA)
        self.rows(*GOOD_ROWS)

    def write(self, name: str, text: str) -> None:
        """Write a file into the current folder."""
        _ = (self.cur / name).write_text(text, encoding="utf-8")

    def rows(self, *rows: str) -> None:
        """Write the ledger rows."""
        _ = self.ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def check(self, command: str) -> tuple[int, str]:
        """Run a command with the arguments it takes in this workspace."""
        base, cur, ledger = str(self.base), str(self.cur), str(self.ledger)
        args = {
            "ledger": (base, ledger),
            "moved": (base, cur, ledger),
            "splits": (cur, ledger),
            "inventory": (base, cur, ledger),
            "mentions": (cur,),
            "blocks": (cur,),
        }[command]
        return run(command, *args)


@contextmanager
def workspace() -> Generator[Workspace, None, None]:
    """Yield a workspace where guide.md was split into alpha.md and beta.md."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Workspace(Path(tmp))


class RestructureTests(unittest.TestCase):
    """Each command catches the loss it exists for, and passes a clean split."""

    def test_clean_split_passes_every_check(self) -> None:
        """A split that keeps every line passes ledger, moved and inventory."""
        with workspace() as ws:
            for command in ("ledger", "moved", "inventory"):
                self.assertEqual(ws.check(command)[0], 0, command)

    def test_ledger_reports_an_unmapped_line(self) -> None:
        """A source line no row covers is reported by its number."""
        with workspace() as ws:
            ws.rows(TITLE, INTRO, ALPHA_ROWS)
            code, output = ws.check("ledger")
            self.assertEqual(code, 1)
            self.assertIn("unmapped [10, 11, 12]", output)

    def test_moved_reports_a_line_missing_from_its_destination(self) -> None:
        """A moved line that never reached its destination is a finding."""
        with workspace() as ws:
            ws.write("alpha.md", ALPHA.replace("Alpha rule two.\n", ""))
            code, output = ws.check("moved")
            self.assertEqual(code, 1)
            self.assertIn("MISSING guide.md:8 -> alpha.md: Alpha rule two", output)

    def test_struct_row_without_a_justification_is_rejected(self) -> None:
        """A struct row must say why its lines hold no content."""
        with workspace() as ws:
            ws.rows("struct\tguide.md\t1\t2\t-\t", INTRO, ALPHA_ROWS, BETA_ROWS)
            code, output = ws.check("ledger")
            self.assertEqual(code, 2)
            self.assertIn("needs a justifying note", output)

    def test_a_dropped_line_must_be_gone_everywhere(self) -> None:
        """A dropped line still present in any file is a finding."""
        with workspace() as ws:
            ws.rows(
                TITLE,
                INTRO,
                "move\tguide.md\t5\t7\talpha.md\t",
                "drop\tguide.md\t8\t8\t-\tsame fact as Alpha rule one",
                "move\tguide.md\t9\t9\talpha.md\t",
                BETA_ROWS,
            )
            code, output = ws.check("moved")
            self.assertEqual(code, 1)
            self.assertIn("DROPPED LINE STILL PRESENT guide.md:8", output)

    def test_split_parts_must_join_and_exist(self) -> None:
        """A split row's parts rebuild the original, and each kept part must exist."""
        with workspace() as ws:
            ws.write("beta.md", BETA.replace("Intro line.\n", "Intro\n"))
            split = "split\tguide.md\t3\t3\t-\tstruct|Intro ||| beta.md|line."
            ws.rows(TITLE, split, "move\tguide.md\t4\t4\tbeta.md\t", ALPHA_ROWS, BETA_ROWS)
            self.assertEqual(ws.check("ledger")[0], 0)
            code, output = ws.check("splits")
            self.assertEqual(code, 1)
            self.assertIn("MISSING guide.md:3 -> beta.md: line.", output)

    def test_inventory_allows_only_what_the_ledger_justifies(self) -> None:
        """Without the ledger the old title is missing; with it, nothing is."""
        with workspace() as ws:
            code, output = run("inventory", str(ws.base), str(ws.cur))
            self.assertEqual(code, 1)
            self.assertIn("guide.md:1: # Guide", output)
            self.assertEqual(ws.check("inventory")[0], 0)

    def test_mentions_flags_a_stale_file_name(self) -> None:
        """A file name that no longer exists is reported; a code-fenced one is not."""
        with workspace() as ws:
            ws.write("alpha.md", ALPHA + "\nSee guide.md for more.\n\n```text\nold.md\n```\n")
            code, output = ws.check("mentions")
            self.assertEqual(code, 1)
            self.assertIn("UNRESOLVED alpha.md:8: guide.md", output)
            self.assertNotIn("old.md", output)

    def test_blocks_ignore_headings_inside_code_fences(self) -> None:
        """A heading inside fenced code opens no section, and coverage holds."""
        with workspace() as ws:
            ws.write("alpha.md", ALPHA + "\n````markdown\n## Not a section\n````\n")
            code, output = ws.check("blocks")
            self.assertEqual(code, 0)
            self.assertNotIn("Not a section", output)

    def test_a_file_edited_in_place_needs_no_coverage(self) -> None:
        """A source with only edit rows is checked for its ranges, not for full coverage."""
        with workspace() as ws:
            _ = (ws.base / "notes.md").write_text("a\nb\nc\n", encoding="utf-8")
            ws.rows(*GOOD_ROWS, "edit\tnotes.md\t2\t2\t-\treworded on purpose")
            code, output = ws.check("ledger")
            self.assertEqual(code, 0)
            self.assertIn("notes.md: edited in place", output)

    def test_mentions_accepts_names_declared_outside_the_set(self) -> None:
        """A conventional file name passed to --allow is not reported."""
        with workspace() as ws:
            ws.write("alpha.md", ALPHA + "\nFollow CLAUDE.md here.\n")
            self.assertEqual(ws.check("mentions")[0], 1)
            code, _ = run("mentions", str(ws.cur), "--allow", r"CLAUDE\.md")
            self.assertEqual(code, 0)


if __name__ == "__main__":
    _ = unittest.main()
