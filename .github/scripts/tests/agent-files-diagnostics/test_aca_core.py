"""Core tests for agent-files-diagnostics: validation, coverage, history, IDs, schemas, plans.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-files-diagnostics -v
Needs git on PATH. Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
import re
import tempfile
from typing import TYPE_CHECKING
import unittest

import _aca_built
import _aca_support
from aca import coverage, findings, history, knowledge, plan, schema, snapshot, validate

if TYPE_CHECKING:
    from aca.jsonutil import JsonObj

DOC = "https://code.claude.com/docs/en/memory"


@functools.cache
def built() -> _aca_built.Built:
    """The fixture and its deterministic results, built once for this module."""
    return _aca_built.make()


def tearDownModule() -> None:
    if built.cache_info().currsize:
        built().temp.cleanup()


def item(display: str, line: int, excerpt: str, conflict: JsonObj, **extra: object) -> JsonObj:
    """An auditor finding on one line of a fixture file."""
    base: JsonObj = {
        "category": "ambiguous",
        "severity": "low",
        "confidence": "medium",
        "sid": built().sid(display),
        "line_start": line,
        "line_end": line,
        "excerpt": excerpt,
        "conflicts_with": [conflict],
        "evidence": ["test"],
        "ladder": "n/a",
        "impact": ["reliability"],
        "disposition": "keep",
        "rationale": "test finding",
        "related": [],
        "target": "",
        "replacement": "",
        "topics": [],
    }
    base.update(extra)
    return base


def conflict(kind: str, ref: str) -> JsonObj:
    """A conflicts_with entry."""
    return {"kind": kind, "ref": ref, "detail": ""}


def verdict(entry: JsonObj) -> str:
    """'' when the finding validates, else the rejection reason."""
    found, reason = validate_one(entry)
    return "" if found is not None else reason


def validate_one(entry: JsonObj) -> tuple[findings.Finding | None, str]:
    """Validate one finding against the fixture."""
    return validate.check_finding(built().checker(), entry, "auditor:test")


LINE = "Run `npm run lint` before every commit to keep the style consistent."


@unittest.skipUnless(_aca_support.POSIX, "the fixture needs a POSIX system")
class ValidatorTests(unittest.TestCase):
    def test_a_finding_with_a_real_conflict_passes(self) -> None:
        local = built().sid("CLAUDE.local.md")
        assert verdict(item("CLAUDE.md", 3, LINE, conflict("file-line", f"{local}:4"))) == ""

    def test_lines_and_excerpts_must_match_the_file(self) -> None:
        local = built().sid("CLAUDE.local.md")
        ref = conflict("file-line", f"{local}:4")
        assert "do not exist" in verdict(item("CLAUDE.md", 99, LINE, ref))
        assert "excerpt" in verdict(item("CLAUDE.md", 3, "not there", ref))

    def test_each_conflict_kind_is_checked(self) -> None:
        good = {
            "file-line": f"{built().sid('AGENTS.md')}:3",
            "repo-fact": "package.json: no lint script",
            "doc": DOC,
            "default": "DEF-CC-AUTO-MEMORY",
        }
        bad = {
            "file-line": "S999:1",
            "repo-fact": "nowhere/missing.txt: absent",
            "doc": "https://example.com/blog",
            "default": "DEF-NOPE",
        }
        for kind, ref in good.items():
            assert verdict(item("CLAUDE.md", 3, LINE, conflict(kind, ref))) == "", kind
        for kind, ref in bad.items():
            assert verdict(item("CLAUDE.md", 3, LINE, conflict(kind, ref))), kind
        assert verdict(item("CLAUDE.md", 3, LINE, conflict("none", ""))) == "no conflict named"

    def test_unknown_categories_and_unassigned_files_are_rejected(self) -> None:
        ref = conflict("doc", DOC)
        assert "category" in verdict(item("CLAUDE.md", 3, LINE, ref, category="weird"))
        evidence = built().sid("node_modules/left-pad/CLAUDE.md")
        entry = item("CLAUDE.md", 3, "# left-pad", ref, sid=evidence)
        assert "not an audited" in verdict(entry)

    def test_judgment_only_redundancy_is_downgraded(self) -> None:
        entry = item(
            "CLAUDE.md",
            3,
            LINE,
            conflict("doc", DOC),
            category="redundant-with-defaults",
            ladder="c",
            confidence="high",
            disposition="remove",
        )
        found, _ = validate_one(entry)
        assert found is not None
        assert found.confidence == "low"
        assert found.disposition == "investigate"
        assert found.trail

    def test_redundancy_needs_an_evidence_level(self) -> None:
        entry = item("CLAUDE.md", 3, LINE, conflict("doc", DOC), category="redundant-with-defaults")
        assert "evidence ladder" in verdict(entry)

    def test_a_revision_without_replacement_becomes_investigate(self) -> None:
        entry = item("CLAUDE.md", 3, LINE, conflict("doc", DOC), disposition="revise")
        found, _ = validate_one(entry)
        assert found is not None
        assert found.disposition == "investigate"

    def test_external_claims_are_located(self) -> None:
        claim: JsonObj = {
            "sid": built().sid("CLAUDE.md"),
            "line_start": 3,
            "line_end": 3,
            "excerpt": LINE,
            "claim": "npm run lint exists in npm 10",
            "subject": "npm",
            "why": "version claim",
            "sources": ["https://docs.npmjs.com"],
            "impact_if_false": "the instruction fails",
        }
        found, reason = validate.check_claim(built().checker(), claim)
        assert found is not None, reason
        bad = {**claim, "excerpt": "nope"}
        found, reason = validate.check_claim(built().checker(), bad)
        assert found is None
        assert "excerpt" in reason


class CoverageTests(unittest.TestCase):
    @staticmethod
    def snap(work: Path, lines: list[str]) -> snapshot.Snapshot:
        path = work / "S001-CLAUDE.md"
        _ = path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return snapshot.Snapshot(work=work, paths={"S001": path}, lines={"S001": lines})

    @staticmethod
    def read(path: Path, numbered: list[str], *, error: bool = False) -> coverage.ReadEvent:
        return coverage.ReadEvent(str(path), "\n".join(numbered), error)

    def test_every_line_must_arrive_intact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snap = self.snap(Path(temp), ["a", "b", "c", "d"])
            path = snap.paths["S001"]
            reads = [
                self.read(path, ["1\ta", "2→b"]),
                self.read(path, ["3\tCHANGED", "4\td"]),
                self.read(path, ["3\tc"], error=True),
                self.read(Path(temp) / "other.md", ["3\tc"]),
            ]
            ledger = coverage.build(reads, snap, ["S001"])["S001"]
            assert not ledger.complete
            assert ledger.missing == [3]
            reads.append(self.read(path, ["3\tc"]))
            assert coverage.build(reads, snap, ["S001"])["S001"].complete

    def test_missing_lines_are_compressed(self) -> None:
        assert coverage.compress([1, 2, 3, 7, 9, 10]) == "1-3, 7, 9-10"
        assert coverage.compress([]) == ""

    def test_reads_tools_and_usage_come_from_a_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "agent-x.jsonl"
            call = {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/f"}}
            grep = {"type": "tool_use", "id": "t2", "name": "Grep", "input": {}}
            usage = {"input_tokens": 7, "output_tokens": 3}
            result = {"type": "tool_result", "tool_use_id": "t1", "content": "1\tx"}
            events: list[object] = [
                {"type": "assistant", "message": {"usage": usage, "content": [call, grep]}},
                {"type": "user", "message": {"content": [result]}},
                {"type": "attachment", "attachment": {}},
            ]
            lines = [json.dumps(event) for event in events] + ["not json"]
            _ = path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            reads, tools = coverage.reads_from_transcript(path)
            assert [(read.file_path, read.text) for read in reads] == [("/f", "1\tx")]
            assert tools == {"Read", "Grep"}
            usage = coverage.usage_from_transcript(path)
            assert usage["input_tokens"] == 7
            assert usage["output_tokens"] == 3
            assert usage["requests"] == 1

    def test_the_run_folder_is_found_by_its_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            claude_dir = Path(temp)
            run_dir = claude_dir / "projects" / "p" / "s" / "subagents" / "workflows" / "wf_1"
            run_dir.mkdir(parents=True)
            _ = (run_dir / "journal.jsonl").write_text(
                '{"type":"started","label":"B1","agentId":"a1"}\n', encoding="utf-8"
            )
            assert coverage.find_run_dir(claude_dir, "wf_1") == run_dir
            assert coverage.find_run_dir(claude_dir, "wf_2") is None
            assert coverage.agent_ids(run_dir) == {"B1": "a1"}
            assert coverage.transcript(run_dir, "a1") == run_dir / "agent-a1.jsonl"


class HistoryTests(unittest.TestCase):
    @staticmethod
    def finding(fid: str, unit: str) -> findings.Finding:
        found = findings.Finding("ambiguous", "low", "low", "S001", 1, 1, "x", "keep", "", "test")
        found.fid, found.unit = fid, unit
        return found

    @staticmethod
    def entry(run_id: str, status: str, ids: list[str], units: dict[str, str]) -> JsonObj:
        return {"run_id": run_id, "status": status, "findings": ids, "units": units}

    def test_changes_against_the_last_complete_run(self) -> None:
        runs = [
            self.entry(
                "r1", "complete-with-findings", ["A", "B", "C"], {"A": "ua", "B": "ub", "C": "uc"}
            ),
            self.entry("r2", "complete-with-findings", ["A", "B"], {"A": "ua", "B": "ub"}),
        ]
        now = [self.finding("A", "ua"), self.finding("D", "ud"), self.finding("C", "uc")]
        change = history.compare(now, runs)
        assert change.previous == "r2"
        assert change.persisting == ["A"]
        assert change.new == ["D"]
        assert change.regressed == ["C"]
        assert change.resolved == ["B"]

    def test_a_partial_run_never_claims_a_fix(self) -> None:
        runs = [self.entry("r1", "complete-with-findings", ["A", "B"], {"A": "ua", "B": "ub"})]
        change = history.compare([self.finding("A", "ua")], runs, partial=True)
        assert change.resolved == []
        assert change.unconfirmed == ["B"]

    def test_a_recategorized_finding_keeps_its_unit(self) -> None:
        runs = [self.entry("r1", "complete-with-findings", ["ACA-AMB-u1"], {"ACA-AMB-u1": "u1"})]
        change = history.compare([self.finding("ACA-DUP-u1", "u1")], runs)
        assert change.recategorized == [("ACA-AMB-u1", "ACA-DUP-u1")]
        assert change.resolved == []

    def test_record_keeps_the_index_and_latest_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = self.entry("r1", "complete", [], {})
            history.record(root, entry, {"run_id": "r1"})
            history.record(root, self.entry("r2", "complete", [], {}), {"run_id": "r2"})
            assert [run["run_id"] for run in history.read_index(root)] == ["r1", "r2"]
            latest = json.loads((root / "latest.json").read_text(encoding="utf-8"))
            assert latest["run_id"] == "r2"


class FindingIdTests(unittest.TestCase):
    def test_ids_name_the_category_and_unit(self) -> None:
        assert findings.finding_id("duplicated", "abc") == "ACA-DUP-abc"
        assert findings.finding_id("weird", "abc") == "ACA-GEN-abc"

    def test_repeats_get_suffixes_whatever_the_input_order(self) -> None:
        def make(start: int) -> findings.Finding:
            found = findings.Finding(
                "dead", "low", "low", "S001", start, start, "x", "keep", "", "t"
            )
            found.unit = "u"
            return found

        first = [make(5), make(2), make(9)]
        findings.assign_ids(first)
        second = [make(9), make(5), make(2)]
        findings.assign_ids(second)
        by_start = {item.start: item.fid for item in first}
        assert by_start == {item.start: item.fid for item in second}
        assert sorted(by_start.values()) == ["ACA-DED-u", "ACA-DED-u-2", "ACA-DED-u-3"]


class SchemaTests(unittest.TestCase):
    def test_every_schema_is_strict_and_matches_its_workflow_copy(self) -> None:
        workflows = _aca_support.PLUGIN / "workflows"
        copies = {
            "auditor": "audit-domains.js",
            "reconciler": "review-and-verify.js",
            "rebuttal": "review-and-verify.js",
            "decide": "review-and-verify.js",
            "verify": "review-and-verify.js",
            "verifier": "review-and-verify.js",
        }
        for role, script in copies.items():
            loaded = schema.load(role)
            assert loaded.get("additionalProperties") is False, role
            text = (workflows / script).read_text(encoding="utf-8")
            marker = f"/* schema:{role} */"
            assert marker in text, (role, script)
            start = text.index(marker) + len(marker)
            end = text.index("/* end */", start)
            assert json.loads(text[start:end]) == loaded, role

    def test_strict_objects_reject_missing_extra_and_wrong_values(self) -> None:
        loaded = schema.load("decide")
        good: JsonObj = {"decisions": [{"fid": "x", "outcome": "owner", "reason": "r"}]}
        assert schema.validate(good, loaded) == []
        assert schema.validate({}, loaded)
        assert schema.validate({**good, "extra": 1}, loaded)
        bad: JsonObj = {"decisions": [{"fid": "x", "outcome": "maybe", "reason": "r"}]}
        assert schema.validate(bad, loaded)


class KnowledgeTests(unittest.TestCase):
    def test_the_bundled_knowledge_is_complete(self) -> None:
        bundled = knowledge.load()
        assert bundled.version
        assert bundled.docs_checked
        assert set(bundled.covers) == {"claude-code", "codex"}
        assert bundled.sources
        assert all(hashes for hashes in bundled.sources.values())
        assert "DEF-CC-AUTO-MEMORY" in bundled.defaults
        assert "autoMemoryEnabled" in bundled.settings_keys

    def test_sections_follow_headings_outside_fences(self) -> None:
        page = "intro\n## One\na\n```\n## not a heading\n```\n### Sub\nb\n## Two\nc"
        found = knowledge.sections(page)
        assert list(found) == ["(top)", "One", "One > Sub", "Two"]
        assert "not a heading" in found["One"]

    def test_section_hashes_ignore_reflow(self) -> None:
        assert knowledge.section_hash("a  b\nc") == knowledge.section_hash("a b c")
        assert knowledge.section_hash("a b") != knowledge.section_hash("a c")

    def test_only_https_urls_are_fetched(self) -> None:
        assert knowledge.fetch("http://code.claude.com/docs/en/memory.md") is None
        assert knowledge.fetch("file:///etc/passwd") is None

    def test_the_settings_index_is_parsed(self) -> None:
        page = (
            "| [`model`](#model) | Default model | Any file |\n"
            "| [`oldKey`](#oldkey) | Deprecated: use model | User |\n"
        )
        keys = knowledge.parse_settings_index(page)
        assert keys["model"]["files"] == ["user", "project", "local", "managed"]
        assert keys["oldKey"]["deprecated"] is True


@unittest.skipUnless(_aca_support.POSIX, "the fixture needs a POSIX system")
class PlanTests(unittest.TestCase):
    def test_chunks_cover_every_line_within_the_limits(self) -> None:
        lines = ["x" * 10] * (plan.CHUNK_LINES * 2 + 5)
        planned = plan.chunks(lines)
        assert planned[0] == (1, plan.CHUNK_LINES)
        assert sum(count for _offset, count in planned) == len(lines)
        wide = ["y" * 30_000] * 3
        assert len(plan.chunks(wide)) == len(wide)

    def test_packages_keep_domains_apart_and_list_every_file(self) -> None:
        packages = plan.make_packages(built().inventory, built().snapshot, built().result)
        assigned = [sid for package in packages for sid in package.sids]
        audited = [source.sid for source in built().inventory.audited]
        assert sorted(assigned) == sorted(audited)
        assert {package.domain for package in packages} == {"A", "B", "C", "D", "E"}
        for package in packages:
            found = [built().inventory.by_sid(sid) for sid in package.sids]
            assert all(found)
            assert {source.domain for source in found if source} == {package.domain}
            assert package.name.startswith(package.domain)

    def test_auditor_tasks_name_each_snapshot_copy_and_its_chunks(self) -> None:
        packages = plan.make_packages(built().inventory, built().snapshot, built().result)
        package = next(item for item in packages if item.domain == "B")
        task = plan.auditor_task(package, built().inventory, built().snapshot, built().result)
        for sid in package.sids:
            assert f"| {sid} |" in task
            assert str(built().snapshot.paths[sid]) in task
        assert re.search(r"- C\d{3} ", task) or "(none)" in task
        assert "(do not repeat them)" in task

    def test_the_manifest_carries_the_four_fields(self) -> None:
        rows = json.loads(plan.manifest_json(built().inventory, built().snapshot))
        for row in rows:
            for key in ("loading", "consumption", "availability", "applicability", "snapshot"):
                assert key in row, key
