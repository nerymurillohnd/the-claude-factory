"""End-to-end tests for agent-files-diagnostics: the four stages through the entry script.

Each scenario builds the known-answer fixture in a fresh folder, runs `prepare`, writes the
journal and transcripts a workflow run would leave, runs `accept` for the domains and the review,
then `finalize`, and checks the status, the report files, the history, and that nothing audited
changed. No model runs and nothing is spent.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-files-diagnostics -v
Needs git on PATH; POSIX only (the audit refuses native Windows, which by_path.sh checks).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import functools
import json
from pathlib import Path
import re
import tempfile
from typing import TYPE_CHECKING, cast
import unittest

import _aca_support
from aca.jsonutil import as_obj, get_list, get_obj, get_str

if TYPE_CHECKING:
    from aca.jsonutil import JsonObj

KNOWN_FINDINGS = {
    ("dead", "medium", "~/.claude/CLAUDE.md", 4, 4),
    ("dead", "medium", "CLAUDE.md", 5, 5),
    ("dead", "medium", "docs/guide.md", 5, 5),
    ("dead", "medium", ".claude/rules/typescript.md", 1, 4),
    ("duplicated", "medium", "CLAUDE.local.md", 4, 4),
    ("duplicated", "low", "~/.claude/agents/helper.md", 7, 7),
    ("duplicated", "low", "CLAUDE.md", 3, 3),
}
LINE = "Run `npm run lint` before every commit to keep the style consistent."
CANDIDATE = re.compile(r"^- (C\d{3}) ", re.MULTILINE)
ROOT = tempfile.TemporaryDirectory()


def tearDownModule() -> None:
    ROOT.cleanup()


def load(path: Path) -> JsonObj:
    """Decode a JSON file as an object."""
    return as_obj(_aca_support.load(path))


def git_state(repo: Path) -> str:
    """HEAD and the full porcelain status (untracked files included)."""
    status = _aca_support.git(repo, "status", "--porcelain", "--untracked-files=all")
    return _aca_support.git(repo, "rev-parse", "HEAD") + status


@dataclass
class Run:
    """One audit of a fresh fixture, driven stage by stage."""

    fixture: _aca_support.Fixture
    env: dict[str, str]
    prepared: JsonObj = field(default_factory=dict)
    domains: JsonObj = field(default_factory=dict)
    review: JsonObj = field(default_factory=dict)
    final: JsonObj = field(default_factory=dict)
    before: dict[str, str] = field(default_factory=dict)
    git_before: str = ""

    @property
    def run_dir(self) -> Path:
        """The run folder prepare created."""
        return Path(get_str(self.prepared, "run_dir"))

    @property
    def work(self) -> Path:
        """The work folder with the snapshot copies and the task files."""
        return Path(get_str(self.prepared, "work"))

    def sources(self) -> dict[str, JsonObj]:
        """sid -> manifest row, from state.json (kept after the work folder is deleted)."""
        state = load(self.run_dir / "state.json")
        return {get_str(as_obj(row), "sid"): as_obj(row) for row in get_list(state, "sources")}

    def sid(self, display: str) -> str:
        """The manifest ID of a display path."""
        return next(
            sid for sid, row in self.sources().items() if get_str(row, "display") == display
        )

    def package_of(self, sid: str) -> JsonObj:
        """The package that holds a source."""
        for raw in get_list(self.prepared, "packages"):
            package = as_obj(raw)
            if sid in [str(item) for item in get_list(package, "files")]:
                return package
        message = f"no package holds {sid}"
        raise AssertionError(message)

    def cli(self, *args: str) -> JsonObj:
        """Run one stage and decode its JSON."""
        done = _aca_support.run_cli(list(args), self.env)
        assert done.returncode == 0, done.stderr
        return as_obj(_aca_support.parse(done.stdout))

    @property
    def report(self) -> JsonObj:
        """report.json of this run."""
        return load(self.run_dir / "report.json")

    def displays(self) -> dict[str, str]:
        """Manifest ID -> display path, from the report."""
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


def auditor_result(run: Run, package: JsonObj, *, invalid: bool = False) -> JsonObj:
    """A valid auditor result for one package: every file analyzed, every candidate judged."""
    sids = [str(item) for item in get_list(package, "files")]
    task = Path(get_str(package, "task")).read_text(encoding="utf-8")
    candidates = [
        {"id": cid, "verdict": "rejected", "reason": "test"} for cid in CANDIDATE.findall(task)
    ]
    findings: list[JsonObj] = []
    claims: list[JsonObj] = []
    project = run.sid("CLAUDE.md")
    if project in sids:
        local = run.sid("CLAUDE.local.md")
        findings.append(
            {
                "category": "ambiguous",
                "severity": "medium",
                "confidence": "medium",
                "sid": project,
                "line_start": 3,
                "line_end": 3,
                "excerpt": LINE,
                "conflicts_with": [{"kind": "file-line", "ref": f"{local}:4", "detail": ""}],
                "evidence": ["the local copy says the same with no exception"],
                "ladder": "n/a",
                "impact": ["reliability"],
                "disposition": "investigate",
                "rationale": "test finding from the auditor",
                "related": [],
                "target": "",
                "replacement": "",
                "topics": [],
            }
        )
        findings.append({**findings[0], "excerpt": "this text is not on line 3"})
        claims.append(
            {
                "sid": project,
                "line_start": 3,
                "line_end": 3,
                "excerpt": LINE,
                "claim": "npm run lint needs npm 10 or later",
                "subject": "npm",
                "why": "a version claim the repository cannot settle",
                "sources": ["https://docs.npmjs.com"],
                "impact_if_false": "the instruction fails on older npm",
            }
        )
    return {
        "files": [{"sid": sid, "status": "analyzed", "note": ""} for sid in sids],
        "findings": findings if not invalid else "not a list",
        "candidates": candidates,
        "external_claims": claims,
    }


def reads_for(run: Run, package: JsonObj) -> list[tuple[Path, int, int]]:
    """One full read per file of the package, from its snapshot copy."""
    rows = run.sources()
    reads: list[tuple[Path, int, int]] = []
    for sid in [str(item) for item in get_list(package, "files")]:
        row = rows[sid]
        reads.append((Path(get_str(row, "snapshot")), 1, max(int(str(row.get("lines", 1))), 1)))
    return reads


def domain_scenario(run: Run, **tweaks: object) -> _aca_support.Scenario:
    """The first workflow's results: one auditor per package, complete coverage by default."""
    results: dict[str, object] = {}
    reads: dict[str, list[tuple[Path, int, int]]] = {}
    tools: dict[str, list[str]] = {}
    skip: dict[str, int] = {}
    target = get_str(run.package_of(run.sid("CLAUDE.md")), "name")
    for raw in get_list(run.prepared, "packages"):
        package = as_obj(raw)
        name = get_str(package, "name")
        invalid = bool(tweaks.get("invalid")) and name == target
        results[name] = auditor_result(run, package, invalid=invalid)
        reads[name] = reads_for(run, package)
        if tweaks.get("skip_line") and name == target:
            skip[name] = 3
        if tweaks.get("stray_tool") and name == target:
            tools[name] = ["Bash"]
    return _aca_support.Scenario(results=results, reads=reads, tools=tools, skip=skip)


