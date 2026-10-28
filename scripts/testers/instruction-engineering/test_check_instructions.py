#!/usr/bin/env python3
"""Tests for the claude-md-and-rules skill's checker in plugins/instruction-engineering.

Run: python3 -m unittest discover -s scripts/testers/instruction-engineering -v
Standard library only. Each case builds a project in a temporary folder and runs the checker
on it as a separate process with --no-user, so the maintainer's ~/.claude never takes part.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import cast
import unittest

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "plugins" / "instruction-engineering" / "skills" / "claude-md-and-rules"
CHECKER = SKILL / "scripts" / "check_instructions.py"


def scratch(case: unittest.TestCase) -> Path:
    """Create a temporary folder that is removed when the test ends."""
    root = Path(tempfile.mkdtemp()).resolve()
    case.addCleanup(shutil.rmtree, root)
    return root


def write(root: Path, files: dict[str, str]) -> None:
    """Write each relative path with its text, creating folders as needed."""
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")


def rule(paths_line: str, body: str = "Rule body.") -> str:
    """A rule file whose frontmatter is the given line."""
    return f"---\n{paths_line}\n---\n{body}\n"


def run(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the checker on a project with user scope skipped."""
    cmd = [sys.executable, "-I", str(CHECKER), "--project", str(project), "--no-user", *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)


class Result:
    """The checker's JSON output with typed accessors."""

    def __init__(self, proc: subprocess.CompletedProcess[str]) -> None:
        """Parse the JSON document the checker printed."""
        self.returncode: int = proc.returncode
        data = cast("object", json.loads(proc.stdout))
        if not isinstance(data, dict):
            msg = f"checker printed no JSON object: {proc.stdout[:200]}"
            raise TypeError(msg)
        self.data: dict[str, object] = cast("dict[str, object]", data)

    def findings(self) -> list[dict[str, object]]:
        """Every finding as a dictionary."""
        return cast("list[dict[str, object]]", self.data["findings"])

    def codes(self, path_suffix: str = "") -> set[str]:
        """Finding codes, optionally only for paths ending with path_suffix."""
        return {str(x["code"]) for x in self.findings() if str(x["path"]).endswith(path_suffix)}

    def finding(self, code: str, path_suffix: str = "") -> dict[str, object]:
        """The first finding with this code (and path suffix)."""
        for x in self.findings():
            if x["code"] == code and str(x["path"]).endswith(path_suffix):
                return x
        msg = f"no {code} finding for {path_suffix!r}: {self.codes()}"
        raise AssertionError(msg)

    def file(self, path_suffix: str) -> dict[str, object]:
        """The inventory row of a discovered file."""
        for f in cast("list[dict[str, object]]", self.data["files"]):
            if str(f["path"]).endswith(path_suffix):
                return f
        msg = f"{path_suffix} was not discovered"
        raise AssertionError(msg)


def check(project: Path, *args: str) -> Result:
    """Run the checker with --json and parse its output."""
    return Result(run(project, "--json", *args))


class FrontmatterTests(unittest.TestCase):
    """The strict subset parser: what YAML rejects and what it cannot interpret."""

    def codes_for(self, paths_line: str) -> set[str]:
        """Codes reported for one rule whose frontmatter is paths_line."""
        root = scratch(self)
        write(root, {".claude/rules/r.md": rule(paths_line), "src/a.ts": "x\n"})
        return check(root).codes(".claude/rules/r.md")

    def test_valid_forms_parse(self) -> None:
        """Block lists, flow lists, quoted scalars and comma lists are read as patterns."""
        for line in (
            'paths:\n  - "src/**/*.ts"',
            "paths: ['src/**'] # comment",
            'paths: "src/**/*.ts, docs/**"',
            "paths: 'it''s/**'",
            'paths: "src/\\ta"',
        ):
            with self.subTest(line=line):
                codes = self.codes_for(line)
                assert "frontmatter-invalid" not in codes
                assert "frontmatter-unchecked" not in codes

    def test_invalid_yaml_is_an_error(self) -> None:
        """Each of these makes Claude Code ignore the frontmatter."""
        for line in (
            "paths: *.ts",
            "paths: {a,b}",
            "paths: !tag x",
            "paths: src: x",
            "paths: [src/{a,b}/*.ts]",
            'paths: ["src/**"',
            'paths: ["src/**"] trailing',
            'paths: "src/**',
            "paths: 'src/**",
            'paths: "src/**" junk',
            'paths: "src/\\[x].ts"',
            'paths:\n\t- "src/**"',
            '- "src/**"',
            "this is not yaml",
            "  paths: x",
        ):
            with self.subTest(line=line):
                assert "frontmatter-invalid" in self.codes_for(line)

    def test_unsupported_yaml_is_a_warning(self) -> None:
        """Valid YAML the parser does not interpret is reported, not judged."""
        for line in ("paths: &anchor src/**", 'paths: "a"\npaths: "b"', "paths:\n  key: v"):
            with self.subTest(line=line):
                assert "frontmatter-unchecked" in self.codes_for(line)

    def test_unclosed_frontmatter(self) -> None:
        """An opening --- without a closing one is invalid."""
        root = scratch(self)
        write(root, {".claude/rules/r.md": '---\npaths: "x"\nno close\n'})
        assert "frontmatter-invalid" in check(root).codes("r.md")

    def test_block_scalar_then_paths(self) -> None:
        """A | block scalar ends at the next top-level key, which still parses."""
        root = scratch(self)
        text = '---\ndescription: |\n  some text\n  more\npaths: "src/**"\n---\nx\n'
        write(root, {".claude/rules/r.md": text, "src/a.ts": "x\n"})
        result = check(root)
        assert result.file("r.md")["paths"] == ["src/**"]
        assert result.finding("frontmatter-ignored-key", "r.md")["severity"] == "warning"

    def test_foreign_scoping_key_without_paths_is_an_error(self) -> None:
        """A Cursor-style key leaves the rule global when `paths` is missing."""
        root = scratch(self)
        write(root, {".claude/rules/r.md": rule("globs: src/**/*.ts")})
        assert check(root).finding("frontmatter-ignored-key")["severity"] == "error"

    def test_empty_paths(self) -> None:
        """`paths` with no pattern is an error."""
        root = scratch(self)
        write(root, {".claude/rules/r.md": rule("paths:")})
        assert "paths-empty" in check(root).codes()


