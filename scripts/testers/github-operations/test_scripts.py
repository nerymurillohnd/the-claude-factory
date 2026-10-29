#!/usr/bin/env python3
"""Tests for github-operations' skill scripts, each run by its path as the skill runs it.

Run: python3 -m unittest discover -s scripts/testers/github-operations -v
Standard library only; runs on the python3 on PATH.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from typing import TYPE_CHECKING, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "plugins" / "github-operations" / "skills" / "github" / "scripts"
SHA = "0123456789abcdef0123456789abcdef01234567"
CONTAINED = "git merge-base --is-ancestor old-feature origin/main"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode

TEMPLATE = """## Summary

<!-- What changes and why. -->

## Verification

<!-- The commands you ran and what they printed. -->
"""

SUMMARY = "## Summary\n\nRejects expired holds.\n"
BODIES = {
    "valid.md": SUMMARY + "\n## Verification\n\n`npm test`: 12/12 pass.\n",
    "no-verification.md": SUMMARY,
    "comment-left.md": SUMMARY + "\n## Verification\n\n<!-- The commands you ran. -->\n",
}


def action(number: int, title: str, cls: str, fields: dict[str, str] | None = None) -> str:
    """Return one plan action block in the format check-cleanup-plan.py reads."""
    f = {"items": "none", "containment": "n/a", "force": "none", "commands": "git status"}
    f.update(fields or {})
    return (
        f"### A-{number:02d} {title}\n\n"
        f"- **Class**: {cls}\n"
        f"- **Affected items**: {f['items']}\n"
        f"- **Containment check**: {f['containment']}\n"
        f"- **Force**: {f['force']}\n"
        "- **Commands**:\n\n"
        f"```bash\n{f['commands']}\n```\n\n"
    )


BACKUP = action(1, "Backup", "prep", {"commands": 'git bundle create "<dir>/all.bundle" --all'})
DELETE_FIELDS = {
    "items": f"refs/heads/old-feature at {SHA}",
    "containment": CONTAINED,
    "commands": "git branch -d old-feature",
}
DELETE = action(2, "Delete the merged branch old-feature", "local-delete", DELETE_FIELDS)
PLANS = {
    "valid-plan.md": BACKUP + DELETE,
    "backup-second.md": action(1, "Delete old-feature", "local-delete", DELETE_FIELDS)
    + action(2, "Backup", "prep"),
    "no-containment.md": BACKUP
    + action(2, "Delete old-feature", "local-delete", {**DELETE_FIELDS, "containment": "n/a"}),
    "short-sha.md": BACKUP
    + action(
        2,
        "Delete old-feature",
        "local-delete",
        {**DELETE_FIELDS, "items": "refs/heads/old-feature at 0123abc"},
    ),
    "integrate-after-delete.md": BACKUP
    + DELETE
    + action(3, "Merge fix into main", "integrate", {"commands": "git merge --no-ff fix"}),
    "force-unapproved.md": BACKUP
    + action(2, "Publish main", "publish", {"commands": "git push --force origin main"}),
    "force-approved.md": BACKUP
    + action(
        2,
        "Publish main",
        "publish",
        {"force": "approved by name: --force", "commands": "git push --force origin main"},
    ),
    "clustered-force.md": BACKUP
    + action(2, "Publish main", "publish", {"commands": "git push -uf origin main"}),
    "clean-untracked.md": BACKUP
    + action(2, "Remove build output", "files", {"commands": "git clean -fdx"}),
    "stash-all.md": BACKUP + action(2, "Stash everything", "prep", {"commands": "git stash --all"}),
    "stash-branch.md": BACKUP
    + action(2, "Move the stash", "prep", {"commands": "git stash branch rescued stash@{0}"}),
    "tar-backup.md": action(
        1, "Backup", "prep", {"commands": 'tar -cf "<dir>/untracked-main.tar" notes.txt'}
    ),
    "empty.md": "",
}


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run one skill script by path and capture its output."""
    return subprocess.run(
        [str(SCRIPTS / script), *args], capture_output=True, text=True, check=False, timeout=30
    )


class Workspace(unittest.TestCase):
    """A temporary folder holding the inputs a test writes."""

    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name)

    def file(self, name: str, text: str) -> str:
        """Write text to a file in the workspace and return its path."""
        path = self.tmp / name
        _ = path.write_text(text, encoding="utf-8")
        return str(path)


