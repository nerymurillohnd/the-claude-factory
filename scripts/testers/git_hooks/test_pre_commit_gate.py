#!/usr/bin/env python3
"""Tests for the Git pre-commit gate and the installer that turns it on.

Each test stages files in a local clone of this repository, which shares its node_modules and .venv
through symlinks, then runs the gate from the working tree the way Git runs .githooks/pre-commit.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import ClassVar, final, override
import unittest

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "scripts" / "validators" / "pre-commit-gate.sh"
INSTALLER = ROOT / "scripts" / "install-git-hooks.sh"
HOOK = ROOT / ".githooks" / "pre-commit"

CLEAN_PY = (
    '"""A clean module."""\n\n\n'
    "def double(value: int) -> int:\n"
    '    """Return twice value."""\n'
    "    return value * 2\n"
)
CLEAN_SH = '#!/usr/bin/env bash\nset -euo pipefail\nprintf "%s\\n" "hi"\n'
CLEAN_MJS = "/** @param {number} value */\nexport const double = (value) => value * 2\n"
PROBE_PY = "scripts/validators/gate_probe.py"
# A stand-in for the tsconfig.json Claude Code writes at a mod's root (git-ignored).
MOD_TSCONFIG = '{"extends": "../../tsconfig.base.json", "compilerOptions": {"types": []}}\n'
PADDED_TABLE = "# Probe\n\n| A   | B |\n| :-- | :-- |\n| 1   | 2 |\n"

type Result = subprocess.CompletedProcess[str]


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> Result:
    """Run a command and capture its output as text."""
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, check=False)


@final
class Sandbox:
    """A local clone of the repository whose index the tests stage into."""

    def __init__(self) -> None:
        """Clone the repository and share its installed node_modules and .venv."""
        self.tmp: Path = Path(tempfile.mkdtemp(prefix="pre-commit-gate-"))
        self.repo: Path = self.tmp / "repo"
        _ = run(["git", "clone", "--quiet", "--local", str(ROOT), str(self.repo)], cwd=self.tmp)
        for shared in ("node_modules", ".venv"):
            (self.repo / shared).symlink_to(ROOT / shared)

    def write(self, rel: str, text: str) -> None:
        """Write a file in the clone, creating its folders."""
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")

    def stage(self, rel: str, text: str) -> None:
        """Write a file in the clone and stage it."""
        self.write(rel, text)
        _ = run(["git", "add", "--", rel], cwd=self.repo)

    def gate(self, env: dict[str, str] | None = None) -> Result:
        """Run the gate from the clone's root, as Git runs a hook."""
        return run(["bash", str(GATE)], cwd=self.repo, env=env)

    def reset(self) -> None:
        """Drop every staged and unstaged change and every untracked file."""
        _ = run(["git", "reset", "--quiet", "--hard"], cwd=self.repo)
        _ = run(["git", "clean", "-fdqx", "-e", "node_modules", "-e", ".venv"], cwd=self.repo)

    def remove(self) -> None:
        """Delete the clone."""
        shutil.rmtree(self.tmp, ignore_errors=True)