class GlobTests(unittest.TestCase):
    """Pattern checks and the --match scope test."""

    def test_pattern_findings(self) -> None:
        """No match, root-only, leading slash, bad bracket and brace budget are reported."""
        root = scratch(self)

        def group(n: int) -> str:
            return "{" + ",".join(f"x{i}" for i in range(n)) + "}"

        write(
            root,
            {
                ".claude/rules/none.md": rule('paths: "lib/**"'),
                ".claude/rules/root.md": rule('paths: "*.ts"'),
                ".claude/rules/slash.md": rule('paths: "./src/**"'),
                ".claude/rules/bracket.md": rule("paths: 'src/[abc.ts'"),
                # 10 x 10 x 10 = 1,000 patterns, the budget; 7 x 11 x 13 = 1,001, one over it.
                ".claude/rules/at-budget.md": rule(f"paths: '{group(10)}/{group(10)}/{group(10)}'"),
                ".claude/rules/over-budget.md": rule(
                    f"paths: '{group(7)}/{group(11)}/{group(13)}'"
                ),
                "src/a.ts": "x\n",
                "top.ts": "x\n",
            },
        )
        result = check(root)
        assert result.finding("glob-no-match", "none.md")["severity"] == "warning"
        assert "glob-root-only" in result.codes("root.md")
        assert "glob-leading-slash" in result.codes("slash.md")
        assert "glob-invalid-bracket" in result.codes("bracket.md")
        assert "brace-budget" not in result.codes("at-budget.md")
        assert "brace-budget" in result.codes("over-budget.md")

    def test_match_lists_scoped_rules(self) -> None:
        """--match reports which scoped rules load for each file, nested rules included."""
        root = scratch(self)
        write(
            root,
            {
                ".claude/rules/api.md": rule('paths: "src/api/**"'),
                ".claude/rules/md.md": rule("paths: ['*.md', 'docs/**/*.{md,mdx}']"),
                "pkg/.claude/rules/go.md": rule('paths: "**/*.go"'),
                "src/api/v2/users.ts": "x\n",
                "README.md": "x\n",
                "docs/a/b.mdx": "x\n",
                "pkg/main.go": "x\n",
            },
        )
        files = ["src/api/v2/users.ts", "README.md", "docs/a/b.mdx", "pkg/main.go", "src/x.ts"]
        match = cast("dict[str, list[str]]", check(root, "--match", *files).data["match"])
        assert [Path(p).name for p in match["src/api/v2/users.ts"]] == ["api.md"]
        assert [Path(p).name for p in match["README.md"]] == ["md.md"]
        assert [Path(p).name for p in match["docs/a/b.mdx"]] == ["md.md"]
        assert [Path(p).name for p in match["pkg/main.go"]] == ["go.md"]
        assert match["src/x.ts"] == []

    def test_hostile_patterns_finish_quickly(self) -> None:
        """A brace bomb, a backtracking glob and a bad class are reported, not run for minutes.

        Each case once hung the checker or crashed it; the 10-second timeout fails the test.
        """
        cases = {
            "brace-budget": "{a,b}" * 26,  # 67 million expansions before the budget check
            "glob-no-match": "*a" * 25 + "b",  # catastrophic backtracking in a regex matcher
            "glob-invalid-bracket": "src/[z-a].ts",  # re.error: bad character range
        }
        for code, pattern in cases.items():
            with self.subTest(code=code):
                root = scratch(self)
                write(root, {".claude/rules/r.md": rule(f"paths: '{pattern}'"), "a" * 60: "x\n"})
                cmd = [sys.executable, "-I", str(CHECKER), "--project", str(root), "--no-user"]
                proc = subprocess.run(
                    [*cmd, "--json"], capture_output=True, text=True, check=False, timeout=10
                )
                assert "Traceback" not in proc.stderr, proc.stderr
                assert code in Result(proc).codes("r.md")

    def test_ancestor_rule_without_match_is_info_about_this_project(self) -> None:
        """A rule above the project is tested only against the project's files, and says so."""
        root = scratch(self)
        write(
            root,
            {
                ".claude/rules/mcp.md": rule('paths: "**/.mcp.json"'),
                "other/.mcp.json": "{}\n",
                "sub/src/a.ts": "x\n",
            },
        )
        found = check(root / "sub").finding("glob-no-match", "mcp.md")
        assert found["severity"] == "info"
        assert "of this project" in str(found["message"])
        assert "no file under" not in str(found["message"])


