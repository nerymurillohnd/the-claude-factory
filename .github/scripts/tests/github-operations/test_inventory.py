"""Tests for the git-cleanup skill's scripts/inventory.py against a throwaway repository.

Run: python3 -m unittest discover -s .github/scripts/tests/github-operations -v
Needs git 2.38+ on PATH. Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable
REPO = Path(__file__).resolve().parents[4]
INVENTORY = (
    REPO / "plugins" / "github-operations" / "skills" / "git-cleanup" / "scripts" / "inventory.py"
)
MARKER = "fixture-value-42"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def obj(value: object) -> JsonObject:
    """Return value as a JSON object, failing the test when it is not one."""
    assert isinstance(value, JsonObject), value
    return value


def items(value: object) -> list[object]:
    """Return value as a JSON array, failing the test when it is not one."""
    assert isinstance(value, list), value
    return value


class Fixture:
    """A repository with an origin and the clutter the audit must find."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.env = {
            **os.environ,
            "HOME": str(base / "home"),
            "GIT_CONFIG_GLOBAL": str(base / "gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Ada",
            "GIT_AUTHOR_EMAIL": "ada@example.com",
            "GIT_COMMITTER_NAME": "Ada",
            "GIT_COMMITTER_EMAIL": "ada@example.com",
        }
        (base / "home").mkdir()
        self.origin = base / "origin.git"
        self.work = base / "work"

    def git(self, *args: str, cwd: Path | None = None) -> str:
        """Run git in the working repository (or cwd) and return stdout."""
        done = subprocess.run(
            [shutil.which("git") or "git", *args],
            cwd=cwd or self.work,
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        return done.stdout

    def commit(self, name: str, text: str, message: str) -> None:
        """Write a file and commit it."""
        path = self.work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.git("add", "--", name)
        self.git("commit", "-q", "-m", message)

    def build(self) -> None:
        """Create origin, main, and branches in every interesting state."""
        self.git("init", "-q", "--bare", "-b", "main", str(self.origin), cwd=self.base)
        self.git("clone", "-q", str(self.origin), str(self.work), cwd=self.base)
        self.git("checkout", "-q", "-b", "main")
        self.commit("README.md", "hello\n", "init")
        self.commit(".DS_Store", "junk", "wip")
        self.git("push", "-q", "-u", "origin", "main")
        self.git("branch", "feat/merged")
        self.git("checkout", "-q", "-b", "feat/unmerged", "main")
        self.commit("only-here.txt", "exclusive\n", "valuable work")
        self.git("checkout", "-q", "-b", "feat/squashed", "main")
        self.commit("squashed.txt", "same\n", "feature part 1")
        self.git("checkout", "-q", "main")
        self.commit("squashed.txt", "same\n", "feature (#1)")
        self.git("push", "-q", "origin", "main", "feat/unmerged")
        wt = self.base / "wt"
        self.git("worktree", "add", "-q", str(wt), "-b", "feat/in-worktree", "main")
        shutil.rmtree(wt)
        (self.work / "README.md").write_text("changed\n", encoding="utf-8")
        (self.work / "stashed-new.txt").write_text("new\n", encoding="utf-8")
        self.git("add", "stashed-new.txt")
        self.git("stash", "push", "-q", "-m", "half done")
        (self.work / ".env").write_text(f"TOKEN={MARKER}\n", encoding="utf-8")
        (self.work / "scratch").mkdir()
        (self.work / "scratch" / "notes.tmp").write_text("x", encoding="utf-8")
        self.git("remote", "add", "creds", f"https://ada:{MARKER}@example.com/o/r.git")
        self.git("remote", "add", "creds2", f"https://ada:p@ss-{MARKER}@example.com:8443/o/r.git")


def run_inventory(repo: Path, *extra: str) -> tuple[int, JsonObject, str]:
    """Run inventory.py by path; return (exit code, parsed JSON, raw stdout)."""
    done = subprocess.run(
        [sys.executable, str(INVENTORY), "--repo", str(repo), *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return (done.returncode, obj(_decode(done.stdout)), done.stdout)


class InventoryTests(unittest.TestCase):
    """The inventory finds the clutter, changes nothing and leaks no credential."""

    tmp: tempfile.TemporaryDirectory[str]
    fixture: Fixture
    before: str
    code: int
    data: JsonObject
    raw: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Fixture(Path(cls.tmp.name))
        cls.fixture.build()
        cls.before = cls.snapshot()
        cls.code, cls.data, cls.raw = run_inventory(cls.fixture.work)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @classmethod
    def snapshot(cls) -> str:
        """Return a fingerprint of everything the inventory must leave untouched."""
        return "\n".join(
            [
                cls.fixture.git("for-each-ref"),
                cls.fixture.git("status", "--porcelain", "--ignored"),
                cls.fixture.git("stash", "list"),
                cls.fixture.git("worktree", "list", "--porcelain"),
                cls.fixture.git("config", "--local", "--list"),
                cls.fixture.git("count-objects", "-v"),
                cls.fixture.git("fsck", "--unreachable", "--no-reflogs", "--no-progress"),
            ]
        )

    def branch(self, ref: str) -> JsonObject:
        """Return the inventory entry of one branch."""
        for entry in items(obj(self.data["branches"])["branches"]):
            if obj(entry)["ref"] == ref:
                return obj(entry)
        self.fail(f"branch {ref} missing from the inventory")
        return JsonObject()

    def signals(self, ref: str) -> list[object]:
        return items(self.branch(ref).get("signals", []))

    def test_exits_zero_and_changes_nothing(self) -> None:
        assert self.code == 0
        assert self.snapshot() == self.before

    def test_context(self) -> None:
        context = obj(self.data["context"])
        head = obj(context["head"])
        assert head["branch"] == "main"
        assert context["main_exists"]
        assert context["origin_main_exists"]
        assert not context["bare"]
        assert not context["linked_worktree"]
        assert context["operations_in_progress"] == []

    def test_credentials_never_appear(self) -> None:
        assert MARKER not in self.raw
        remotes = obj(obj(self.data["context"])["remotes"])
        assert "creds" in remotes
        assert "***@example.com" in self.raw

    def test_saved_inventory_is_redacted(self) -> None:
        source = self.fixture.base / "saved-inventory.json"
        source.write_text(json.dumps({"note": f"TOKEN={MARKER}"}), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, str(INVENTORY), "--from", str(source)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert done.returncode == 0
        assert MARKER not in done.stdout
        assert "[REDACTED]" in done.stdout

    def test_names_containing_token_prefixes_are_kept(self) -> None:
        source = self.fixture.base / "saved-names.json"
        token = "sk-" + "a1b2c3d4e5f6g7h8"
        names = [
            "feat/task-cleanup-inventory",
            "fix/risk-assessment-page",
            "Add mask-eyJhbGciOiJIUzI1",
        ]
        source.write_text(json.dumps({"names": [*names, token]}), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, str(INVENTORY), "--from", str(source)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert done.returncode == 0
        for name in names:
            assert name in done.stdout
        assert token not in done.stdout

    def test_merged_branch_is_flagged(self) -> None:
        assert "merged-into-base" in self.signals("feat/merged")

    def test_exclusive_work_is_found(self) -> None:
        assert "has-exclusive-commits" in self.signals("feat/unmerged")
        detail = obj(self.branch("feat/unmerged")["vs_base"])
        assert detail["ahead"] == 1
        assert detail["authors"] == ["Ada"]
        assert "valuable work" in str(detail["exclusive_commits"])

    def test_squash_merged_branch_has_no_net_change(self) -> None:
        signals = self.signals("feat/squashed")
        assert "no-net-change-vs-base" in signals
        assert "has-exclusive-commits" in signals

    def test_missing_worktree_is_reported(self) -> None:
        missing = [w for w in items(self.data["worktrees"]) if obj(w)["exists"] is False]
        assert len(missing) == 1
        assert "prunable" in obj(missing[0])
        assert self.branch("feat/in-worktree")["worktree"] == str(obj(missing[0])["worktree"])

    def test_stash_is_listed_with_its_files(self) -> None:
        stash = obj(items(self.data["stashes"])[0])
        assert stash["selector"] == "stash@{0}"
        assert "stashed-new.txt" in str(stash["files"])
        assert "half done" in str(stash["message"])

    def test_noise_and_secret_names_are_found_without_contents(self) -> None:
        files = obj(self.data["files"])
        tracked_noise = obj(obj(obj(files["noise"])["tracked"])["os-metadata"])
        assert tracked_noise["sample"] == [".DS_Store"]
        assert ".env" in str(obj(files["secret_like_file_names"])["sample"])
        assert MARKER not in self.raw

    def test_working_tree_lists_untracked(self) -> None:
        untracked = obj(obj(self.data["working_tree"])["untracked"])
        assert "scratch/notes.tmp" in str(untracked["sample"])

    def test_wip_commit_is_flagged_in_history(self) -> None:
        wip = obj(obj(self.data["history"])["base"])["wip_style"]
        assert "wip" in str(wip)

    def test_out_file_and_section_roundtrip(self) -> None:
        out = Path(self.tmp.name) / "inventory.json"
        code, summary, _ = run_inventory(self.fixture.work, "--out", str(out))
        assert code == 0
        assert summary["saved_to"] == str(out)
        assert int(str(summary["branch_count"])) >= 5
        done = subprocess.run(
            [sys.executable, str(INVENTORY), "--from", str(out), "--section", "stashes"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert len(items(_decode(done.stdout))) == 1

    def test_ls_remote_compares_with_the_real_remote(self) -> None:
        self.fixture.git("remote", "remove", "creds")
        self.fixture.git("remote", "remove", "creds2")
        self.fixture.git("branch", "-D", "-r", "origin/feat/unmerged")
        code, data, _ = run_inventory(self.fixture.work, "--ls-remote")
        assert code == 0
        live = obj(obj(data["remote_live"])["origin"])
        assert "feat/unmerged" in str(live["not_fetched_yet"])

    def test_password_with_an_at_sign_is_fully_redacted(self) -> None:
        assert "ss-" not in self.raw
        remotes = obj(obj(self.data["context"])["remotes"])
        creds2 = obj(obj(remotes["creds2"])["url"])
        assert creds2["host"] == "example.com"
        assert creds2["path"] == "o/r"

    def test_section_filters_page_the_branches(self) -> None:
        done = subprocess.run(
            [
                sys.executable,
                str(INVENTORY),
                "--repo",
                str(self.fixture.work),
                "--section",
                "branches",
                "--signal",
                "has-exclusive-commits",
                "--limit",
                "1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        section = obj(_decode(done.stdout))
        assert len(items(section["branches"])) == 1
        assert int(str(section["matching_branches"])) >= 2
        total = int(str(section["matching_branches"]))
        second = subprocess.run(
            [
                sys.executable,
                str(INVENTORY),
                "--repo",
                str(self.fixture.work),
                "--section",
                "branches",
                "--signal",
                "has-exclusive-commits",
                "--limit",
                "1",
                "--offset",
                "1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        page = obj(_decode(second.stdout))
        assert len(items(page["branches"])) == min(1, total - 1)
        assert obj(items(page["branches"])[0])["ref"] != obj(items(section["branches"])[0])["ref"]

    def test_subdirectory_repo_argument_resolves_the_real_git_dir(self) -> None:
        sub = self.fixture.work / "docs"
        sub.mkdir(exist_ok=True)
        _, data, _ = run_inventory(sub)
        context = obj(data["context"])
        assert context["linked_worktree"] is False
        assert context["common_git_dir"] == str((self.fixture.work / ".git").resolve())

    def test_not_a_repository_reports_inside_the_json(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            code, data, _ = run_inventory(Path(empty))
        assert code == 0
        assert "not a Git repository" in str(data["error"])


class FailureTests(unittest.TestCase):
    """A failed git call is recorded, never silently read as an empty result."""

    def test_failures_are_recorded_not_collapsed_into_zeros(self) -> None:
        spec = importlib.util.spec_from_file_location("inventory_under_test", INVENTORY)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as empty:
            repo = module.Repo(empty)
            assert repo.out("status") == ""
        assert len(repo.errors) == 1
        assert repo.errors[0]["exit"] == 128

    def test_a_healthy_inventory_reports_no_failed_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Fixture(Path(tmp))
            fixture.build()
            _, data, _ = run_inventory(fixture.work, "--time-budget", "0")
        assert "errors" in data
        assert items(data["errors"]) == []


class ScaleAndRenameTests(unittest.TestCase):
    """Renames are read correctly and many branches do not make the audit unusable."""

    def test_staged_rename_is_one_staged_path_and_no_unstaged_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Fixture(Path(tmp))
            fixture.build()
            fixture.git("stash", "clear")
            fixture.git("checkout", "-q", "--", ".")
            fixture.git("mv", "README.md", "renamed_file.md")
            _, data, _ = run_inventory(fixture.work)
        tree = obj(data["working_tree"])
        assert obj(tree["staged"])["sample"] == ["renamed_file.md"]
        assert obj(tree["unstaged"])["count"] == 0

    def test_many_merged_branches_are_cheap_and_deep_detail_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Fixture(Path(tmp))
            fixture.build()
            head = fixture.git("rev-parse", "main").strip()
            lines = "".join(f"create refs/heads/old/{i} {head}\n" for i in range(1500))
            subprocess.run(
                [shutil.which("git") or "git", "update-ref", "--stdin"],
                cwd=fixture.work,
                env=fixture.env,
                input=lines.encode(),
                check=True,
            )
            started = time.monotonic()
            _, data, _ = run_inventory(fixture.work, "--detail-limit", "1")
            elapsed = time.monotonic() - started
            _, none, _ = run_inventory(fixture.work, "--time-budget", "0")
        branches = obj(data["branches"])
        assert len(items(branches["branches"])) >= 1500
        assert elapsed < 60
        assert int(str(branches["deep_detail_skipped"])) >= 1
        assert branches["detail_truncated"] is True
        assert obj(none["branches"])["detail_truncated"] is True


class BaseAndLimitTests(unittest.TestCase):
    """The base ref is checked against the remote, and every cut list says it was cut."""

    def fresh(self) -> Fixture:
        """Build the fixture without the unreachable credentialed remotes."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        fixture = Fixture(Path(tmp.name))
        fixture.build()
        fixture.git("remote", "remove", "creds")
        fixture.git("remote", "remove", "creds2")
        return fixture

    def test_base_matches_the_live_default(self) -> None:
        fixture = self.fresh()
        _, data, _ = run_inventory(fixture.work, "--ls-remote")
        check = obj(data["base_check"])
        assert check["remote"] == "origin"
        assert check["published"] is True
        assert check["live_default"] == "origin/main"
        assert check["matches_live_default"] is True

    def test_a_changed_remote_default_is_flagged(self) -> None:
        fixture = self.fresh()
        fixture.git("push", "-q", "origin", "main:trunk")
        fixture.git("symbolic-ref", "HEAD", "refs/heads/trunk", cwd=fixture.origin)
        _, data, _ = run_inventory(fixture.work, "--ls-remote")
        check = obj(data["base_check"])
        assert check["base"] == "origin/main"
        assert check["live_default"] == "origin/trunk"
        assert check["matches_live_default"] is False

    def test_without_the_network_the_default_is_unknown(self) -> None:
        _, data, _ = run_inventory(self.fresh().work)
        check = obj(data["base_check"])
        assert check["published"] is True
        assert check["matches_live_default"] is None

    def test_a_local_only_base_is_not_published(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Fixture(Path(tmp))
            fixture.work.mkdir()
            fixture.git("init", "-q", "-b", "main")
            fixture.commit("a.txt", "a\n", "init")
            _, data, _ = run_inventory(fixture.work)
        check = obj(data["base_check"])
        assert check["base"] == "main"
        assert check["remote"] is None
        assert check["published"] is False

    def test_long_lists_are_samples_with_a_truncated_flag(self) -> None:
        fixture = self.fresh()
        for number in range(51):
            (fixture.work / f"repo{number}" / ".git").mkdir(parents=True)
            (fixture.work / f".hidden{number}").write_text("x", encoding="utf-8")
        _, data, _ = run_inventory(fixture.work)
        nested = obj(obj(data["context"])["nested_repositories"])
        hidden = obj(obj(data["files"])["hidden_top_level"])
        for listing in (nested, hidden):
            assert int(str(listing["count"])) >= 51
            assert len(items(listing["sample"])) == 50
            assert listing["truncated"] is True

    def test_history_says_when_the_scan_hit_its_cap(self) -> None:
        spec = importlib.util.spec_from_file_location("inventory_history", INVENTORY)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fixture = self.fresh()
        repo = module.Repo(str(fixture.work))
        assert module.history_of(repo, "main")["base"]["capped"] is False
        vars(module)["HISTORY_LIMIT"] = 2
        assert module.history_of(repo, "main")["base"]["capped"] is True

    def test_unreadable_and_unwritable_files_report_inside_the_json(self) -> None:
        fixture = self.fresh()
        missing = Path(fixture.base) / "missing" / "inventory.json"
        done = subprocess.run(
            [sys.executable, str(INVENTORY), "--from", str(missing), "--section", "branches"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert done.returncode == 0
        assert "cannot read the saved inventory" in str(obj(_decode(done.stdout))["error"])
        code, data, _ = run_inventory(fixture.work, "--out", str(missing))
        assert code == 0
        assert "cannot write the inventory" in str(data["error"])
        assert not missing.exists()

    def test_not_a_repository_writes_no_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            out = Path(empty) / "inventory.json"
            code, data, _ = run_inventory(Path(empty), "--out", str(out))
            assert code == 0
            assert "not a Git repository" in str(data["error"])
            assert not out.exists()


if __name__ == "__main__":
    unittest.main()
