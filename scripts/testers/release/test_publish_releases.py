#!/usr/bin/env python3
"""Tests for publish-releases.sh, run in a fixture marketplace with a stub `gh` first on PATH."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from testers.release.helpers import Marketplace, changelog, git

SCRIPT = Path(__file__).resolve().parents[2] / "release" / "publish-releases.sh"

# The stub logs each call and copies the notes file it was given, so a test can read both.
STUB = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >>"${STUB_LOG}"
previous=""
for arg in "$@"; do
  if [[ ${previous} == --notes-file ]]; then cat "${arg}" >>"${STUB_NOTES}"; fi
  previous="${arg}"
done
"""

FIRST = "### Added\n\n- First."
NEW = "### Added\n\n- New."


class PublishReleasesTest(unittest.TestCase):
    """Which tags the script creates, at which commit, and when it refuses."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Build a marketplace with demo 0.1.0, committed, pushed and tagged."""
        super().__init__(method_name)
        self._tmp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.tmp: Path = Path(self._tmp.name)
        self.m: Marketplace = Marketplace(self.tmp)
        self.m.add_plugin("demo", "0.1.0", changelog_text=changelog("demo", {"0.1.0": FIRST}))
        self.m.commit()
        self.m.push()
        self.m.tag("demo--v0.1.0")
        self.addCleanup(self._tmp.cleanup)

    def _bump(self) -> str:
        """Commit and push demo 0.2.0 with both sections; return the new commit."""
        text = changelog("demo", {"0.2.0": NEW, "0.1.0": FIRST})
        self.m.add_plugin("demo", "0.2.0", changelog_text=text)
        self.m.commit()
        self.m.push()
        return git(self.m.root, "rev-parse", "HEAD").strip()

    def _run(self, **env: str) -> tuple[int, list[str], str, str]:
        """Run the script in the fixture; return (exit code, gh calls, notes, stderr)."""
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir(exist_ok=True)
        stub = bin_dir / "gh"
        _ = stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
        log, notes = self.tmp / "log.txt", self.tmp / "notes.txt"
        full = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(log),
            "STUB_NOTES": str(notes),
            **env,
        }
        bash = shutil.which("bash") or "bash"
        done = subprocess.run(
            [bash, str(SCRIPT)],
            cwd=self.m.root,
            env=full,
            capture_output=True,
            text=True,
            check=False,
        )
        calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        body = notes.read_text(encoding="utf-8") if notes.exists() else ""
        return done.returncode, calls, body, done.stderr

    def test_no_bump_releases_nothing(self) -> None:
        """Every current version already has its tag, so gh is never called."""
        code, calls, _, _ = self._run()
        self.assertEqual((code, calls), (0, []))

    def test_new_version_is_released_at_the_target(self) -> None:
        """An untagged current version gets its tag and Release at TARGET_SHA."""
        head = self._bump()
        code, calls, body, _ = self._run(TARGET_SHA=head)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(
            calls[0].startswith(f"release create demo--v0.2.0 --target {head} --title demo--v0.2.0")
        )
        self.assertTrue(body.startswith(NEW))

    def test_unknown_plugin_exits_2(self) -> None:
        """PLUGIN must be a marketplace plugin; nothing is released otherwise."""
        code, calls, _, _ = self._run(PLUGIN="nope")
        self.assertEqual((code, calls), (2, []))

    def test_backfill_tags_the_old_commit_with_current_notes(self) -> None:
        """BACKFILL_TARGET releases the version current at that commit, with today's notes."""
        old = git(self.m.root, "rev-parse", "HEAD").strip()
        _ = git(self.m.root, "push", "-q", "origin", ":refs/tags/demo--v0.1.0")
        _ = self._bump()
        code, calls, body, _ = self._run(PLUGIN="demo", BACKFILL_TARGET=old)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].startswith(f"release create demo--v0.1.0 --target {old} "))
        self.assertTrue(body.startswith(FIRST))

    def test_backfill_of_a_tagged_version_releases_nothing(self) -> None:
        """A backfill whose version already has its tag is skipped."""
        old = git(self.m.root, "rev-parse", "HEAD").strip()
        _ = self._bump()
        code, calls, _, _ = self._run(PLUGIN="demo", BACKFILL_TARGET=old)
        self.assertEqual((code, calls), (0, []))

    def test_backfill_needs_a_plugin(self) -> None:
        """BACKFILL_TARGET without PLUGIN is a usage error."""
        code, calls, _, err = self._run(BACKFILL_TARGET="HEAD")
        self.assertEqual((code, calls), (2, []))
        self.assertIn("PLUGIN", err)

    def test_a_target_outside_main_is_refused(self) -> None:
        """A dispatch on a branch never tags a commit that main doesn't have."""
        _ = git(self.m.root, "checkout", "-q", "-b", "feature")
        text = changelog("demo", {"0.2.0": NEW, "0.1.0": FIRST})
        self.m.add_plugin("demo", "0.2.0", changelog_text=text)
        self.m.commit()
        head = git(self.m.root, "rev-parse", "HEAD").strip()
        code, calls, _, err = self._run(TARGET_SHA=head)
        self.assertEqual((code, calls), (1, []))
        self.assertIn("not on main", err)

    def test_backfill_target_must_be_an_ancestor(self) -> None:
        """A commit outside the checked-out history is refused."""
        _ = git(self.m.root, "checkout", "-q", "-b", "side")
        self.m.write("plugins/demo/extra.txt", "x\n")
        self.m.commit()
        side = git(self.m.root, "rev-parse", "HEAD").strip()
        _ = git(self.m.root, "checkout", "-q", "main")
        code, calls, _, _ = self._run(PLUGIN="demo", BACKFILL_TARGET=side)
        self.assertEqual((code, calls), (1, []))


if __name__ == "__main__":
    _ = unittest.main()
