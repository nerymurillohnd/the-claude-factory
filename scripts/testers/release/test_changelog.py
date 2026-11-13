#!/usr/bin/env python3
"""Tests for release-changelog: dating [Unreleased] and the link references."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from release.release_tools import changelog as tool
from release.release_tools.changelog import ChangelogError, date_release

from testers.release.helpers import REPO_URL, Marketplace

FIRST = f"""# Changelog

## [Unreleased]

### Added

- Initial release.

[Unreleased]: {REPO_URL}/commits/main/plugins/demo
"""

LATER = f"""# Changelog

## [Unreleased]

### Fixed

- A fix.

## [0.1.0] - 2026-11-01

### Added

- Initial release.

[Unreleased]: {REPO_URL}/compare/demo--v0.1.0...HEAD
[0.1.0]: {REPO_URL}/releases/tag/demo--v0.1.0
"""


class DateReleaseTest(unittest.TestCase):
    """date_release() follows changelog.md steps 4 and 5."""

    def test_dates_unreleased_and_adds_empty_one(self) -> None:
        """[Unreleased] becomes the dated version and a new empty one sits above it."""
        out = date_release(FIRST, "demo", "0.1.0", "2026-11-13", REPO_URL)
        self.assertIn(
            "## [Unreleased]\n\n## [0.1.0] - 2026-11-13\n\n### Added\n\n- Initial release.\n", out
        )

    def test_links_first_release(self) -> None:
        """The first release links [Unreleased] to a compare and the version to its tag."""
        out = date_release(FIRST, "demo", "0.1.0", "2026-11-13", REPO_URL)
        self.assertTrue(
            out.endswith(
                "".join(
                    [
                        f"[Unreleased]: {REPO_URL}/compare/demo--v0.1.0...HEAD\n",
                        f"[0.1.0]: {REPO_URL}/releases/tag/demo--v0.1.0\n",
                    ]
                )
            )
        )

    def test_links_later_release(self) -> None:
        """A later release compares its tag with the previous one; older links stay."""
        out = date_release(LATER, "demo", "0.2.0", "2026-11-13", REPO_URL)
        self.assertTrue(
            out.endswith(
                "".join(
                    [
                        f"[Unreleased]: {REPO_URL}/compare/demo--v0.2.0...HEAD\n",
                        f"[0.2.0]: {REPO_URL}/compare/demo--v0.1.0...demo--v0.2.0\n",
                        f"[0.1.0]: {REPO_URL}/releases/tag/demo--v0.1.0\n",
                    ]
                )
            )
        )
        self.assertIn("## [0.2.0] - 2026-11-13\n\n### Fixed\n\n- A fix.\n\n## [0.1.0]", out)

    def test_empty_unreleased_raises(self) -> None:
        """An empty [Unreleased] is an error, as changelog.md step 4 says to stop."""
        empty = FIRST.replace("### Added\n\n- Initial release.\n\n", "")
        with self.assertRaises(ChangelogError):
            _ = date_release(empty, "demo", "0.1.0", "2026-11-13", REPO_URL)

    def test_existing_version_raises(self) -> None:
        """A version that already has its section is not dated again."""
        with self.assertRaises(ChangelogError):
            _ = date_release(LATER, "demo", "0.1.0", "2026-11-13", REPO_URL)


class CliTest(unittest.TestCase):
    """The command line writes the plugin's CHANGELOG.md, or leaves it unchanged."""

    def _run(self, text: str, *args: str) -> tuple[int, str]:
        """Write text as demo 0.1.0's changelog, run the CLI, return (exit, file text)."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.1.0", changelog_text=text)
            with contextlib.redirect_stderr(io.StringIO()):
                code = tool.main(["demo", "--root", str(m.root), *args])
            return code, (m.root / "plugins/demo/CHANGELOG.md").read_text(encoding="utf-8")

    def test_writes_with_given_date(self) -> None:
        """--date sets the date; the plugin's version comes from plugin.json."""
        code, text = self._run(FIRST, "--date", "2026-11-13")
        self.assertEqual(code, 0)
        self.assertIn("## [0.1.0] - 2026-11-13", text)

    def test_empty_unreleased_exits_1_unchanged(self) -> None:
        """An empty [Unreleased] exits 1 and leaves the file as it was."""
        empty = FIRST.replace("### Added\n\n- Initial release.\n\n", "")
        self.assertEqual(self._run(empty, "--date", "2026-11-13"), (1, empty))

    def test_bad_date_exits_2(self) -> None:
        """A date that is not YYYY-MM-DD is a usage error."""
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            _ = self._run(FIRST, "--date", "13/11/2026")
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    _ = unittest.main()
