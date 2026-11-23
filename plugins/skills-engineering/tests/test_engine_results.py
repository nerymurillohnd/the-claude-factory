"""Tests for engine.results in process: where a run goes, and what removal never touches.

Each test builds its folders under a throwaway root and points TMPDIR there, so the sweep never
touches the real temp folder.
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import override
import unittest
from unittest import mock

from frontmatter_helpers import SCRIPTS

sys.path.insert(0, str(SCRIPTS))

from engine import results

DAY_AGO = time.time() - 25 * 3600


class ResolveOutTest(unittest.TestCase):
    """Which --out values get the session layout, a plain folder, or the temp folder."""

    def test_table(self) -> None:
        """Only <existing P>/checks/<id>, or a path cut at <P>/checks, is a session layout."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp).resolve()
            missing = d / "missing"
            cases: list[tuple[str | None, tuple[Path | None, Path | None]]] = [
                (None, (None, None)),
                ("results", (None, None)),
                ("/", (None, None)),
                ("/${X}/y", (None, None)),
                (f"{d}/checks/${{S}}", (d / "checks", d / "checks")),
                (f"{d}/checks/sid", (d / "checks" / "sid", d / "checks")),
                (f"{d}/out", (d / "out", None)),
                (f"{d}/out/${{S}}", (d / "out", None)),
                ("/checks/sid", (Path("/checks/sid"), None)),
                ("/checks/${S}", (Path("/checks"), None)),
                (f"{missing}/checks/sid", (missing / "checks" / "sid", None)),
                (f"{d}/checks/..", (d / "checks" / "..", None)),
            ]
            for raw, expected in cases:
                with self.subTest(raw=raw):
                    self.assertEqual(results.resolve_out(raw), expected)


class RemovalTest(unittest.TestCase):
    """remove_run, create and the sweep against symlinks, other owners and a concurrent run."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway root; setUp fills it, tearDown removes it."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.saved_tempdir: str | None = None

    @override
    def setUp(self) -> None:
        """A throwaway root whose temp-root folder is the temp folder the sweep reads."""
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        (self.tmp / "temp-root").mkdir()
        self.saved_tempdir = tempfile.tempdir
        tempfile.tempdir = str(self.tmp / "temp-root")

    @override
    def tearDown(self) -> None:
        """Restore the temp folder and remove the throwaway root."""
        tempfile.tempdir = self.saved_tempdir
        shutil.rmtree(self.tmp)

    def run_folder(self, parent: Path, name: str, *, old: bool = False) -> Path:
        """A marked run folder holding one result file."""
        path = parent / f"{results.PREFIX}{name}"
        path.mkdir(parents=True)
        _ = (path / results.MARKER).write_text("", encoding="utf-8")
        _ = (path / "summary.json").write_text("{}", encoding="utf-8")
        if old:
            os.utime(path, (DAY_AGO, DAY_AGO))
        return path

    def test_remove_run_never_follows_the_folder_symlink(self) -> None:
        """A run path swapped for a symlink to another marked run leaves the target whole."""
        target = self.run_folder(self.tmp / "victim", "target")
        link = self.tmp / f"{results.PREFIX}link"
        link.symlink_to(target, target_is_directory=True)
        results.remove_run(link)
        self.assertTrue((target / "summary.json").is_file())
        self.assertTrue((target / results.MARKER).is_file())

    def test_remove_run_keeps_a_symlink_target_inside(self) -> None:
        """A symlink inside a run goes; the file it points to stays."""
        outside = self.tmp / "outside.txt"
        _ = outside.write_text("keep", encoding="utf-8")
        run = self.run_folder(self.tmp, "with-link")
        (run / "link").symlink_to(outside)
        results.remove_run(run)
        self.assertFalse(run.exists())
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep")

    def test_remove_run_keeps_another_users_folder(self) -> None:
        """A run folder owned by another user is never emptied."""
        run = self.run_folder(self.tmp, "foreign")
        with mock.patch.object(os, "getuid", return_value=os.getuid() + 1):
            results.remove_run(run)
        self.assertTrue((run / "summary.json").is_file())

    def test_sweep_skips_another_users_folder(self) -> None:
        """The temp-folder sweep leaves an old run owned by another user."""
        run = self.run_folder(self.tmp / "temp-root", "foreign", old=True)
        with mock.patch.object(os, "getuid", return_value=os.getuid() + 1):
            results.sweep()
        self.assertTrue((run / "summary.json").is_file())

    def test_path_fallback_removes_a_run(self) -> None:
        """Without fd-based removal, as on Windows, a run still goes, marker last."""
        run = self.run_folder(self.tmp, "fallback")
        with mock.patch.object(results, "FD_REMOVAL", new=False):
            results.remove_run(run)
        self.assertFalse(run.exists())

    def test_create_refreshes_an_old_session_marker(self) -> None:
        """A new run in a session folder makes its session marker fresh."""
        session = self.tmp / "data" / "checks" / "sid"
        session.mkdir(parents=True)
        marker = session / results.SESSION_MARKER
        _ = marker.write_text("", encoding="utf-8")
        os.utime(marker, (DAY_AGO, DAY_AGO))
        _ = results.create(session, mark_session=True)
        self.assertGreater(marker.stat().st_mtime, time.time() - 3600)

    def test_sweep_restores_the_marker_when_a_run_arrives(self) -> None:
        """A run created between the emptiness check and rmdir keeps the session recognizable."""
        checks = self.tmp / "data" / "checks"
        session = checks / "old"
        session.mkdir(parents=True)
        marker = session / results.SESSION_MARKER
        _ = marker.write_text("", encoding="utf-8")
        os.utime(marker, (DAY_AGO, DAY_AGO))
        real_rmdir = Path.rmdir

        def racing_rmdir(path: Path) -> None:
            if path == session:
                _ = self.run_folder(session, "arrived")
            real_rmdir(path)

        with mock.patch.object(Path, "rmdir", new=racing_rmdir):
            results.sweep(checks)
        self.assertTrue(marker.is_file())


if __name__ == "__main__":
    _ = unittest.main()
