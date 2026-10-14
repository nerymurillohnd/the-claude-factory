"""Core tests for agent-context-audit: validation, coverage, history, IDs, schemas, plans, workers.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-context-audit -v
Needs git on PATH. Standard library only; runs on Python 3.9+. Worker tests run the fake claude
CLI and are skipped outside POSIX systems.
"""

from __future__ import annotations

import functools
import json
import os
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING
import unittest

import _aca_built
import _aca_support
from aca import (
    coverage,
    findings,
    history,
    knowledge,
    plan,
    schema,
    snapshot,
    validate,
    workers,
)
from aca.jsonutil import get_obj, str_list

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
        other = f"{built().sid('AGENTS.md')}:3-3"
        assert verdict(item("CLAUDE.md", 3, LINE, conflict("file-line", other))) == ""

    def test_lines_and_excerpts_must_match_the_file(self) -> None:
        doc = conflict("doc", DOC)
        assert "do not exist" in verdict(item("CLAUDE.md", 99, LINE, doc))
        assert "excerpt" in verdict(item("CLAUDE.md", 3, "words that are not there", doc))

    def test_each_conflict_kind_is_checked(self) -> None:
        repo = built().fixture.repo
        cases = {
            ("file-line", "S999:1-1"): False,
            ("file-line", f"{built().sid('AGENTS.md')}:40-41"): False,
            ("repo-fact", "package.json: no lint script"): True,
            ("repo-fact", f"{repo / 'package.json'}: no lint script"): True,
            ("repo-fact", "missing/nowhere.json: absent"): False,
            ("repo-fact", "/etc/hosts: outside the project"): False,
            ("doc", DOC): True,
            ("doc", f"<{DOC}>"): True,
            ("doc", "https://example.com/blog"): False,
            ("doc", "http://code.claude.com/docs/en/memory"): False,
            ("default", "DEF-CC-AUTO-MEMORY"): True,
            ("default", "DEF-NOT-A-DEFAULT"): False,
            ("none", ""): False,
        }
        for (kind, ref), valid in cases.items():
            reason = verdict(item("CLAUDE.md", 3, LINE, conflict(kind, ref)))
            assert (reason == "") is valid, (kind, ref, reason)

    def test_unknown_categories_and_unassigned_files_are_rejected(self) -> None:
        doc = conflict("doc", DOC)
        assert "category" in verdict(item("CLAUDE.md", 3, LINE, doc, category="bad"))
        checker = built().checker()
        checker.allowed = frozenset()
        found, reason = validate.check_finding(
            checker, item("CLAUDE.md", 3, LINE, doc), "auditor:test"
        )
        assert found is None
        assert "not assigned" in reason

    def test_the_own_enablement_entry_is_never_a_defect(self) -> None:
        excerpt = '"agent-context-audit@the-claude-factory": true'
        entry = item("~/.claude/settings.json", 3, excerpt, conflict("doc", DOC))
        assert "own enablement entry" in verdict(entry)

    def test_judgment_only_redundancy_is_downgraded(self) -> None:
        entry = item(
            "CLAUDE.md",
            3,
            LINE,
            conflict("default", "DEF-CC-AUTO-MEMORY"),
            category="redundant-with-defaults",
            ladder="c",
            confidence="high",
            disposition="remove",
        )
        found, reason = validate_one(entry)
        assert reason == ""
        assert found is not None
        assert (found.confidence, found.disposition) == ("low", "investigate")
        assert found.trail

    def test_redundancy_needs_an_evidence_level(self) -> None:
        entry = item(
            "CLAUDE.md",
            3,
            LINE,
            conflict("default", "DEF-CC-AUTO-MEMORY"),
            category="redundant-with-defaults",
        )
        assert "ladder" in verdict(entry)

    def test_a_revision_without_replacement_becomes_investigate(self) -> None:
        entry = item("CLAUDE.md", 3, LINE, conflict("doc", DOC), disposition="revise")
        found, _reason = validate_one(entry)
        assert found is not None
        assert found.disposition == "investigate"

    def test_external_claims_are_located(self) -> None:
        checker = built().checker()
        claim: JsonObj = {
            "sid": built().sid("CLAUDE.md"),
            "line_start": 3,
            "line_end": 3,
            "excerpt": LINE,
            "claim": "lint works",
            "subject": "npm",
            "why": "test",
            "sources": [],
            "impact_if_false": "none",
        }
        found, reason = validate.check_claim(checker, claim)
        assert (found is not None, reason) == (True, "")
        claim["line_start"] = 50
        claim["line_end"] = 50
        found, reason = validate.check_claim(checker, claim)
        assert found is None
        assert reason


