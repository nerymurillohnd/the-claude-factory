#!/usr/bin/env python3
"""Tests for check_instructions.py: how a rule's `paths` patterns match files.

The cases follow the pattern table of https://code.claude.com/docs/en/memory ("Path-specific
rules"): a pattern with no '/' matches at any depth, a leading '/' anchors it to the base
directory, and a pattern with a '/' inside it is relative to the base. Each test runs the checker
as a user would, on a throwaway project, with only the standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, TypeGuard, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "cc-md-and-rules"
    / "scripts"
    / "check_instructions.py"
)


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded JSON value to an array."""
    return isinstance(value, list)


def run(project: Path, patterns: list[str], targets: list[str]) -> JsonObject:
    """Write one rule with these patterns, run the checker with --match, return its JSON."""
    rules = project / ".claude" / "rules"
    rules.mkdir(parents=True, exist_ok=True)
    listed = "".join(f'  - "{p}"\n' for p in patterns)
    _ = (rules / "r.md").write_text(f"---\npaths:\n{listed}---\n\n# R\n\n- Rule.\n", "utf-8")
    args = [str(SCRIPT), "--project", str(project), "--no-user", "--json", "--match", *targets]
    done = subprocess.run([sys.executable, *args], capture_output=True, text=True, check=False)
    data = parse_json(done.stdout)
    if not isinstance(data, JsonObject):
        msg = f"the checker printed no JSON object: {done.stderr}"
        raise TypeError(msg)
    return data


def loads_for(data: JsonObject, target: str) -> bool:
    """True when the rule loads for the target file."""
    match = data.get("match")
    return isinstance(match, JsonObject) and bool(match.get(target))


def finding_codes(data: JsonObject) -> list[str]:
    """The codes of the checker's findings."""
    found = data.get("findings")
    items = found if is_list(found) else []
    return [str(f.get("code")) for f in items if isinstance(f, JsonObject)]


class PathPatternTest(unittest.TestCase):
    """The patterns of the docs' table, matched as Claude Code documents them."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway project each test builds; setUp fills it, tearDown removes it."""
        super().__init__(method_name)
        self.project: Path = Path()

    @override
    def setUp(self) -> None:
        """A root package.json, a nested one, and Markdown at two depths."""
        self.project = Path(tempfile.mkdtemp())
        for rel in ("package.json", "sub/package.json", "README.md", "docs/guide.md"):
            path = self.project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text("x\n", "utf-8")

    @override
    def tearDown(self) -> None:
        """Remove the throwaway project."""
        shutil.rmtree(self.project)

    def test_leading_slash_anchors_the_pattern_to_the_base(self) -> None:
        """'/package.json' loads for the root file only, with no no-match or prefix finding."""
        data = run(self.project, ["/package.json"], ["package.json", "sub/package.json"])
        loaded = (loads_for(data, "package.json"), loads_for(data, "sub/package.json"))
        self.assertEqual(loaded, (True, False))
        self.assertNotIn("glob-no-match", finding_codes(data))
        self.assertNotIn("glob-leading-slash", finding_codes(data))

    def test_pattern_without_a_slash_matches_at_any_depth(self) -> None:
        """'*.md' loads for Markdown at the root and in subfolders."""
        data = run(self.project, ["*.md"], ["README.md", "docs/guide.md"])
        loaded = (loads_for(data, "README.md"), loads_for(data, "docs/guide.md"))
        self.assertEqual(loaded, (True, True))

    def test_slash_inside_the_pattern_keeps_it_relative_to_the_base(self) -> None:
        """'docs/*.md' loads for docs/guide.md only, not for a deeper docs folder."""
        nested = self.project / "pkg" / "docs" / "a.md"
        nested.parent.mkdir(parents=True)
        _ = nested.write_text("x\n", "utf-8")
        data = run(self.project, ["docs/*.md"], ["docs/guide.md", "pkg/docs/a.md"])
        loaded = (loads_for(data, "docs/guide.md"), loads_for(data, "pkg/docs/a.md"))
        self.assertEqual(loaded, (True, False))

    def test_anchored_pattern_with_no_root_file_is_reported(self) -> None:
        """'/missing.json' matches nothing, so the checker still says the rule never loads."""
        data = run(self.project, ["/missing.json"], ["package.json"])
        self.assertIn("glob-no-match", finding_codes(data))

    def test_checked_against_names_the_reference_version(self) -> None:
        """The JSON names the Claude Code version in the loading reference's recheck line."""
        reference = SCRIPT.parents[1] / "references" / "loading-semantics.md"
        line = next(
            ln for ln in reference.read_text("utf-8").splitlines() if ln.startswith("Checked with")
        )
        version = line.split()[4]
        data = run(self.project, ["*.md"], ["README.md"])
        expected = f"Claude Code {version}, as references/loading-semantics.md records"
        self.assertEqual(data.get("checked_against"), expected)


if __name__ == "__main__":
    _ = unittest.main()
