"""Unit tests for agent-context-audit's parsers: Markdown, JSON spans, TOML, globs, redaction, IDs.

Run: python3 -m unittest discover -s .github/scripts/tests/agent-context-audit -v
Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

from pathlib import Path
import unittest

import _aca_support
from aca import globmatch, jsonpos, markdown, redact, tomlish, units

SAMPLE = """\
---
paths:
  - "src/**/*.ts"
description: Style rules
---

# Title

Intro paragraph line one
continues here.

- item one
- item two
  continued

| a | b |
| - | - |
| 1 | 2 |

```bash
@not/an/import.md
npm test
```

<!-- a comment
spanning two lines -->

See @docs/a.md and `@code/b.md`, or write to me@example.com.
"""


LINES = markdown.split_lines(SAMPLE)


class PackageTests(unittest.TestCase):
    def test_the_tests_import_the_plugins_own_package(self) -> None:
        assert Path(markdown.__file__).resolve().parent.parent == _aca_support.SCRIPTS


class MarkdownTests(unittest.TestCase):
    def test_split_lines_counts_like_a_line_numbered_reader(self) -> None:
        assert len(LINES) == SAMPLE.count("\n")
        assert markdown.split_lines("") == []
        assert markdown.split_lines("a\nb") == ["a", "b"]

    def test_units_cover_each_block_with_its_lines(self) -> None:
        found = [(unit.start, unit.end, unit.kind) for unit in markdown.units(LINES)]
        assert found == [
            (1, 5, "frontmatter"),
            (9, 10, "paragraph"),
            (12, 12, "item"),
            (13, 14, "item"),
            (16, 16, "table-row"),
            (17, 17, "table-row"),
            (18, 18, "table-row"),
            (20, 23, "code"),
            (25, 26, "comment"),
            (28, 28, "paragraph"),
        ]
        assert markdown.units(LINES)[1].heading == "Title"

    def test_imports_skip_code_spans_fences_and_emails(self) -> None:
        found = markdown.imports(LINES)
        assert [(ref.line, ref.target) for ref in found] == [(28, "docs/a.md")]

    def test_block_comments_are_found(self) -> None:
        assert [unit.start for unit in markdown.block_comments(LINES)] == [25]

    def test_frontmatter_parses_lists_and_scalars(self) -> None:
        front = markdown.find_frontmatter(LINES)
        assert front is not None
        assert (front.start, front.end, front.error) == (1, 5, "")
        assert front.data == {"paths": ["src/**/*.ts"], "description": "Style rules"}

    def test_strict_yaml_rejects_a_colon_space_in_a_plain_value(self) -> None:
        data, error = markdown.parse_yaml(["description: runs: fast"])
        assert data == {}
        assert "mapping values are not allowed" in error

    def test_strict_yaml_reports_a_line_without_a_key(self) -> None:
        _data, error = markdown.parse_yaml(["name: x", "no key here"])
        assert "line" in error

    def test_normalize_ignores_list_markers_and_reflow(self) -> None:
        assert markdown.normalize("- Prefer   short\n  answers.") == markdown.normalize(
            "* Prefer short answers."
        )


class JsonSpanTests(unittest.TestCase):
    def test_members_and_items_keep_their_lines(self) -> None:
        node, error = jsonpos.parse('{\n  "a": 1,\n  "b": [\n    "x",\n    "y"\n  ]\n}')
        assert error == ""
        assert node is not None
        assert (node.start, node.end) == (1, 7)
        assert (node.members["a"].start, node.members["a"].end) == (2, 2)
        assert (node.members["b"].start, node.members["b"].end) == (3, 6)
        assert [(item.start, item.end) for item in node.members["b"].items] == [(4, 4), (5, 5)]

    def test_invalid_json_returns_the_error(self) -> None:
        node, error = jsonpos.parse('{"a": 1,}')
        assert node is None
        assert "line 1" in error


class TomlTests(unittest.TestCase):
    def test_entries_track_tables_quoted_keys_and_multiline_values(self) -> None:
        lines = [
            'model = "x"',
            "[features]",
            "web_search = true",
            '[profiles."my profile"]',
            'model = "y"',
            "args = [",
            '  "a",',
            "]",
            "oops",
        ]
        found, unreadable = tomlish.entries(lines)
        assert [(entry.path, entry.value, entry.start, entry.end) for entry in found] == [
            ("model", "x", 1, 1),
            ("features.web_search", True, 3, 3),
            ("profiles.my profile.model", "y", 5, 5),
            ("profiles.my profile.args", ["a"], 6, 8),
        ]
        assert unreadable == ["line 9: oops"]

    def test_decode_keeps_non_string_arrays_as_text(self) -> None:
        assert tomlish.decode("[1, 2]") == "[1, 2]"
        assert tomlish.decode("[ ]") == []
        assert tomlish.decode("1_000") == 1000

    def test_validate_uses_tomllib_when_available(self) -> None:
        verdict = tomlish.validate("a = 1")
        if verdict is None:
            self.skipTest("tomllib needs Python 3.11+")
        assert verdict == ""
        assert tomlish.validate("a = ")

    def test_starlark_calls_balance_parentheses(self) -> None:
        lines = [
            "prefix_rule(",
            '  pattern = ["git", "push"],',
            '  decision = "forbidden",',
            ")",
            "",
            'prefix_rule(pattern=["ls"])',
        ]
        assert [(start, end) for start, end, _text in tomlish.starlark_calls(lines)] == [
            (1, 4),
            (6, 6),
        ]


class GlobTests(unittest.TestCase):
    def test_double_star_spans_zero_or_more_folders(self) -> None:
        assert globmatch.matches("src/**/*.ts", "src/a/b.ts")
        assert globmatch.matches("src/**/*.ts", "src/b.ts")
        assert not globmatch.matches("src/*.ts", "src/a/b.ts")

    def test_braces_expand(self) -> None:
        assert globmatch.matches("*.{ts,tsx}", "a.tsx")
        assert not globmatch.matches("*.{ts,tsx}", "a.js")

    def test_count_matches_stops_at_the_limit(self) -> None:
        names = [f"src/{index}.ts" for index in range(10)]
        assert globmatch.count_matches(["src/*.ts"], names, limit=3) == 3


class RedactionTests(unittest.TestCase):
    def test_secret_shapes_are_masked(self) -> None:
        cases = {
            'token = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz0123"': "abcdefghijklmnop",
            "https://user:pass@example.com/x": "user:pass",
            "https://x.com/?token=abcd1234efgh": "abcd1234efgh",
            '"apiKey": "abcdef123456"': "abcdef123456",
            "API_KEY=supersecretvalue123": "supersecretvalue123",
            "ghp_abcdefghijklmnopqrstuvwxyz0123456789": "ghp_",
            "Authorization: Bearer abcdefghijklmnop1234": "abcdefghijklmnop1234",
        }
        for line, secret in cases.items():
            with self.subTest(line=line):
                masked = redact.redact_line(line)
                assert secret not in masked
                assert redact.MASK in masked

    def test_words_and_placeholders_are_kept(self) -> None:
        for line in ("feat/task-cleanup-inventory", "API_KEY=${API_KEY}", "Run npm test."):
            with self.subTest(line=line):
                assert redact.redact_line(line) == line

    def test_private_key_blocks_keep_the_line_count(self) -> None:
        lines = ["a", "-----BEGIN PRIVATE KEY-----", "MIIabc", "-----END PRIVATE KEY-----", "b"]
        masked = redact.redact_lines(lines)
        assert len(masked) == len(lines)
        assert "MIIabc" not in "\n".join(masked)
        assert (masked[0], masked[-1]) == ("a", "b")

    def test_nested_values_are_masked(self) -> None:
        value = {"list": ["API_KEY=supersecretvalue123"], "n": 1}
        assert "supersecretvalue123" not in str(redact.redact_value(value))


class UnitIdTests(unittest.TestCase):
    def test_ids_are_stable_and_numbered_on_repeats(self) -> None:
        lines = ["# Rules", "", "- Use tabs.", "", "- Use tabs.", "", "- Use spaces."]
        found = markdown.units(lines)
        first = units.unit_ids("CLAUDE.md", found)
        assert first == units.unit_ids("CLAUDE.md", markdown.units(lines))
        assert len(set(first)) == len(first)
        assert first != units.unit_ids("AGENTS.md", found)

    def test_reflowing_a_unit_keeps_its_id(self) -> None:
        before = units.unit_ids("CLAUDE.md", markdown.units(["Prefer short", "answers."]))
        after = units.unit_ids("CLAUDE.md", markdown.units(["Prefer short answers."]))
        assert before == after

    def test_json_units_split_settings_rules_and_hooks(self) -> None:
        text = '{\n  "model": "x",\n  "permissions": {\n    "allow": [\n      "Read"\n    ]\n  }\n}'
        found = units.json_units(markdown.split_lines(text))
        assert any(unit.start == 2 for unit in found)
        assert any(unit.start == 5 and unit.end == 5 for unit in found)