def review_scenario(run: Run, *, outcome: str = "owner") -> _aca_support.Scenario:
    """The second workflow's results: the reconciler disputes the auditor's finding."""
    rows = [
        as_obj(row)
        for row in cast("list[object]", _aca_support.load(run.work / "tasks" / "findings.json"))
    ]
    auditor = next((row for row in rows if get_str(row, "origin").startswith("auditor")), {})
    decisions: list[JsonObj] = []
    for row in rows:
        fid = get_str(row, "fid")
        verdict = "dismiss" if row is auditor else "accept"
        decisions.append(
            {
                "fid": fid,
                "verdict": verdict,
                "disposition": get_str(row, "disposition"),
                "severity": get_str(row, "severity"),
                "reason": "disputed in the test" if verdict == "dismiss" else "holds",
                "evidence": [],
            }
        )
    results: dict[str, object] = {
        "reconcile": {
            "decisions": decisions,
            "pairs": [],
            "cross_findings": [],
            "conflict_groups": [],
        },
        f"rebuttal-1:{get_str(auditor, 'origin')}": {
            "responses": [
                {
                    "fid": get_str(auditor, "fid"),
                    "position": "rebut",
                    "reason": "it stands",
                    "evidence": [],
                }
            ]
        },
        "decide-1": {
            "decisions": [{"fid": get_str(auditor, "fid"), "outcome": outcome, "reason": "test"}]
        },
        "verify-1": {
            "results": [
                {"fid": get_str(row, "fid"), "holds": True, "reason": "re-read"} for row in rows
            ]
        },
    }
    claims = [as_obj(raw) for raw in get_list(get_obj(run.domains, "review"), "claims")]
    if claims:
        assert get_list(claims[0], "claims"), "a claims batch carries its rows inline"
        assert "task" not in claims[0], "the researcher gets no file to read"
        results["claims-1"] = {
            "results": [
                {
                    "cid": "ACA-EXT-placeholder",
                    "verdict": "confirmed",
                    "summary": "npm 10 is current",
                    "sources": [
                        {
                            "url": "https://docs.npmjs.com",
                            "quote": "npm 10",
                            "checked": "2026-10-15",
                        }
                    ],
                }
            ]
        }
    return _aca_support.Scenario(results=results, reads={}, tools={}, skip={})


