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

# The stub stands in for gh. It logs each call, fails a call that matches STUB_FAIL, lists the
# Releases in STUB_RELEASES, prints STUB_CHECKS for the check-runs API, and copies each notes file.
# `release create` pushes the tag to the fixture's origin, as GitHub does, and adds the Release;
# with --verify-tag it requires the tag to exist already.
STUB = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >>"${STUB_LOG}"
if [[ -n ${STUB_FAIL:-} && "$*" == *"${STUB_FAIL}"* ]]; then
  echo "gh: stub failure" >&2
  exit 1
fi
case "$1 ${2:-}" in
  "release list") cat "${STUB_RELEASES}" ;;
  "api "*) printf '%s\\n' "${STUB_CHECKS:-}" ;;
  "release create")
    tag="$3" target="" verify=0 previous=""
    for arg in "$@"; do
      if [[ ${previous} == --notes-file ]]; then cat "${arg}" >>"${STUB_NOTES}"; fi
      if [[ ${previous} == --target ]]; then target="${arg}"; fi
      if [[ ${arg} == --verify-tag ]]; then verify=1; fi
      previous="${arg}"
    done
    if ((verify)); then
      git ls-remote --exit-code --tags origin "refs/tags/${tag}" >/dev/null
    else
      git push -q origin "${target}:refs/tags/${tag}"
    fi
    printf '%s\\n' "${tag}" >>"${STUB_RELEASES}"
    ;;
esac
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

    def _run(
        self, releases: tuple[str, ...] = ("demo--v0.1.0",), **env: str
    ) -> tuple[int, list[str], str, str]:
        """Run the script in the fixture; return (exit code, gh writes, notes, stderr).

        releases are the GitHub Releases that already exist. The gh calls returned leave out the
        read-only `release list` and `api` calls.
        """
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir(exist_ok=True)
        stub = bin_dir / "gh"
        _ = stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
        log, notes = self.tmp / "log.txt", self.tmp / "notes.txt"
        log.unlink(missing_ok=True)
        notes.unlink(missing_ok=True)
        listed = self.tmp / "releases.txt"
        _ = listed.write_text("".join(f"{tag}\n" for tag in releases), encoding="utf-8")
        full = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(log),
            "STUB_NOTES": str(notes),
            "STUB_RELEASES": str(listed),
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REPOSITORY": "owner/repo",
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
        writes = [c for c in calls if not c.startswith(("release list", "api "))]
        body = notes.read_text(encoding="utf-8") if notes.exists() else ""
        return done.returncode, writes, body, done.stderr

    def _remote_tag(self, tag: str) -> bool:
        """Return whether origin holds the tag."""
        found = git(self.m.root, "ls-remote", "--tags", "origin", f"refs/tags/{tag}")
        return bool(found.strip())

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

    def test_new_tag_reaches_origin(self) -> None:
        """The created tag is on origin afterwards, so a second run releases nothing."""
        head = self._bump()
        first, _, _, _ = self._run(TARGET_SHA=head)
        second, calls, _, _ = self._run(("demo--v0.1.0", "demo--v0.2.0"), TARGET_SHA=head)
        self.assertEqual((first, self._remote_tag("demo--v0.2.0")), (0, True))
        self.assertEqual((second, calls), (0, []))

    def test_tag_without_release_gets_its_release(self) -> None:
        """A tag whose Release was never created gets one, on the tag as it stands."""
        code, calls, body, _ = self._run(releases=())
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].startswith("release create demo--v0.1.0 --verify-tag "))
        self.assertTrue(body.startswith(FIRST))

    def test_a_failed_release_fails_the_run(self) -> None:
        """A gh failure stops the run with exit 1 instead of reporting the version released."""
        head = self._bump()
        code, _, _, err = self._run(TARGET_SHA=head, STUB_FAIL="release create")
        self.assertEqual(code, 1)
        self.assertIn("stub failure", err)

    def test_an_unreadable_release_list_fails_the_run(self) -> None:
        """Without the list of Releases nothing can be skipped safely, so nothing is created."""
        code, calls, _, _ = self._run(STUB_FAIL="release list")
        self.assertEqual((code, calls), (1, []))

    def test_dispatch_needs_validate_checks_passed(self) -> None:
        """A hand dispatch releases a commit only after Validate's Checks passed on it."""
        head = self._bump()
        red, red_calls, _, err = self._run(
            TARGET_SHA=head, GITHUB_EVENT_NAME="workflow_dispatch", STUB_CHECKS="failure"
        )
        green, green_calls, _, _ = self._run(
            TARGET_SHA=head, GITHUB_EVENT_NAME="workflow_dispatch", STUB_CHECKS="success"
        )
        self.assertEqual((red, red_calls), (1, []))
        self.assertIn("Checks", err)
        self.assertEqual((green, len(green_calls)), (0, 1))

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
