"""scripts/checkers/reference-pages.py: reference layout, relative links and anchors.

Each test writes a few Markdown pages under a temporary directory and runs the checker on it by
path, as `npm run check:references` does.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
from typing import override
import unittest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "scripts" / "checkers" / "reference-pages.py"
FENCE = "```"
SOURCE = "- [Source page](https://code.claude.com/docs/en/example)"
REFERENCES_ENTRY = "- [Documentation References](#documentation-references)"


def page(*body: str, contents: tuple[str, ...] | None = None, references: bool = True) -> str:
    """Return a reference page: H1, Contents (the given entries), body and References."""
    entries = [*(contents or ())]
    if references:
        entries.append(REFERENCES_ENTRY)
    lines = ["# Title", "", "## Contents", "", *entries, "", *body, ""]
    if references:
        lines += ["## Documentation References", "", SOURCE, ""]
    return "\n".join(lines)


class ReferencePagesTest(unittest.TestCase):
    """Each check on a small folder of pages."""

    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)

    def write(self, name: str, text: str) -> None:
        """Write one file under the temporary folder."""
        path = self.tmp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")

    def run_checker(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the checker by path on the temporary folder."""
        return subprocess.run(
            [str(CHECKER), *args, str(self.tmp)],
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_exit(self, code: int, *args: str) -> str:
        """Run the checker, assert its exit code and return its standard output."""
        result = self.run_checker(*args)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout

    def test_valid_page_passes(self) -> None:
        """A page with full Contents, links that resolve and References last passes."""
        self.write(
            "x.md",
            page(
                "## Setup",
                "",
                "### Install",
                "",
                "See [install](#install).",
                contents=("- [Setup](#setup)", "  - [Install](#install)"),
            ),
        )
        _ = self.assert_exit(0)

    def test_missing_contents_entry_fails(self) -> None:
        """A heading missing from Contents fails, and the report names it."""
        self.write(
            "x.md",
            page("## Setup", "", "## Usage", "", contents=("- [Setup](#setup)",)),
        )
        self.assertIn("Usage", self.assert_exit(1))

    def test_references_not_last_fails(self) -> None:
        """A ## section after Documentation References fails."""
        text = page("## Setup", "", contents=("- [Setup](#setup)",)) + "\n## Extra\n"
        self.write("x.md", text)
        _ = self.assert_exit(1)

    def test_duplicate_slug_uses_suffix(self) -> None:
        """An H2 that repeats the H1's slug is #slug-1, never #slug."""
        body = ("## Create a marketplace", "", "Go to [it](#create-a-marketplace-1).")
        for anchor, code in (("create-a-marketplace-1", 0), ("create-a-marketplace", 1)):
            text = page(*body, contents=(f"- [Create a marketplace](#{anchor})",))
            self.write("x.md", text.replace("# Title", "# Create a marketplace", 1))
            _ = self.assert_exit(code)

    def test_code_fence_ignored(self) -> None:
        """Headings and links inside a fenced code block are ignored."""
        self.write(
            "x.md",
            page(
                "## Setup",
                "",
                FENCE + "markdown",
                "## Not a heading",
                "[x](#nowhere)",
                FENCE,
                contents=("- [Setup](#setup)",),
            ),
        )
        _ = self.assert_exit(0)

    def test_percent_encoded_anchor(self) -> None:
        """A percent-encoded anchor is decoded, then matched to the slug."""
        contents = ("- [The /hooks menu](#the-hooks-menu)",)
        heading = ("## The /hooks menu", "")
        self.write("x.md", page(*heading, "[m](#the-%2Fhooks-menu)", contents=contents))
        self.assertIn("#the-%2Fhooks-menu", self.assert_exit(1))
        self.write("x.md", page(*heading, "[m](#the-hooks-menu)", contents=contents))
        _ = self.assert_exit(0)

    def test_cross_file_anchor(self) -> None:
        """A link into another folder's file checks that file's headings."""
        self.write("a/x.md", page("[m](../b/y.md#matchers)"))
        self.write("b/y.md", page("## Matchers", "", contents=("- [Matchers](#matchers)",)))
        _ = self.assert_exit(0)
        self.write("b/y.md", page("## Events", "", contents=("- [Events](#events)",)))
        self.assertIn("#matchers", self.assert_exit(1))

    def test_missing_asset_fails(self) -> None:
        """A relative link to a file that does not exist fails."""
        self.write("refs/x.md", page("![shot](../../assets/none.png)"))
        self.assertIn("none.png", self.assert_exit(1))

    def test_links_only_skips_layout(self) -> None:
        """--links-only skips Contents and References, not links."""
        self.write("x.md", "# Title\n\n## Setup\n\nSee [setup](#setup).\n")
        _ = self.assert_exit(0, "--links-only")
        _ = self.assert_exit(1)

    def test_bad_argument_exit_2(self) -> None:
        """A folder that does not exist exits 2."""
        result = subprocess.run(
            [str(CHECKER), str(self.tmp / "missing")], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
