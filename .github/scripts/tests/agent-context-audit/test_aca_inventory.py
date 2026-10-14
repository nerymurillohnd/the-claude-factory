"""Inventory and deterministic-check tests for agent-context-audit on the known-answer fixture.

Every context file the fixture creates must be in the manifest with the right kind and load mode,
everything the audit skips must be listed as out of scope, and the deterministic checks must find
exactly the defects the fixture plants.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-context-audit -v
Needs git on PATH. Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

import functools
from pathlib import Path
import unittest

import _aca_built
import _aca_support
from aca import (
    claude_config,
    config_checks,
)

# display path -> (kind, {tool: mode}); the auto memory files are added per fixture.
EXPECTED_SOURCES = {
    ".claude/rules/typescript.md": ("rule", {"claude": "dead"}),
    "CLAUDE.local.md": ("claude-local-md", {"claude": "always"}),
    "CLAUDE.md": ("claude-md", {"claude": "always"}),
    "docs/guide.md": ("import", {"claude": "always"}),
    "packages/web/CLAUDE.md": ("claude-md", {"claude": "on-demand"}),
    "~/.claude/CLAUDE.md": ("claude-md", {"claude": "always"}),
    ".claude/agents/reviewer.md": ("subagent", {"claude": "on-demand"}),
    ".claude/loop.md": ("loop-md", {"claude": "on-demand"}),
    ".claude/output-styles/terse.md": ("output-style", {"claude": "not-loaded"}),
    "~/.claude/agents/helper.md": ("subagent", {"claude": "on-demand"}),
    "AGENTS.md": ("agents-md", {"claude": "not-loaded", "codex": "always"}),
    "packages/web/AGENTS.md": ("agents-md", {"claude": "not-loaded", "codex": "conditional"}),
    "~/.codex/AGENTS.md": ("codex-agents-md", {"codex": "always"}),
    ".claude/settings.json": ("settings", {"claude": "config"}),
    ".claude/settings.local.json": ("settings", {"claude": "config"}),
    "~/.claude/settings.json": ("settings", {"claude": "config"}),
    ".codex/config.toml": ("codex-config", {"codex": "conditional"}),
    ".codex/rules/default.rules": ("codex-rules", {"codex": "conditional"}),
    ".mcp.json": ("mcp-json", {"claude": "config"}),
    "~/.claude.json": ("claude-json-mcp", {"claude": "config"}),
    "~/.codex/config.toml": ("codex-config", {"codex": "config"}),
}
EXPECTED_OUT_OF_SCOPE = {".claude/skills": 1, ".claude/commands": 1, "enabledPlugins": 1}


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
            assert source.status == "in-scope", source.display
            assert source.sha256, source.display
            assert source.lines, source.display

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

    def test_claude_json_is_audited_as_its_mcp_subset_only(self) -> None:
        source = next(item for item in built().inventory.sources if item.kind == "claude-json-mcp")
        assert "numStartups" not in source.text
        assert "notes-server" in source.text
        assert "local-server" in source.text
        assert source.subset

    def test_own_enablement_entry_is_located(self) -> None:
        settings = next(
            item for item in built().inventory.sources if item.display == "~/.claude/settings.json"
        )
        assert claude_config.own_plugin_entries(settings) == [3]


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

    def test_the_own_enablement_entry_is_never_a_finding(self) -> None:
        for item in built().result.findings:
            assert "agent-context-audit@" not in item.excerpt, item.rationale


class HookPathTests(unittest.TestCase):
    def test_script_words_are_found_in_shell_commands(self) -> None:
        cases = {
            ".claude/hooks/check.sh": [".claude/hooks/check.sh"],
            '"$CLAUDE_PROJECT_DIR"/.claude/hooks/x.py --flag': [
                "$CLAUDE_PROJECT_DIR/.claude/hooks/x.py"
            ],
            "node ./scripts/a.mjs && echo done": ["./scripts/a.mjs"],
            "python3 ~/bin/t.py": ["~/bin/t.py"],
            "npx tsc --noEmit": [],
            'bash -c "echo $OTHER/x.sh"': [],
        }
        for command, expected in cases.items():
            assert config_checks.hook_scripts(command) == expected, command

    def test_paths_resolve_against_the_project_home_or_filesystem(self) -> None:
        repo, home = Path("/repo"), Path("/home/u")
        resolve = config_checks.resolve_hook_path
        assert resolve("${CLAUDE_PROJECT_DIR}/h/a.sh", repo, home) == (repo / "h/a.sh", False)
        assert resolve("~/bin/t.py", repo, home) == (home / "bin/t.py", False)
        assert resolve("/opt/hook.sh", repo, home) == (Path("/opt/hook.sh"), False)
        assert resolve("./scripts/a.mjs", repo, home) == (repo / "scripts/a.mjs", True)