class DiscoveryTests(unittest.TestCase):
    """What the checker discovers and how it says each file loads."""

    def test_load_timing(self) -> None:
        """Root files load at launch, nested files on demand, scoped rules conditionally."""
        root = scratch(self)
        write(
            root,
            {
                "CLAUDE.md": "Root.\n",
                "docs/CLAUDE.md": "Nested.\n",
                ".claude/rules/always.md": "Always on.\n",
                ".claude/rules/scoped.md": rule('paths: "src/**"'),
                "pkg/.claude/rules/nested.md": "Nested rule.\n",
                "src/a.ts": "x\n",
            },
        )
        result = check(root)
        assert result.file("/CLAUDE.md")["loads"] == "launch"
        assert result.file("docs/CLAUDE.md")["loads"] == "on-demand"
        assert result.file("always.md")["loads"] == "launch"
        assert result.file("scoped.md")["loads"] == "conditional"
        assert result.file("nested.md")["loads"] == "on-demand"

    def test_agents_md(self) -> None:
        """AGENTS.md loads directly alone, and is shadowed by a CLAUDE.md."""
        alone = scratch(self)
        write(alone, {"AGENTS.md": "Agents.\n"})
        assert check(alone).file("AGENTS.md")["loads"] == "launch"
        shadowed = scratch(self)
        write(shadowed, {"AGENTS.md": "Agents.\n", "CLAUDE.md": "Claude.\n"})
        result = check(shadowed)
        assert result.file("AGENTS.md")["loads"] == "not-by-default"
        assert "agents-md-shadowed" in result.codes("AGENTS.md")

    def test_backup_in_rules_and_symlinked_rule(self) -> None:
        """A backup under rules loads; a symlink out of the project is noted."""
        root = scratch(self)
        write(root, {"proj/.claude/rules/old/legacy.md": "Old.\n", "shared/s.md": "Shared.\n"})
        (root / "proj/.claude/rules/linked.md").symlink_to(root / "shared/s.md")
        result = check(root / "proj")
        assert "rule-backup-loaded" in result.codes("legacy.md")
        assert "rule-symlink-external" in result.codes("linked.md")

    def test_launch_count_includes_imports(self) -> None:
        """Imported lines count toward the launch set; missing imports are errors."""
        root = scratch(self)
        write(
            root,
            {
                "CLAUDE.md": "Root.\n@docs/guide.md and @missing/file.md\n",
                "docs/guide.md": "one\ntwo\nthree\n",
            },
        )
        result = check(root)
        launch = cast("dict[str, int]", result.data["launch_set"])
        assert launch["lines_including_imports"] == 5
        assert "import-missing" in result.codes("CLAUDE.md")


HEURISTIC_LINES = [
    "# Project",
    "",
    "IMPORTANT: ALWAYS run tests. NEVER skip. MUST lint!!",
    "Think step by step before editing.",
    "Write clean, maintainable code following best practices.",
    "Never edit generated files.",
    "Use 2 spaces for indentation.",
    "As of 2026-01 the team moved.",
    "Pin react to 18.2.0 because the API differs.",
    "Use jest for unit tests.",
    "Run vitest for component tests.",
    "",
    "## Release steps",
    "",
    *[f"{n}. step" for n in range(1, 6)],
    "",
    "## src/api conventions",
    "",
    "- one",
    "- two",
    "- three",
]
TREE = "\n├── src\n├── docs\n└── pkg\n"