class CoverageTests(unittest.TestCase):
    @staticmethod
    def snap(work: Path, lines: list[str]) -> snapshot.Snapshot:
        path = work / "S001-CLAUDE.md"
        _ = path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return snapshot.Snapshot(work=work, paths={"S001": path}, lines={"S001": lines})

    @staticmethod
    def read(path: Path, numbered: list[str], *, error: bool = False) -> workers.ReadEvent:
        return workers.ReadEvent(str(path), 1, 0, "\n".join(numbered), error)

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


class HistoryTests(unittest.TestCase):
    @staticmethod
    def finding(fid: str, unit: str) -> findings.Finding:
        found = findings.Finding("ambiguous", "low", "low", "S001", 1, 1, "x", "keep", "", "test")
        found.fid, found.unit = fid, unit
        return found

    @staticmethod
    def entry(run_id: str, status: str, fids: dict[str, str]) -> JsonObj:
        return {"run_id": run_id, "status": status, "findings": list(fids), "units": fids}

    def test_changes_against_the_last_complete_run(self) -> None:
        runs = [
            self.entry("r1", "complete-with-findings", {"ACA-AMB-old": "u0"}),
            self.entry("r2", "complete-with-findings", {"ACA-AMB-a": "u1", "ACA-DUP-b": "u2"}),
            self.entry("r3", "failure", {}),
        ]
        now = [
            self.finding("ACA-AMB-a", "u1"),
            self.finding("ACA-OVL-b", "u2"),
            self.finding("ACA-AMB-old", "u0"),
            self.finding("ACA-FAL-c", "u3"),
        ]
        change = history.compare(now, runs)
        assert change.previous == "r2"
        assert change.persisting == ["ACA-AMB-a"]
        assert change.recategorized == [("ACA-DUP-b", "ACA-OVL-b")]
        assert change.regressed == ["ACA-AMB-old"]
        assert change.new == ["ACA-FAL-c"]
        assert change.resolved == []

    def test_a_partial_run_never_claims_a_fix(self) -> None:
        runs = [self.entry("r1", "complete-with-findings", {"ACA-AMB-a": "u1", "ACA-AMB-b": "u2"})]
        now = [self.finding("ACA-AMB-a", "u1")]
        assert history.compare(now, runs).resolved == ["ACA-AMB-b"]
        partial = history.compare(now, runs, partial=True)
        assert partial.resolved == []
        assert partial.unconfirmed == ["ACA-AMB-b"]

    def test_a_complete_baseline_wins_over_a_later_partial_one(self) -> None:
        runs = [
            self.entry("r1", "complete-with-findings", {"ACA-AMB-a": "u1"}),
            self.entry("r2", "partial", {}),
        ]
        assert history.compare([self.finding("ACA-AMB-a", "u1")], runs).previous == "r1"

    @unittest.skipUnless(_aca_support.POSIX, "the report folder lock is POSIX flock")
    def test_record_keeps_the_index_and_latest_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for number in range(3):
                entry = self.entry(f"r{number}", "complete", {})
                history.record(root, entry, {"run_id": f"r{number}"})
            assert [run["run_id"] for run in history.read_index(root)] == ["r0", "r1", "r2"]
            latest = _aca_support.load(root / history.LATEST)
            assert latest == {"run_id": "r2"}