class CheckPrBody(Workspace):
    def check(self, body: str, title: str) -> subprocess.CompletedProcess[str]:
        template = self.file("template.md", TEMPLATE)
        body_file = self.file(body, BODIES[body])
        return run(
            "check-pr-body.py", "--template", template, "--body", body_file, "--title", title
        )

    def test_valid_body_passes(self) -> None:
        r = self.check("valid.md", "fix(api): reject expired holds")
        assert r.returncode == 0, r.stderr

    def test_missing_heading_fails(self) -> None:
        r = self.check("no-verification.md", "fix(api): x")
        assert r.returncode == 1
        assert "missing heading: ## Verification" in r.stderr

    def test_unanswered_comment_fails(self) -> None:
        r = self.check("comment-left.md", "fix(api): x")
        assert r.returncode == 1
        assert "unanswered comment" in r.stderr

    def test_title_format_fails(self) -> None:
        r = self.check("valid.md", "Fixed stuff")
        assert r.returncode == 1
        assert "title does not read type(scope): summary" in r.stderr

    def test_title_over_72_fails(self) -> None:
        r = self.check("valid.md", "fix(api): " + "a" * 63)
        assert r.returncode == 1
        assert "title is 73 characters; the limit is 72" in r.stderr
        assert "does not read" not in r.stderr

    def test_breaking_change_title_passes(self) -> None:
        r = self.check("valid.md", "feat(api)!: drop the v1 endpoints")
        assert r.returncode == 0, r.stderr

    def test_missing_file_is_usage_error(self) -> None:
        none = str(self.tmp / "none.md")
        r = run("check-pr-body.py", "--template", none, "--body", none, "--title", "fix: x")
        assert r.returncode == 2


class CheckCleanupPlan(Workspace):
    def check(self, name: str) -> subprocess.CompletedProcess[str]:
        return run("check-cleanup-plan.py", self.file(name, "# Plan\n\n" + PLANS[name]))

    def test_valid_plan_passes(self) -> None:
        r = self.check("valid-plan.md")
        assert r.returncode == 0, r.stderr

    def test_backup_not_first_fails(self) -> None:
        r = self.check("backup-second.md")
        assert r.returncode == 1
        assert "A-01" in r.stderr

    def test_deletion_without_containment_fails(self) -> None:
        r = self.check("no-containment.md")
        assert r.returncode == 1
        assert "containment check" in r.stderr

    def test_short_sha_fails(self) -> None:
        r = self.check("short-sha.md")
        assert r.returncode == 1
        assert "40" in r.stderr

    def test_class_order_fails(self) -> None:
        r = self.check("integrate-after-delete.md")
        assert r.returncode == 1
        assert "order" in r.stderr

    def test_force_without_approval_fails(self) -> None:
        r = self.check("force-unapproved.md")
        assert r.returncode == 1
        assert "--force" in r.stderr

    def test_force_approved_by_name_passes(self) -> None:
        r = self.check("force-approved.md")
        assert r.returncode == 0, r.stderr

    def test_clustered_force_flag_fails(self) -> None:
        r = self.check("clustered-force.md")
        assert r.returncode == 1
        assert "command uses -f" in r.stderr

    def test_clean_untracked_fails(self) -> None:
        r = self.check("clean-untracked.md")
        assert r.returncode == 1
        assert "command uses clean -x" in r.stderr
        assert "command uses -f" in r.stderr

    def test_stash_all_fails(self) -> None:
        r = self.check("stash-all.md")
        assert r.returncode == 1
        assert "command uses stash --all" in r.stderr

    def test_stash_branch_fails(self) -> None:
        r = self.check("stash-branch.md")
        assert r.returncode == 1
        assert "command uses stash branch" in r.stderr

    def test_non_git_flags_are_not_force(self) -> None:
        r = self.check("tar-backup.md")
        assert r.returncode == 0, r.stderr

    def test_plan_without_actions_fails(self) -> None:
        r = self.check("empty.md")
        assert r.returncode == 1
        assert "no action" in r.stderr


class LifecycleState(Workspace):
    def state(
        self, command: str, *rest: str, session: str = "S1"
    ) -> subprocess.CompletedProcess[str]:
        data = str(self.tmp)
        return run("lifecycle-state.py", command, "--data-dir", data, "--session", session, *rest)

    def write(self, *pairs: str) -> subprocess.CompletedProcess[str]:
        return self.state("write", *[part for pair in pairs for part in ("--set", pair)])

    def record(self) -> JsonObject:
        value = _decode(self.state("read").stdout)
        assert isinstance(value, JsonObject)
        return value

    def test_round_trip(self) -> None:
        assert self.write("kind=pr", "pr=12", "phase=observe").returncode == 0
        record = self.record()
        assert record["phase"] == "observe"
        assert "updated" in record

    def test_write_merges_with_the_record(self) -> None:
        _ = self.write("kind=pr", "pr=12", "phase=observe")
        _ = self.write("phase=merge")
        record = self.record()
        assert (record["pr"], record["phase"]) == ("12", "merge")

    def test_unknown_key_exits_2(self) -> None:
        assert self.write("color=red").returncode == 2

    def test_read_absent_exits_1(self) -> None:
        assert self.state("read", session="none").returncode == 1

    def test_clear_removes_the_record(self) -> None:
        _ = self.write("kind=cleanup")
        assert self.state("clear").returncode == 0
        assert self.state("read").returncode == 1

    def test_session_with_a_path_exits_2(self) -> None:
        assert self.state("read", session="../x").returncode == 2


if __name__ == "__main__":
    _ = unittest.main()
