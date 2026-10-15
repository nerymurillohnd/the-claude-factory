"""Inventory and deterministic-check tests for agent-files-diagnostics on the known-answer fixture.

Every context file the fixture creates must be in the manifest with the right kind, load mode,
domain and status; everything the audit skips must be listed as out of scope; and the
deterministic checks must find exactly the defects the fixture plants.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-files-diagnostics -v
Needs git on PATH. Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

import functools
import unittest

import _aca_built
import _aca_support
from aca import sources

# display path -> (kind, {tool: mode}); the auto memory files are added per fixture.
EXPECTED_SOURCES = {
    ".claude/rules/typescript.md": ("rule", {"claude": "dead"}),
    "CLAUDE.local.md": ("claude-local-md", {"claude": "always"}),
    "CLAUDE.md": ("claude-md", {"claude": "always"}),
    "docs/guide.md": ("import", {"claude": "always"}),
    "packages/web/CLAUDE.md": ("claude-md", {"claude": "on-demand"}),
    "node_modules/left-pad/CLAUDE.md": ("claude-md", {"claude": "on-demand"}),
    "~/.claude/CLAUDE.md": ("claude-md", {"claude": "always"}),
    ".claude/agents/reviewer.md": ("subagent", {"claude": "on-demand"}),
    ".claude/loop.md": ("loop-md", {"claude": "on-demand"}),
    ".claude/output-styles/terse.md": ("output-style", {"claude": "not-loaded"}),
    "~/.claude/agents/helper.md": ("subagent", {"claude": "on-demand"}),
    "AGENTS.md": ("agents-md", {"claude": "not-loaded", "codex": "always"}),
    "packages/web/AGENTS.md": ("agents-md", {"claude": "not-loaded", "codex": "conditional"}),
    "~/.codex/AGENTS.md": ("codex-agents-md", {"codex": "always"}),
    ".claude/settings.json": ("settings", {"claude": "config"}),
    "~/.claude/settings.json": ("settings", {"claude": "config"}),
    ".codex/config.toml": ("codex-config", {"codex": "conditional"}),
    ".mcp.json": ("mcp-json", {"claude": "config"}),
    "~/.claude.json": ("claude-json-mcp", {"claude": "config"}),
    "~/.codex/config.toml": ("codex-config", {"codex": "config"}),
}
# Evidence only: configuration, and third-party files the user cannot change.
EXPECTED_EVIDENCE = {
    "node_modules/left-pad/CLAUDE.md",
    ".claude/settings.json",
    "~/.claude/settings.json",
    ".codex/config.toml",
    ".mcp.json",
    "~/.claude.json",
    "~/.codex/config.toml",
}
EXPECTED_DOMAINS = {
    "AGENTS.md": "A",
    "packages/web/AGENTS.md": "A",
    "~/.codex/AGENTS.md": "A",
    "CLAUDE.md": "B",
    "CLAUDE.local.md": "B",
    "docs/guide.md": "B",
    "~/.claude/CLAUDE.md": "B",
    "packages/web/CLAUDE.md": "B",
    ".claude/rules/typescript.md": "C",
    ".claude/agents/reviewer.md": "E",
    "~/.claude/agents/helper.md": "E",
    ".claude/loop.md": "E",
    ".claude/output-styles/terse.md": "E",
}
EXPECTED_OUT_OF_SCOPE = {".claude/skills": 1, ".claude/commands": 1}


@functools.cache
def built() -> _aca_built.Built:
    """The fixture and its deterministic results, built once for this module."""
    return _aca_built.make()


def tearDownModule() -> None:
    if built.cache_info().currsize:
        built().temp.cleanup()


def display(sid: str) -> str:
    """The display path of a manifest ID."""
    return built().display(sid)


@unittest.skipUnless(_aca_support.POSIX, "the fixture needs a POSIX system")
class InventoryTests(unittest.TestCase):
    def expected(self) -> dict[str, tuple[str, dict[str, str]]]:
        fixture = built().fixture
        memory = _aca_support.memory_dir(fixture.home, fixture.repo)
        shown = "~/" + memory.relative_to(fixture.home).as_posix()
        return {
            **EXPECTED_SOURCES,
            f"{shown}/MEMORY.md": ("auto-memory-index", {"claude": "always"}),
            f"{shown}/build.md": ("auto-memory-topic", {"claude": "on-demand"}),
        }

    def test_every_context_file_is_in_the_manifest_and_nothing_else(self) -> None:
        found = {source.display for source in built().inventory.sources}
        assert found == set(self.expected())

    def test_kinds_and_load_modes(self) -> None:
        expected = self.expected()
        for source in built().inventory.sources:
            kind, modes = expected[source.display]
            loaders = {loader.tool: loader.mode for loader in source.loaders}
            assert (source.display, source.kind, loaders) == (source.display, kind, modes)

    def test_ids_are_sequential_and_every_source_was_read(self) -> None:
        sids = [source.sid for source in built().inventory.sources]
        assert sids == [f"S{index:03d}" for index in range(1, len(sids) + 1)]
        for source in built().inventory.sources:
            status = "evidence" if source.display in EXPECTED_EVIDENCE else "in-scope"
            assert source.status == status, source.display
            assert source.sha256, source.display
            assert source.lines, source.display

    def test_only_markdown_is_audited_and_domains_follow_the_file_type(self) -> None:
        for source in built().inventory.sources:
            if source.status != "in-scope":
                assert source.domain == "evidence", source.display
                continue
            assert source.is_markdown, source.display
            if source.display in EXPECTED_DOMAINS:
                assert source.domain == EXPECTED_DOMAINS[source.display], source.display
            else:
                assert source.domain == "D", source.display

    def test_the_four_classification_fields_are_filled(self) -> None:
        by_display = {source.display: source for source in built().inventory.sources}
        always = by_display["CLAUDE.md"]
        assert always.loading == sources.LOADING_AUTOMATIC
        assert always.consumption == sources.CONSUMPTION_DOCUMENTED
        assert always.availability == sources.AVAILABILITY_COMPLETE
        assert always.applicability == sources.APPLICABLE
        rule = by_display[".claude/rules/typescript.md"]
        assert rule.loading == sources.LOADING_UNKNOWN
        assert rule.applicability == sources.APPLICABILITY_SUPERSEDED
        style = by_display[".claude/output-styles/terse.md"]
        assert style.applicability == sources.APPLICABILITY_SUPERSEDED
        nested = by_display["packages/web/CLAUDE.md"]
        assert nested.loading == sources.LOADING_ON_DEMAND
        subset = by_display["~/.claude.json"]
        assert subset.availability == sources.AVAILABILITY_OPAQUE

    def test_skipped_locations_are_listed_with_counts(self) -> None:
        listed = {str(item["path"]): item["count"] for item in built().inventory.out_of_scope}
        assert listed == EXPECTED_OUT_OF_SCOPE

    def test_imports_record_each_edge_and_its_status(self) -> None:
        edges = {(edge.importer, edge.line, edge.status) for edge in built().inventory.imports}
        assert edges == {
            ("~/.claude/CLAUDE.md", 4, "missing"),
            ("CLAUDE.md", 5, "missing"),
            ("CLAUDE.md", 7, "ok"),
        }

    def test_units_carry_a_text_identity_and_an_occurrence_identity(self) -> None:
        found = built().inventory
        local, project = built().sid("CLAUDE.local.md"), built().sid("CLAUDE.md")
        shared = set(found.text_ids[local]) & set(found.text_ids[project])
        assert shared, "the repeated lint line must share one text id across both files"
        assert not set(found.unit_ids[local]) & set(found.unit_ids[project])


@unittest.skipUnless(_aca_support.POSIX, "the fixture needs a POSIX system")
class CheckTests(unittest.TestCase):
    def test_candidates_need_a_reader(self) -> None:
        found = {(display(item.sid), item.start, item.kind) for item in built().result.candidates}
        assert ("CLAUDE.md", 3, "missing-script") in found
        assert ("CLAUDE.md", 9, "stripped-comment") in found

    def test_every_deterministic_finding_names_its_conflict(self) -> None:
        for item in built().result.findings:
            assert item.conflicts_with, item.rationale
            assert item.origin == "deterministic"
            assert item.excerpt, item.rationale

    def test_configuration_never_yields_a_finding(self) -> None:
        for item in built().result.findings:
            source = built().inventory.by_sid(item.sid)
            assert source is not None
            assert source.is_markdown, source.display