class ContentTests(unittest.TestCase):
    """Package scripts and the wording, duplicate and placement heuristics."""

    def test_package_scripts(self) -> None:
        """Missing scripts are errors; npm without run is a warning; local binaries pass."""
        root = scratch(self)
        write(
            root,
            {
                "package.json": '{"scripts": {"build": "x"}}',
                "node_modules/.bin/eslint": "",
                "CLAUDE.md": "Run `npm run build`, `npm run gone`, `npm lint` and `yarn eslint`.\n",
            },
        )
        result = check(root)
        assert result.returncode == 1
        missing = [x for x in result.findings() if x["code"] == "script-missing"]
        assert len(missing) == 1
        assert "gone" in str(missing[0]["message"])
        assert "npm-needs-run" in result.codes()
        assert "command-unverified" not in result.codes()

    def test_package_json_not_utf8_does_not_crash(self) -> None:
        """An unreadable package.json is skipped instead of ending the run with a traceback."""
        root = scratch(self)
        write(root, {"CLAUDE.md": "Run `npm run x`.\n"})
        _ = (root / "package.json").write_bytes(b"\xff\xfe{}")
        proc = run(root)
        assert proc.returncode == 0, proc.stderr
        assert "Traceback" not in proc.stderr

    def test_heuristics(self) -> None:
        """Each heuristic flags its pattern in an always-on CLAUDE.md."""
        root = scratch(self)
        table = "| Column one       | Column two         |\n| ---------------- | ------------- |\n"
        write(
            root,
            {
                ".editorconfig": "root = true\n",
                "src/api/v2/users.ts": "x\n",
                "CLAUDE.md": "\n".join(HEURISTIC_LINES) + "\n\n" + table * 8 + TREE,
            },
        )
        codes = check(root).codes("CLAUDE.md")
        for code in (
            "emphasis",
            "reasoning-nudge",
            "no-op-candidate",
            "negative-only",
            "formatter-enforced",
            "time-sensitive",
            "exact-version",
            "conflicting-choice",
            "procedure-candidate",
            "scope-candidate",
            "table-padding",
            "discoverable-layout",
        ):
            with self.subTest(code=code):
                assert code in codes

    def test_duplicates_across_files(self) -> None:
        """Identical lines, near-duplicates and identical files are reported."""
        root = scratch(self)
        line = "Use pytest for tests and keep the suite fast and deterministic everywhere."
        near = "Use pytest for tests and keep the suite quick and deterministic everywhere."
        write(
            root,
            {
                "CLAUDE.md": f"{line}\n{near}\n",
                "CLAUDE.local.md": f"{line}\n",
                ".claude/CLAUDE.md": f"{line}\n",
            },
        )
        codes = check(root).codes()
        assert {"duplicate-line", "near-duplicate", "duplicate-file"} <= codes

    def test_local_file_must_be_ignored(self) -> None:
        """CLAUDE.local.md in a git repository without an ignore entry is a warning."""
        git = shutil.which("git")
        if git is None:
            msg = "git is required for this test"
            raise AssertionError(msg)
        root = scratch(self)
        write(root, {"CLAUDE.local.md": "Personal.\n"})
        _ = subprocess.run([git, "init", "-q"], cwd=root, check=True)
        assert "local-not-ignored" in check(root).codes()
        write(root, {".gitignore": "CLAUDE.local.md\n"})
        assert "local-not-ignored" not in check(root).codes()


class OutputTests(unittest.TestCase):
    """Exit codes, the text report and the references it points to."""

    def test_exit_codes(self) -> None:
        """0 without errors, 1 with an error, 2 for bad arguments."""
        root = scratch(self)
        write(root, {"CLAUDE.md": "Fine.\n"})
        assert run(root).returncode == 0
        write(root, {".claude/rules/r.md": rule("paths: *.ts")})
        assert run(root).returncode == 1
        assert run(root, "--bogus").returncode == 2
        assert run(root / "missing").returncode == 2

    def test_runs_by_path(self) -> None:
        """The script runs through its own shebang, as the skill documents."""
        assert os.access(CHECKER, os.X_OK), "check_instructions.py is not executable"
        root = scratch(self)
        write(root, {"CLAUDE.md": "Fine.\n"})
        proc = subprocess.run(
            [str(CHECKER), "--project", str(root), "--no-user"],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
        assert "Findings: none" in proc.stdout

    def test_text_report_points_to_existing_references(self) -> None:
        """Every reference the report asks the reader to open exists in the skill."""
        root = scratch(self)
        write(root, {"CLAUDE.md": "Never edit generated files.\n1. a\n2. b\n3. c\n4. d\n5. e\n"})
        result = check(root)
        refs = cast("list[dict[str, object]]", result.data["read_before_reporting"])
        assert refs
        for ref in refs:
            path = Path(str(ref["reference"]))
            with self.subTest(reference=path.name):
                assert path.is_file()
                assert path.parent == SKILL / "references"
        assert "Read before reporting" in run(root).stdout


if __name__ == "__main__":
    _ = unittest.main()