def start() -> Run:
    """Build a fresh fixture and run prepare."""
    base = Path(tempfile.mkdtemp(dir=ROOT.name))
    fixture = _aca_support.build(base)
    run = Run(fixture=fixture, env=_aca_support.environment(fixture))
    run.before, run.git_before = _aca_support.digests(fixture), git_state(fixture.repo)
    run.prepared = run.cli("prepare", "--repo", str(fixture.repo), "--offline")
    return run


def complete_run(**tweaks: object) -> Run:
    """A whole audit on a fresh fixture, with optional tweaks to the domain stage."""
    run = start()
    _ = _aca_support.fake_run(run.fixture, "wf_domains", domain_scenario(run, **tweaks))
    run.domains = run.cli(
        "accept", "--run", str(run.run_dir), "--stage", "domains", "--workflow-run", "wf_domains"
    )
    outcome = str(tweaks.get("outcome", "owner"))
    _ = _aca_support.fake_run(run.fixture, "wf_review", review_scenario(run, outcome=outcome))
    run.review = run.cli(
        "accept", "--run", str(run.run_dir), "--stage", "review", "--workflow-run", "wf_review"
    )
    if tweaks.get("edit"):
        path = run.fixture.repo / "docs" / "guide.md"
        _ = path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    checked = {get_str(as_obj(row), "fid"): "ok" for row in get_list(run.review, "to_inspect")}
    if checked and tweaks.get("reject_one"):
        first = min(checked)
        checked[first] = "rejected: the coordinator read the lines and disagrees"
    if tweaks.get("skip_inspection"):
        checked = {}
    if tweaks.get("inline"):
        run.final = run.cli(
            "finalize", "--run", str(run.run_dir), "--checked-json", json.dumps(checked)
        )
        return run
    checked_file = run.run_dir / "checked.json"
    _ = checked_file.write_text(json.dumps(checked), encoding="utf-8")
    run.final = run.cli("finalize", "--run", str(run.run_dir), "--checked", str(checked_file))
    return run