class FindingIdTests(unittest.TestCase):
    def test_ids_name_the_category_and_unit(self) -> None:
        assert findings.finding_id("duplicated", "abc") == "ACA-DUP-abc"
        assert findings.finding_id("unknown", "abc") == "ACA-GEN-abc"

    def test_repeats_get_suffixes_whatever_the_input_order(self) -> None:
        def make(start: int) -> findings.Finding:
            found = findings.Finding(
                "ambiguous", "low", "low", "S001", start, start, "x", "keep", "", "test"
            )
            found.unit = "u1"
            return found

        first = [make(1), make(2)]
        second = [make(2), make(1)]
        findings.assign_ids(first)
        findings.assign_ids(second)
        assert sorted((item.start, item.fid) for item in first) == sorted(
            (item.start, item.fid) for item in second
        )
        assert len({item.fid for item in first}) == len(first)


class SchemaTests(unittest.TestCase):
    def test_every_role_has_a_strict_schema_and_a_contract(self) -> None:
        for role in ("auditor", "reconciler", "rebuttal", "decide", "verifier"):
            loaded = schema.load(role)
            assert loaded.get("additionalProperties") is False, role
            assert (schema.SCHEMAS.parent / "roles" / f"{role}.md").is_file(), role

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

    def test_shards_keep_domains_apart_and_list_every_file(self) -> None:
        shards = plan.make_shards(built().inventory, built().snapshot, built().result)
        assigned = [sid for shard in shards for sid in shard.sids]
        audited = [source.sid for source in built().inventory.audited]
        assert sorted(assigned) == sorted(audited)
        for shard in shards:
            sources = [built().inventory.by_sid(sid) for sid in shard.sids]
            assert {source.domain for source in sources if source} == {shard.domain}
            assert all(sources)

    def test_auditor_prompts_name_each_snapshot_copy_and_its_chunks(self) -> None:
        shards = plan.make_shards(built().inventory, built().snapshot, built().result)
        shard = shards[0]
        prompt = plan.auditor_prompt(shard, built().inventory, built().snapshot, built().result)
        for sid in shard.sids:
            assert f"| {sid} |" in prompt
            assert str(built().snapshot.paths[sid]) in prompt

    def test_worker_settings_deny_originals_and_secrets(self) -> None:
        root = built().fixture.report_root
        settings = plan.auditor_settings(built().inventory, root)
        deny = str_list(get_obj(settings, "permissions").get("deny"))
        assert f"Read(/{root.as_posix()}/**)" in deny
        for source in built().inventory.sources:
            assert f"Read(/{source.path.as_posix()})" in deny
        assert "Read(**/.env)" in deny
        assert settings["disableAllHooks"] is True

    def test_verifiers_may_fetch_only_listed_domains(self) -> None:
        allow = json.dumps(plan.verifier_settings(["docs.example.org"]))
        assert "WebFetch(domain:github.com)" in allow
        assert "WebFetch(domain:docs.example.org)" in allow
        assert "WebSearch" not in allow


