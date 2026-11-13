#!/usr/bin/env python3
"""Tests for release-status: changed, untagged, bad semver, dependents and the next version."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from release.release_tools import status
from release.release_tools.status import Row, next_version

from testers.release.helpers import Marketplace


def _rows(m: Marketplace) -> list[tuple[str, str]]:
    """Return (kind, detail) pairs for the marketplace."""
    return [(r.kind, r.detail) for r in status.status(m.root)]


def _main(m: Marketplace, *args: str) -> tuple[int, str]:
    """Run the command line and return (exit code, stdout)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = status.main([*args, "--root", str(m.root)])
    return code, out.getvalue()


class StatusTest(unittest.TestCase):
    """status() against a throwaway marketplace with an origin."""

    def test_changed_and_new(self) -> None:
        """A bumped plugin and one absent from the base are both reported as changed."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.3.2")
            m.commit()
            m.push()
            m.tag("demo--v0.3.2")
            m.add_plugin("demo", "0.4.0")
            m.add_plugin("fresh", "0.1.0")
            self.assertEqual(
                _rows(m),
                [("changed", "demo 0.3.2 -> 0.4.0"), ("changed", "fresh new -> 0.1.0")],
            )

    def test_untagged_ignores_peeled_refs(self) -> None:
        """A version on the base without its tag is untagged; a tagged one is not."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.1.0")
            m.add_plugin("other", "1.0.0")
            m.commit()
            m.push()
            m.tag("demo--v0.1.0")
            self.assertEqual(_rows(m), [("untagged", "other--v1.0.0")])

    def test_bad_semver_exits_1(self) -> None:
        """A version that is not MAJOR.MINOR.PATCH is reported and fails the run."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "1.0")
            m.commit()
            m.push()
            m.tag("demo--v1.0")
            self.assertEqual(_main(m), (1, "bad-semver: demo 1.0\n"))

    def test_dependents_listed_with_declared_range(self) -> None:
        """Dependencies from plugin.json and from the marketplace entry are listed as declared."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.3.0")
            m.add_plugin(
                "one",
                "1.0.0",
                manifest={"dependencies": ["demo", {"name": "demo", "version": "^0.3"}]},
            )
            m.add_plugin("two", "1.0.0", entry={"dependencies": ["demo@elsewhere"]})
            m.commit()
            m.push()
            for tag in ("demo--v0.3.0", "one--v1.0.0", "two--v1.0.0"):
                m.tag(tag)
            self.assertEqual(
                _rows(m),
                [
                    ("dependent", "one needs demo any"),
                    ("dependent", "one needs demo ^0.3"),
                    ("dependent", "two needs demo@elsewhere any"),
                ],
            )

    def test_clean_tree_prints_nothing(self) -> None:
        """Nothing changed and everything tagged: no output, exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.1.0")
            m.commit()
            m.push()
            m.tag("demo--v0.1.0")
            self.assertEqual(_main(m), (0, ""))

    def test_cli_next(self) -> None:
        """--next prints the next version from the base's version."""
        with tempfile.TemporaryDirectory() as tmp:
            m = Marketplace(Path(tmp))
            m.add_plugin("demo", "0.3.2")
            m.commit()
            m.push()
            self.assertEqual(_main(m, "--next", "demo", "--level", "minor"), (0, "0.4.0\n"))
            self.assertEqual(_main(m, "--next", "nope", "--level", "minor")[0], 2)

    def test_row_text(self) -> None:
        """A row prints as `<kind>: <detail>`."""
        self.assertEqual(
            str(Row("demo", "changed", "demo new -> 0.1.0")), "changed: demo new -> 0.1.0"
        )


class NextVersionTest(unittest.TestCase):
    """next_version() raises one field and resets the fields after it."""

    def test_next_version_resets_lower_fields(self) -> None:
        """Major, minor and patch from 0.3.2."""
        self.assertEqual(next_version("0.3.2", "major"), "1.0.0")
        self.assertEqual(next_version("0.3.2", "minor"), "0.4.0")
        self.assertEqual(next_version("0.3.2", "patch"), "0.3.3")

    def test_next_version_of_a_new_plugin(self) -> None:
        """A plugin absent from the base starts at 0.1.0 whatever the level."""
        self.assertEqual(next_version(None, "minor"), "0.1.0")

    def test_next_version_rejects_bad_semver(self) -> None:
        """A non-semver base version is an error, not a guess."""
        with self.assertRaises(ValueError):
            _ = next_version("1.0", "patch")


if __name__ == "__main__":
    _ = unittest.main()