@functools.cache
def scenario(name: str) -> Run:
    """One cached audit per scenario."""
    tweaks: dict[str, dict[str, object]] = {
        "clean": {},
        "inline": {"inline": True},
        "reject": {"reject_one": True},
        "open": {"outcome": "open"},
        "skip": {"skip_line": True},
        "stray": {"stray_tool": True},
        "invalid": {"invalid": True},
        "edit": {"edit": True},
        "uninspected": {"skip_inspection": True},
    }
    return complete_run(**tweaks[name])


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class PrepareTests(unittest.TestCase):
    def test_prepare_plans_one_package_per_domain_with_task_files(self) -> None:
        run = start()
        packages = [as_obj(raw) for raw in get_list(run.prepared, "packages")]
        assert {get_str(package, "domain") for package in packages} == {"A", "B", "C", "D", "E"}
        for package in packages:
            task = Path(get_str(package, "task"))
            assert task.is_file(), task
            assert "read every line" in task.read_text(encoding="utf-8")
        assert run.prepared["deterministic_findings"] == len(KNOWN_FINDINGS)
        assert "~/.claude/CLAUDE.md" in [
            str(item) for item in get_list(run.prepared, "external_sources")
        ]
        assert (run.work / "snap").is_dir()
        assert (run.work / "knowledge" / "drift.md").is_file()
        assert (run.run_dir / "state.json").is_file()


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class CompleteRunTests(unittest.TestCase):
    def test_known_answers_and_status(self) -> None:
        run = scenario("clean")
        assert get_str(run.final, "status") == "complete-with-findings", run.final
        assert run.found() == KNOWN_FINDINGS
        auditor = run.found("auditor")
        assert auditor == {("ambiguous", "medium", "CLAUDE.md", 3, 3)}

    def test_every_package_is_complete_with_proven_coverage(self) -> None:
        run = scenario("clean")
        for raw in get_list(run.domains, "packages"):
            package = as_obj(raw)
            assert get_str(package, "status") == "complete", package
            assert not get_obj(package, "gaps")
        assert get_list(run.domains, "retry") == []
        for row in get_list(run.report, "sources"):
            source = as_obj(row)
            if "evidence" in get_str(source, "status"):
                continue
            assert get_str(source, "status") == "read completely", source

    def test_nothing_audited_changes_and_git_is_untouched(self) -> None:
        run = scenario("clean")
        assert _aca_support.digests(run.fixture) == run.before
        assert git_state(run.fixture.repo) == run.git_before
        assert not (run.work).exists(), "the work folder is deleted at the end"

    def test_report_files_and_self_ignoring_folder(self) -> None:
        run = scenario("clean")
        root = run.fixture.report_root
        assert (root / ".gitignore").read_text(encoding="utf-8") == "*\n"
        for name in ("report.md", "report.json", "status.json", "state.json"):
            assert (run.run_dir / name).is_file(), name
        assert (root / "latest.json").is_file()
        text = (run.run_dir / "report.md").read_text(encoding="utf-8")
        for heading in (
            "## Domain assignments",
            "## Coverage",
            "## Findings",
            "## External claims",
            "## Usage",
        ):
            assert heading in text, heading
        assert "| Loading | Consumption | Availability | Applicability |" in text

    def test_invalid_findings_are_listed_not_reported(self) -> None:
        run = scenario("clean")
        rejected = [as_obj(row) for row in get_list(run.report, "rejected")]
        assert any("excerpt" in get_str(row, "reason") for row in rejected), rejected

    def test_the_challenge_round_kept_the_auditors_finding(self) -> None:
        run = scenario("clean")
        rows = [as_obj(row) for row in get_list(run.report, "findings")]
        auditor = next(row for row in rows if get_str(row, "origin").startswith("auditor"))
        assert get_str(auditor, "status") == "final"
        assert any("owner's evidence stood" in str(note) for note in get_list(auditor, "trail"))
        assert get_str(auditor, "verified") == "confirmed"
        assert get_str(auditor, "coordinator_check") == "ok"

    def test_external_claims_record_their_sources(self) -> None:
        run = scenario("clean")
        claims = [as_obj(row) for row in get_list(run.report, "external_claims")]
        assert len(claims) == 1
        assert get_str(claims[0], "verdict") in {"confirmed", "unverified"}

    def test_usage_comes_from_the_transcripts(self) -> None:
        run = scenario("clean")
        usage = [as_obj(row) for row in get_list(run.report, "usage")]
        labels = {get_str(row, "label") for row in usage}
        assert any(label.startswith("B") for label in labels)
        assert "reconcile" in labels

    def test_latest_points_at_the_run(self) -> None:
        run = scenario("clean")
        latest = run.cli("latest", "--repo", str(run.fixture.repo))
        assert get_str(latest, "run_id") == get_str(run.final, "run_id")


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class CoordinatorTests(unittest.TestCase):
    def test_a_rejected_finding_is_dismissed_with_the_reason(self) -> None:
        run = scenario("reject")
        dismissed = [as_obj(row) for row in get_list(run.report, "dismissed")]
        assert len(dismissed) == 1
        assert "coordinator" in get_str(dismissed[0], ["trail"][0]) or dismissed[0]["trail"]
        assert get_str(run.final, "status") == "complete-with-findings"

    def test_inline_verdicts_work_like_the_file(self) -> None:
        run = scenario("inline")
        assert get_str(run.final, "status") == "complete-with-findings"
        assert not (run.run_dir / "checked.json").exists()

    def test_uninspected_findings_make_the_run_partial(self) -> None:
        run = scenario("uninspected")
        assert get_str(run.final, "status") == "partial"
        assert any("not inspected" in str(text) for text in get_list(run.final, "problems"))

    def test_an_unsettled_dispute_stays_open(self) -> None:
        run = scenario("open")
        rows = [as_obj(row) for row in get_list(run.report, "findings")]
        auditor = next(row for row in rows if get_str(row, "origin").startswith("auditor"))
        assert get_str(auditor, "status") == "open"
        assert run.final["open_decisions"] == 1


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class PartialRunTests(unittest.TestCase):
    def test_a_skipped_line_makes_the_run_partial(self) -> None:
        run = scenario("skip")
        assert get_str(run.final, "status") == "partial"
        packages = {
            get_str(as_obj(p), "name"): as_obj(p) for p in get_list(run.domains, "packages")
        }
        target = packages[get_str(run.package_of(run.sid("CLAUDE.md")), "name")]
        assert get_str(target, "status") == "partial"
        assert get_obj(target, "gaps")[run.sid("CLAUDE.md")] == "3"
        assert get_list(run.domains, "retry") == [get_str(target, "name")]

    def test_a_tool_outside_the_allowlist_voids_the_package(self) -> None:
        run = scenario("stray")
        packages = [as_obj(p) for p in get_list(run.domains, "packages")]
        failed = [p for p in packages if get_str(p, "status") == "failed"]
        assert len(failed) == 1
        assert "Bash" in get_str(failed[0], "error")
        assert run.found("auditor") == set()

    def test_invalid_output_is_refused(self) -> None:
        run = scenario("invalid")
        packages = [as_obj(p) for p in get_list(run.domains, "packages")]
        failed = [p for p in packages if get_str(p, "status") == "failed"]
        assert len(failed) == 1
        assert "invalid output" in get_str(failed[0], "error")

    def test_an_edit_during_the_run_is_caught(self) -> None:
        run = scenario("edit")
        assert get_str(run.final, "status") == "partial"
        assert any(
            "changed during the audit" in str(text) for text in get_list(run.final, "problems")
        )

    def test_a_missing_journal_is_a_failure(self) -> None:
        run = start()
        done = run.cli(
            "accept", "--run", str(run.run_dir), "--stage", "domains", "--workflow-run", "wf_none"
        )
        assert any("wf_none" in str(text) for text in get_list(done, "failures"))