class WorkerEnvTests(unittest.TestCase):
    def test_session_markers_are_dropped_and_isolation_added(self) -> None:
        parent = {
            "CLAUDECODE": "1",
            "CLAUDE_CODE_ENTRYPOINT": "cli",
            "CLAUDE_CODE_EFFORT_LEVEL": "max",
            "CLAUDE_EFFORT": "max",
            "CLAUDE_AGENT_SDK_VERSION": "1",
            "CLAUDE_CODE_OAUTH_TOKEN": "token",
            "CLAUDE_CODE_USE_BEDROCK": "1",
            "HOME": "/home/u",
        }
        env = workers.worker_env(parent)
        for dropped in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_EFFORT_LEVEL"):
            assert dropped not in env, dropped
        assert "CLAUDE_EFFORT" not in env
        assert "CLAUDE_AGENT_SDK_VERSION" not in env
        assert env["CLAUDE_CODE_OAUTH_TOKEN"] == parent["CLAUDE_CODE_OAUTH_TOKEN"]
        assert env["CLAUDE_CODE_USE_BEDROCK"] == "1"
        assert env["HOME"] == "/home/u"
        assert env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] == "1"
        assert env["CLAUDE_CODE_DISABLE_CRON"] == "1"

    def test_the_command_locks_the_worker_down(self) -> None:
        spec = workers.Spec(
            name="w",
            role="auditor",
            prompt="p",
            schema={"type": "object"},
            role_file=Path("/r.md"),
            settings_file=Path("/s.json"),
            model="sonnet",
            effort="high",
            tools="Read,Grep,Glob",
            max_turns=10,
            timeout=60,
            budget=1.5,
        )
        argv = workers.command("claude", spec, Path("/work"))
        joined = " ".join(argv)
        for flag in (
            "-p",
            "--no-session-persistence",
            "--restricted",
            "--strict-mcp-config",
            "--verbose",
        ):
            assert flag in argv, flag
        pairs = {argv[index]: argv[index + 1] for index in range(1, len(argv) - 1)}
        assert pairs["--setting-sources"] == ""
        assert pairs["--tools"] == "Read,Grep,Glob"
        assert pairs["--permission-mode"] == "dontAsk"
        assert pairs["--permission-prompts"] == "none"
        assert pairs["--add-dir"] == "/work"
        assert pairs["--max-budget-usd"] == "1.50"
        assert "--dangerously-skip-permissions" not in joined

    def test_the_stream_gives_reads_tools_and_the_result(self) -> None:
        use: JsonObj = {
            "type": "tool_use",
            "id": "t1",
            "name": "Read",
            "input": {"file_path": "/w/S001-CLAUDE.md", "offset": 1, "limit": 2},
        }
        back: JsonObj = {"type": "tool_result", "tool_use_id": "t1", "content": "1\ta\n2\tb"}
        final: JsonObj = {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "structured_output": {"files": []},
            "total_cost_usd": 0.5,
            "num_turns": 2,
        }
        lines = [
            json.dumps({"type": "system", "subtype": "init", "model": "m"}),
            json.dumps({"type": "assistant", "message": {"content": [use]}}),
            json.dumps({"type": "user", "message": {"content": [back]}}),
            "not json",
            json.dumps(final),
        ]
        result = workers.Result(spec=self.spec())
        workers.parse_stream(lines, result)
        assert result.ok
        assert result.tools_used == ["Read"]
        assert [(read.offset, read.limit, read.text) for read in result.reads] == [
            (1, 2, "1\ta\n2\tb")
        ]
        assert (result.model, result.cost, result.turns) == ("m", 0.5, 2)

    def test_a_stream_without_a_result_is_an_error(self) -> None:
        result = workers.Result(spec=self.spec())
        workers.parse_stream([json.dumps({"type": "system", "subtype": "init"})], result)
        assert not result.ok
        assert "without a result" in result.error

    def test_a_missing_override_binary_is_not_found(self) -> None:
        assert workers.find_claude({workers.CLAUDE_ENV: "/no/such/claude"}) is None
        assert workers.find_claude({workers.CLAUDE_ENV: str(_aca_support.FAKE_CLAUDE)})

    @staticmethod
    def spec(timeout: int = 60) -> workers.Spec:
        return workers.Spec(
            name="probe",
            role="auditor",
            prompt="no files",
            schema={"type": "object"},
            role_file=_aca_support.SCRIPTS / "aca" / "data" / "roles" / "auditor.md",
            settings_file=Path("/dev/null"),
            model="m",
            effort="low",
            tools="Read",
            max_turns=1,
            timeout=timeout,
        )


@unittest.skipUnless(_aca_support.POSIX, "the fake claude runs through its shebang")
class WorkerProcessTests(unittest.TestCase):
    def test_a_slow_worker_is_stopped_at_its_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            env = {"PATH": os.environ.get("PATH", ""), "FAKE_CLAUDE_SCENARIO": "slow"}
            spec = WorkerEnvTests.spec(timeout=1)
            result = workers.run_one(str(_aca_support.FAKE_CLAUDE), spec, Path(temp), env)
            assert not result.ok
            assert "timed out after 1 s" in result.error
            assert result.seconds < _aca_support.RUN_TIMEOUT

    def test_a_crash_reports_the_error_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            env = {"PATH": os.environ.get("PATH", ""), "FAKE_CLAUDE_SCENARIO": "fail"}
            spec = WorkerEnvTests.spec()
            result = workers.run_one(str(_aca_support.FAKE_CLAUDE), spec, Path(temp), env)
            assert not result.ok
            assert "simulated crash" in result.error