class PreCommitGateTest(unittest.TestCase):
    """The gate checks only the staged files of each covered type, with the project's tools."""

    box: ClassVar[Sandbox]

    @classmethod
    @override
    def setUpClass(cls) -> None:
        """Clone once for the whole class: a clone takes seconds."""
        cls.box = Sandbox()

    @classmethod
    @override
    def tearDownClass(cls) -> None:
        """Delete the clone."""
        cls.box.remove()

    @override
    def setUp(self) -> None:
        """Start each test from a clean index and work tree."""
        self.box.reset()

    def assert_blocks(self, result: Result, tool: str) -> None:
        """The gate failed, and its report names the tool that found the problem."""
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(f"pre-commit: {tool} failed", output)

    def assert_passes(self, result: Result) -> None:
        """The gate passed."""
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nothing_staged_passes(self) -> None:
        """With nothing staged there is nothing to check."""
        self.assert_passes(self.box.gate())

    def test_clean_files_pass(self) -> None:
        """Clean Python, shell and JavaScript files pass every tool."""
        self.box.stage(PROBE_PY, CLEAN_PY)
        self.box.stage("scripts/gate-probe.sh", CLEAN_SH)
        self.box.stage("scripts/gate-probe.mjs", CLEAN_MJS)
        self.assert_passes(self.box.gate())

    def test_ruff_lint_blocks(self) -> None:
        """A Ruff lint finding blocks the commit."""
        self.box.stage(PROBE_PY, CLEAN_PY + "import os\n")
        self.assert_blocks(self.box.gate(), "ruff check")

    def test_ruff_format_blocks(self) -> None:
        """A Python file Ruff would reformat blocks the commit."""
        self.box.stage(PROBE_PY, CLEAN_PY.replace("value * 2", "value*2"))
        result = self.box.gate()
        self.assert_blocks(result, "ruff format")
        self.assertIn("+    return value * 2", result.stdout, "the diff shows the fix")

    def test_basedpyright_blocks(self) -> None:
        """A type error blocks the commit."""
        broken = CLEAN_PY.replace("return value * 2", 'return value + "x"')
        self.box.stage(PROBE_PY, broken)
        self.assert_blocks(self.box.gate(), "basedpyright")

    def test_basedpyright_checks_plugins_at_the_312_floor(self) -> None:
        """A plugin file that calls a 3.13 stdlib API fails: plugins run on Python 3.12."""
        probe = "plugins/macos-grep-guard/hooks/gate_probe.py"
        self.box.stage(
            probe, '"""Probe."""\n\nfrom warnings import deprecated\n\n__all__ = ["deprecated"]\n'
        )
        self.assert_blocks(self.box.gate(), "basedpyright")

    def test_basedpyright_checks_stub_files(self) -> None:
        """A .pyi stub is type-checked too."""
        self.box.stage(
            "scripts/validators/gate_probe.pyi", "def double(value: Undefined) -> int: ...\n"
        )
        self.assert_blocks(self.box.gate(), "basedpyright")

    def test_shfmt_blocks(self) -> None:
        """A shell script shfmt would reformat blocks the commit."""
        self.box.stage("scripts/gate-probe.sh", CLEAN_SH.replace("printf ", "printf  "))
        self.assert_blocks(self.box.gate(), "shfmt")

    def test_shellcheck_blocks(self) -> None:
        """A ShellCheck finding blocks the commit."""
        self.box.stage("scripts/gate-probe.sh", CLEAN_SH + "echo $UNQUOTED\n")
        self.assert_blocks(self.box.gate(), "shellcheck")

    def test_extensionless_shell_script_is_checked(self) -> None:
        """A shell script found by its shebang, like a Git hook, is checked as shfmt -f finds it."""
        self.box.stage(".githooks/gate-probe", CLEAN_SH + "echo $UNQUOTED\n")
        self.assert_blocks(self.box.gate(), "shellcheck")

    def test_extensionless_text_file_is_skipped(self) -> None:
        """A file with no extension and no shell shebang is not a shell script."""
        self.box.stage("docs/GATE-PROBE", "Plain text, not a script: $UNQUOTED\n")
        self.assert_passes(self.box.gate())

    def test_suppression_blocks(self) -> None:
        """A staged file that silences a check blocks the commit, even when every tool passes."""
        self.box.stage("scripts/gate-probe.mjs", "// @ts-nocheck\n" + CLEAN_MJS)
        self.assert_blocks(self.box.gate(), "suppressions")

    def test_cast_blocks(self) -> None:
        """A typing.cast call is a suppression of the type checker."""
        source = CLEAN_PY + "\n\nfrom typing import cast\n\nVALUE = cast('int', 1)\n"
        self.box.stage(PROBE_PY, source)
        self.assert_blocks(self.box.gate(), "suppressions")

    def test_shellcheck_reads_shellcheck_opts(self) -> None:
        """SHELLCHECK_OPTS reaches ShellCheck: its options change what the gate reports."""
        self.box.stage("scripts/gate-probe.sh", CLEAN_SH + "echo $UNQUOTED\n")
        self.assert_blocks(self.box.gate(), "shellcheck")
        opts = {**os.environ, "SHELLCHECK_OPTS": "--exclude=SC2086,SC2154,SC2250"}
        self.assert_passes(self.box.gate(opts))

    def test_biome_blocks_javascript(self) -> None:
        """A Biome finding in a .mjs file blocks the commit."""
        self.box.stage("scripts/gate-probe.mjs", CLEAN_MJS + "var unused = 1\n")
        self.assert_blocks(self.box.gate(), "biome")

    def test_biome_blocks_json(self) -> None:
        """A JSON file Biome would reformat blocks the commit."""
        self.box.stage("scripts/gate-probe.json", '{"a":1,\n  "b":2}\n')
        self.assert_blocks(self.box.gate(), "biome")

    def test_biome_blocks_markdown(self) -> None:
        """A Markdown file Biome would reformat blocks the commit."""
        self.box.stage("docs/gate-probe.md", PADDED_TABLE)
        self.assert_blocks(self.box.gate(), "biome")

    def test_markdown_goes_to_biome_only(self) -> None:
        """Biome owns Markdown: a .md file with a Python block Ruff would reformat skips Ruff."""
        self.box.stage("docs/gate-probe.md", "# Probe\n\n```python\nx=1\n```\n")
        result = self.box.gate()
        self.assert_passes(result)
        self.assertIn("== pre-commit: biome", result.stdout)
        self.assertNotIn("== pre-commit: ruff", result.stdout)

    def test_instruction_markdown_is_not_formatted(self) -> None:
        """Biome's override keeps instruction Markdown out of formatting, so padding passes."""
        self.box.stage(".claude/rules/gate-probe.md", PADDED_TABLE)
        self.assert_passes(self.box.gate())

    def test_tsc_blocks(self) -> None:
        """A type error in a .mjs file the root tsconfig covers blocks the commit."""
        broken = CLEAN_MJS + "export const bad = double.missing.value\n"
        self.box.stage("scripts/gate-probe.mjs", broken)
        self.assert_blocks(self.box.gate(), "tsc")

    def test_mod_typescript_without_tsconfig_blocks(self) -> None:
        """A mod's .ts file with no generated tsconfig can't be type-checked, so it blocks."""
        probe = "plugins/macos-grep-guard/hooks/gate-probe.ts"
        self.box.stage(probe, "export const one = 1\n")
        result = self.box.gate()
        self.assert_blocks(result, "tsc")
        self.assertIn("not type-checked", result.stdout + result.stderr)
        self.assertIn(probe, result.stdout + result.stderr)

    def test_mod_typescript_uses_its_tsconfig(self) -> None:
        """With the mod's tsconfig.json in place, tsc checks the staged .ts file through it."""
        mod = "plugins/macos-grep-guard"
        self.box.write(f"{mod}/tsconfig.json", MOD_TSCONFIG)
        probe = f"{mod}/hooks/gate-probe.ts"
        self.box.stage(probe, "export const one: number = 1\n")
        self.assert_passes(self.box.gate())
        self.box.stage(probe, 'export const one: number = "one"\n')
        self.assert_blocks(self.box.gate(), "tsc")

    def test_mod_tsx_uses_its_tsconfig(self) -> None:
        """A mod's .tsx file is formatted, linted and type-checked like a .ts file."""
        mod = "plugins/macos-grep-guard"
        self.box.write(f"{mod}/tsconfig.json", MOD_TSCONFIG)
        probe = f"{mod}/hooks/gate-probe.tsx"
        self.box.stage(probe, "export const one: number = 1\n")
        self.assert_passes(self.box.gate())
        self.box.stage(probe, 'export const one: number = "one"\n')
        self.assert_blocks(self.box.gate(), "tsc")
        self.box.stage(probe, "export const one: number = 1;;\n")
        self.assert_blocks(self.box.gate(), "biome")

    def test_only_staged_files_are_checked(self) -> None:
        """A broken file that is not staged does not block the commit."""
        self.box.write("scripts/validators/gate_broken.py", "import os\n")
        self.box.stage(PROBE_PY, CLEAN_PY)
        self.assert_passes(self.box.gate())

    def test_uncovered_types_are_skipped(self) -> None:
        """A staged file of a type the gate doesn't cover is not checked."""
        self.box.stage("docs/gate-probe.yml", "a:   [1,2]\n")
        self.assert_passes(self.box.gate())

    def test_deleted_files_are_skipped(self) -> None:
        """A staged deletion has no content to check."""
        _ = run(["git", "rm", "--quiet", "scripts/validators/pr-checks.sh"], cwd=self.box.repo)
        self.assert_passes(self.box.gate())

    def test_partially_staged_file_blocks(self) -> None:
        """A staged file with unstaged edits is refused: the tools would read the wrong text."""
        self.box.stage(PROBE_PY, CLEAN_PY)
        self.box.write(PROBE_PY, CLEAN_PY + "# later\n")
        result = self.box.gate()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("unstaged changes", output)
        self.assertIn(PROBE_PY, output)

    def test_missing_tool_blocks(self) -> None:
        """A tool the gate needs but can't find blocks the commit instead of skipping its check."""
        self.box.stage("scripts/gate-probe.sh", CLEAN_SH)
        bare = Path(tempfile.mkdtemp(prefix="bare-path-"))
        try:
            for tool in ("git", "bash", "env", "mkdir", "rm", "grep"):
                found = shutil.which(tool)
                if found:
                    (bare / tool).symlink_to(found)
            result = self.box.gate({**os.environ, "PATH": str(bare)})
        finally:
            shutil.rmtree(bare, ignore_errors=True)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("not installed", output)

    def test_hook_runs_the_gate_on_commit(self) -> None:
        """Once installed, git commit runs the gate and refuses a broken file."""
        repo = self.box.repo
        (repo / ".githooks").mkdir(exist_ok=True)
        _ = shutil.copy2(HOOK, repo / ".githooks" / "pre-commit")
        _ = shutil.copy2(GATE, repo / "scripts" / "validators" / "pre-commit-gate.sh")
        _ = run(["bash", str(INSTALLER)], cwd=repo)
        self.box.stage(PROBE_PY, CLEAN_PY + "import os\n")
        identity = ["-c", "user.name=Probe", "-c", "user.email=probe@example.invalid"]
        result = run(["git", *identity, "commit", "--quiet", "-m", "probe"], cwd=repo)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("pre-commit: ruff check failed", output)


class InstallerTest(unittest.TestCase):
    """The prepare script points Git at .githooks, and does nothing outside a work tree."""

    def test_sets_hooks_path(self) -> None:
        """Inside a work tree it sets core.hooksPath to .githooks."""
        with tempfile.TemporaryDirectory() as tmp:
            _ = run(["git", "init", "--quiet", tmp], cwd=Path(tmp))
            result = run(["bash", str(INSTALLER)], cwd=Path(tmp))
            self.assertEqual(result.returncode, 0, result.stderr)
            value = run(["git", "config", "--get", "core.hooksPath"], cwd=Path(tmp))
            self.assertEqual(value.stdout.strip(), ".githooks")

    def test_outside_work_tree_is_a_no_op(self) -> None:
        """Outside a Git work tree it exits 0 and changes nothing, so npm ci never fails on it."""
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(Path(tmp).parent)}
            result = run(["bash", str(INSTALLER)], cwd=Path(tmp), env=env)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