@unittest.skipUnless(_aca_support.POSIX, "the audit runs on macOS, Linux and WSL only")
class CommandLineTests(unittest.TestCase):
    def test_latest_without_a_report_says_so(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        env = _aca_support.environment(fixture)
        done = _aca_support.run_cli(["latest", "--repo", str(fixture.repo)], env)
        assert done.returncode == 0
        assert get_str(as_obj(_aca_support.parse(done.stdout)), "status") == "no-report"

    def test_preflight_refuses_an_old_cli(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        env = _aca_support.environment(fixture)
        old = fixture.bin / "old-claude"
        _aca_support.write(old, '#!/bin/sh\necho "2.1.200 (Claude Code)"\n')
        old.chmod(0o755)
        env["AGENT_CONTEXT_AUDIT_CLAUDE"] = str(old)
        done = _aca_support.run_cli(["prepare", "--repo", str(fixture.repo), "--offline"], env)
        status = as_obj(_aca_support.parse(done.stdout))
        assert get_str(status, "status") == "cannot-run"
        assert "too old" in get_str(status, "reason")

    def test_usage_errors_exit_four(self) -> None:
        base = Path(tempfile.mkdtemp(dir=ROOT.name))
        fixture = _aca_support.build(base)
        env = _aca_support.environment(fixture)
        assert _aca_support.run_cli(["bogus"], env).returncode == 4
        assert _aca_support.run_cli(["accept", "--run", "x"], env).returncode == 4
