"""End-to-end tests for agent-context-audit: the entry script against the fake claude CLI.

Each scenario builds the known-answer fixture in a fresh folder, runs a whole audit through the
entry script with a minimal environment (no Codex CLI on PATH, a throwaway HOME), and checks the
exit code, the status, the report files, the history, and that nothing audited changed.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-context-audit -v
Needs git on PATH; POSIX only (the audit refuses native Windows, which by_path.sh checks).
"""

from __future__ import annotations

from dataclasses import dataclass
import functools
import json
from pathlib import Path
import sys
import tempfile
from typing import TYPE_CHECKING, cast
import unittest
from unittest import mock

import _aca_support
from aca import cli
from aca.jsonutil import as_list, as_obj, get_list, get_obj, get_str

if TYPE_CHECKING:
    from aca.jsonutil import JsonObj

KNOWN_FINDINGS = {
    ("wrong", "high", ".claude/settings.json", 8, 11),
    ("contradictory", "medium", "~/.claude/settings.json", 7, 7),
    ("dead", "medium", "~/.claude/CLAUDE.md", 4, 4),
    ("dead", "medium", "CLAUDE.md", 5, 5),
    ("dead", "medium", ".claude/rules/typescript.md", 1, 4),
    ("duplicated", "medium", "CLAUDE.local.md", 4, 4),
    ("obsolete", "medium", "~/.codex/config.toml", 2, 2),
    ("wrong", "medium", ".claude/settings.json", 2, 2),
    ("duplicated", "low", "~/.claude/agents/helper.md", 7, 7),
    ("duplicated", "low", "CLAUDE.md", 3, 3),
}
ROOT = tempfile.TemporaryDirectory()


def tearDownModule() -> None:
    ROOT.cleanup()


@dataclass
class Run:
    """One audit of a fresh fixture, with what the project looked like before and after."""

    fixture: _aca_support.Fixture
    code: int
    stdout: str
    stderr: str
    before: dict[str, str]
    after: dict[str, str]
    git_before: str
    git_after: str

    @property
    def status(self) -> JsonObj:
        """The --json status object."""
        return as_obj(_aca_support.parse(self.stdout))

    @property
    def report(self) -> JsonObj:
        """report.json of this run."""
        path = Path(get_str(self.status, "report")).parent / "report.json"
        return as_obj(_aca_support.load(path))

    def displays(self) -> dict[str, str]:
        """Manifest ID -> display path."""
        return {
            get_str(as_obj(row), "sid"): get_str(as_obj(row), "path")
            for row in get_list(self.report, "sources")
        }

    def found(self, origin: str = "deterministic") -> set[tuple[str, str, str, int, int]]:
        """(category, severity, path, start, end) of the reported findings of one origin."""
        shown = self.displays()
        rows = [as_obj(row) for row in get_list(self.report, "findings")]
        return {
            (
                get_str(row, "category"),
                get_str(row, "severity"),
                shown[get_str(row, "sid")],
                cast("int", row["start"]),
                cast("int", row["end"]),
            )
            for row in rows
            if get_str(row, "origin").startswith(origin)
        }


def git_state(repo: Path) -> str:
    """HEAD and the full porcelain status (untracked files included)."""
    status = _aca_support.git(repo, "status", "--porcelain", "--untracked-files=all")
    return _aca_support.git(repo, "rev-parse", "HEAD") + status


def audit(scenario: str, *args: str, **extra: str) -> Run:
    """Build a fresh fixture and audit it once."""
    base = Path(tempfile.mkdtemp(dir=ROOT.name))
    fixture = _aca_support.build(base)
    env = _aca_support.environment(fixture, scenario, **extra)
    if scenario == "touch":
        env["FAKE_CLAUDE_TOUCH"] = str(fixture.repo / "docs" / "guide.md")
    before, git_before = _aca_support.digests(fixture), git_state(fixture.repo)
    argv = ["run", "--repo", str(fixture.repo), "--offline", "--json", *args]
    done = _aca_support.run_cli(argv, env)
    return Run(
        fixture=fixture,
        code=done.returncode,
        stdout=done.stdout,
        stderr=done.stderr,
        before=before,
        after=_aca_support.digests(fixture),
        git_before=git_before,
        git_after=git_state(fixture.repo),
    )


@functools.cache
def scenario(name: str) -> Run:
    """One cached audit per scenario."""
    return audit(name)


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class CompleteRunTests(unittest.TestCase):
    def test_known_answers_and_exit_code(self) -> None:
        run = scenario("clean")
        assert run.code == 1, run.stderr
        assert get_str(run.status, "status") == "complete-with-findings"
        assert run.found() == KNOWN_FINDINGS

    def test_nothing_audited_changes_and_git_is_untouched(self) -> None:
        run = scenario("clean")
        assert run.before == run.after
        assert run.git_before == run.git_after

    def test_report_files_and_self_ignoring_folder(self) -> None:
        run = scenario("clean")
        root = run.fixture.report_root
        report = Path(get_str(run.status, "report"))
        for name in ("report.md", "report.json", "status.json"):
            assert (report.parent / name).is_file(), name
        for name in ("index.json", "latest.json", "notice.json"):
            assert (root / name).is_file(), name
        assert (root / ".gitignore").read_text(encoding="utf-8") == "*\n"

    def test_the_report_covers_every_source_and_says_how(self) -> None:
        run = scenario("clean")
        text = Path(get_str(run.status, "report")).read_text(encoding="utf-8")
        for heading in ("## Metadata", "## Coverage", "## Executive summary", "## Findings"):
            assert heading in text, heading
        for display in run.displays().values():
            assert display in text, display
        assert "| Codex CLI | not installed |" in text
        for row in get_list(run.report, "domains"):
            assert get_str(as_obj(row), "status") == "complete"

    def test_every_finding_is_traceable(self) -> None:
        run = scenario("findings")
        rows = [as_obj(row) for row in get_list(run.report, "findings")]
        assert any(get_str(row, "origin").startswith("auditor") for row in rows)
        for row in rows:
            assert get_str(row, "fid").startswith("ACA-"), row
            assert get_str(row, "excerpt"), row
            assert get_list(row, "conflicts_with"), row

    def test_a_rerun_keeps_every_finding_id(self) -> None:
        run = audit("clean")
        first = {get_str(as_obj(row), "fid") for row in get_list(run.report, "findings")}
        env = _aca_support.environment(run.fixture, "clean")
        argv = ["run", "--repo", str(run.fixture.repo), "--offline", "--json"]
        again = _aca_support.run_cli(argv, env)
        status = as_obj(_aca_support.parse(again.stdout))
        report = as_obj(_aca_support.load(Path(get_str(status, "report")).parent / "report.json"))
        second = {get_str(as_obj(row), "fid") for row in get_list(report, "findings")}
        assert first == second
        change = get_obj(report, "change")
        assert sorted(first) == sorted(str(fid) for fid in get_list(change, "persisting"))
        latest = as_obj(_aca_support.load(run.fixture.report_root / "latest.json"))
        assert get_str(latest, "run_id") == get_str(status, "run_id")

    def test_exit_zero_keeps_the_status(self) -> None:
        run = audit("clean", "--exit-zero")
        assert run.code == 0
        assert get_str(run.status, "status") == "complete-with-findings"

    def test_the_mode_is_recorded(self) -> None:
        run = audit("clean", "--mode", "scheduled")
        assert get_str(run.report, "mode") == "scheduled"


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class PartialRunTests(unittest.TestCase):
    def assert_partial(self, run: Run, words: str) -> None:
        assert run.code == 2, (run.code, run.stderr)
        assert get_str(run.status, "status") == "partial"
        problems = " ".join(str(item) for item in get_list(run.status, "problems"))
        assert words in problems, problems
        text = Path(get_str(run.status, "report")).read_text(encoding="utf-8")
        assert "**partial**" in text
        assert "**complete" not in text

    def test_a_skipped_line_makes_the_run_partial(self) -> None:
        self.assert_partial(scenario("gap"), "never received")

    def test_a_crashed_worker_is_a_visible_failure(self) -> None:
        self.assert_partial(scenario("fail"), "simulated crash")

    def test_invalid_output_is_refused(self) -> None:
        self.assert_partial(scenario("invalid"), "invalid output")

    def test_a_tool_outside_the_allowlist_voids_the_shard(self) -> None:
        self.assert_partial(scenario("stray"), "outside its allowlist")

    def test_an_edit_during_the_run_is_caught(self) -> None:
        self.assert_partial(scenario("touch"), "changed during the audit")

    def test_findings_that_fail_validation_are_listed_not_reported(self) -> None:
        run = scenario("badexcerpt")
        assert run.code == 1
        assert get_list(run.report, "rejected")
        assert run.found("auditor") == set()
        assert run.found() == KNOWN_FINDINGS


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class ReviewTests(unittest.TestCase):
    def test_a_rebutted_finding_stays_final(self) -> None:
        run = scenario("contest")
        assert run.code == 1
        assert cast("int", run.status["open_decisions"]) == 0
        trails = [get_list(as_obj(row), "trail") for row in get_list(run.report, "findings")]
        assert any(trail for trail in trails)

    def test_an_unsettled_dispute_stays_open(self) -> None:
        run = scenario("open")
        assert cast("int", run.status["open_decisions"]) == 1
        statuses = [get_str(as_obj(row), "status") for row in get_list(run.report, "findings")]
        assert statuses.count("open") == 1

    def test_external_claims_are_kept_apart_and_unverified(self) -> None:
        run = scenario("claims")
        claims = [as_obj(row) for row in get_list(run.report, "external_claims")]
        assert claims
        for claim in claims:
            assert get_str(claim, "cid").startswith("ACA-EXT-")
            assert get_str(claim, "verdict") == "unverified"

    def test_online_verification_records_its_sources(self) -> None:
        run = audit("claims", "--verify-online")
        claims = [as_obj(row) for row in get_list(run.report, "external_claims")]
        assert claims
        for claim in claims:
            assert get_str(claim, "verdict") == "confirmed"
            assert get_list(claim, "verdict_evidence")


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class CommandLineTests(unittest.TestCase):
    def test_human_output_names_the_report_and_the_deep_link(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        env = _aca_support.environment(fixture)
        done = _aca_support.run_cli(["--repo", str(fixture.repo), "--offline"], env)
        assert done.returncode == 1
        assert "status: complete-with-findings (exit 1)" in done.stdout
        assert "report: " in done.stdout
        assert "claude-cli://open?cwd=" in done.stdout

    def test_two_repositories_report_the_worst_exit_code(self) -> None:
        first = _aca_support.build(Path(tempfile.mkdtemp(dir=ROOT.name)))
        second = _aca_support.build(Path(tempfile.mkdtemp(dir=ROOT.name)))
        env = _aca_support.environment(first)
        argv = ["run", "--repo", str(first.repo), "--repo", str(second.repo), "--offline", "--json"]
        done = _aca_support.run_cli(argv, env)
        statuses = as_list(_aca_support.parse(done.stdout))
        assert len(statuses) == 2
        assert done.returncode == 1

    def test_out_keeps_reports_outside_the_repository(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        out = base / "reports"
        env = _aca_support.environment(fixture)
        argv = ["run", "--repo", str(fixture.repo), "--offline", "--json", "--out", str(out)]
        done = _aca_support.run_cli(argv, env)
        report = Path(get_str(as_obj(_aca_support.parse(done.stdout)), "report"))
        assert report.is_file()
        assert out.resolve() in report.parents
        assert not fixture.report_root.exists()
        latest = _aca_support.run_cli(
            ["latest", "--repo", str(fixture.repo), "--out", str(out)], env
        )
        assert latest.returncode == 0
        assert str(report) in latest.stdout

    def test_latest_without_a_report_is_an_error(self) -> None:
        fixture = _aca_support.build(Path(tempfile.mkdtemp(dir=ROOT.name)))
        done = _aca_support.run_cli(["latest", "--repo", str(fixture.repo)], {"PATH": ""})
        assert done.returncode == 4
        assert "no report yet" in done.stdout

    def test_an_unwritable_report_folder_is_a_failure(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        blocker = base / "not-a-folder"
        _ = blocker.write_text("x", encoding="utf-8")
        env = _aca_support.environment(fixture)
        argv = ["run", "--repo", str(fixture.repo), "--offline", "--json", "--out", str(blocker)]
        done = _aca_support.run_cli(argv, env)
        status = as_obj(_aca_support.parse(done.stdout))
        assert done.returncode == 3
        assert get_str(status, "status") == "failure"
        assert get_str(status, "report") == ""
        assert get_list(status, "failures")

    def test_preflight_refuses_a_missing_or_old_cli(self) -> None:
        fixture = _aca_support.build(Path(tempfile.mkdtemp(dir=ROOT.name)))
        missing = _aca_support.environment(fixture, AGENT_CONTEXT_AUDIT_CLAUDE="/no/claude")
        done = _aca_support.run_cli(["--repo", str(fixture.repo), "--json"], missing)
        assert done.returncode == 4
        assert get_str(as_obj(_aca_support.parse(done.stdout)), "status") == "cannot-run"
        old = _aca_support.environment(fixture, FAKE_CLAUDE_VERSION="2.1.299")
        done = _aca_support.run_cli(["--repo", str(fixture.repo)], old)
        assert done.returncode == 4
        assert "too old" in done.stdout
        done = _aca_support.run_cli(["--repo", str(fixture.repo), "--exit-zero"], old)
        assert done.returncode == 0

    def test_native_windows_is_refused(self) -> None:
        with mock.patch.object(sys, "platform", "win32"):
            claude, reason = cli.preflight({})
        assert claude == ""
        assert "WSL" in reason

    def test_usage_errors_exit_four(self) -> None:
        done = _aca_support.run_cli(["run", "--challenge-rounds", "9"], {"PATH": ""})
        assert done.returncode == 4


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class SessionNoticeTests(unittest.TestCase):
    @staticmethod
    def notice(fixture: _aca_support.Fixture, **extra: str) -> str:
        env = {"PATH": str(fixture.bin), "HOME": str(fixture.home), **extra}
        event = json.dumps({"hook_event_name": "SessionStart", "cwd": str(fixture.repo)})
        return _aca_support.run_cli(["session-notice"], env, stdin=event).stdout

    def test_a_new_report_is_announced_once(self) -> None:
        run = audit("clean")
        first = as_obj(_aca_support.parse(self.notice(run.fixture)))
        assert "systemMessage" in first
        output = get_obj(first, "hookSpecificOutput")
        assert get_str(output, "hookEventName") == "SessionStart"
        assert get_str(run.status, "report") in get_str(output, "additionalContext")
        assert self.notice(run.fixture) == ""

    def test_the_option_turns_the_notice_off(self) -> None:
        run = audit("clean")
        off = {"CLAUDE_PLUGIN_OPTION_SESSION_NOTICE": "false"}
        assert self.notice(run.fixture, **off) == ""
        assert self.notice(run.fixture) != ""

    def test_an_interactive_run_is_not_announced_again(self) -> None:
        run = audit("clean", "--mode", "interactive")
        assert self.notice(run.fixture) == ""

    def test_the_hook_finds_the_project_from_its_variable(self) -> None:
        run = audit("clean")
        project = {"CLAUDE_PROJECT_DIR": str(run.fixture.repo / "packages")}
        env = {"PATH": str(run.fixture.bin), "HOME": str(run.fixture.home), **project}
        done = _aca_support.run_cli(["session-notice"], env, stdin="")
        assert "systemMessage" in done.stdout
        assert done.returncode == 0

    def test_a_project_without_reports_gets_no_output(self) -> None:
        fixture = _aca_support.build(Path(tempfile.mkdtemp(dir=ROOT.name)))
        assert self.notice(fixture) == ""
