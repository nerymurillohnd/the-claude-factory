#!/usr/bin/env python3
"""Tests for plugin-engineering's hooks/validate-plugin.sh, run with a stub claude binary."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import NamedTuple
import unittest

# The stub claude logs its arguments, one call per line. For `claude plugin <sub> …` it prints
# STUB_OUT_<sub> and exits with STUB_EXIT_<sub> (0 by default), with <sub> validate or test.
STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "${STUB_LOG}"
out_var="STUB_OUT_$2"
code_var="STUB_EXIT_$2"
printf '%s' "${!out_var:-}"
exit "${!code_var:-0}"
"""

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "validate-plugin.sh"
# The commands the hook runs besides claude: the whole PATH of a test run.
SYSTEM_TOOLS = ("bash", "awk", "env", "cat", "find")
FINDINGS = 2
HOOK_FAILED = 1


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


class Tree(NamedTuple):
    """A marketplace with one plugin, a PATH folder and a stub claude, in a temporary folder."""

    root: Path
    bin: Path
    stub: Path
    log: Path
    market: Path
    plugin: Path
    skill: Path


def need(name: str) -> str:
    """The path of tool `name`; these are POSIX tools every supported system has."""
    found = shutil.which(name)
    if found is None:
        message = f"{name} is not on PATH"
        raise AssertionError(message)
    return found


def write(path: Path, text: str) -> None:
    """Write text to path, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")


def event(tool: str, file_path: str) -> dict[str, object]:
    """A PostToolUse event for tool on file_path, with a content field that mentions a path."""
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": file_path, "content": '"file_path": "/etc/hosts"'},
        "tool_response": {"filePath": file_path},
    }


def run_hook(tree: Tree, payload: dict[str, object] | str, **env: str) -> Outcome:
    """Run the hook with payload on stdin, the stub as the session's binary, and env."""
    full = {
        "PATH": str(tree.bin),
        "STUB_LOG": str(tree.log),
        "CLAUDE_CODE_EXECPATH": str(tree.stub),
        **env,
    }
    done = subprocess.run(
        [need("bash"), str(HOOK)],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        env=full,
        capture_output=True,
        text=True,
        check=False,
    )
    return Outcome(done.returncode, done.stdout, done.stderr)


def calls(tree: Tree) -> list[str]:
    """The stub calls logged so far."""
    return tree.log.read_text(encoding="utf-8").splitlines() if tree.log.is_file() else []


class ValidateHookTest(unittest.TestCase):
    """The hook validates the plugin or marketplace an edit lands in, and nothing else."""

    def tree(self) -> Tree:
        """A fresh tree, removed when the test ends. The marketplace's name has a space."""
        root = Path(tempfile.mkdtemp(prefix="validate-plugin-test-")).resolve()
        self.addCleanup(shutil.rmtree, root)
        folder = root / "bin"
        folder.mkdir()
        for name in SYSTEM_TOOLS:
            (folder / name).symlink_to(need(name))
        stub = root / "stub" / "claude"
        write(stub, STUB)
        stub.chmod(0o755)
        market = root / "my market"
        write(market / ".claude-plugin" / "marketplace.json", "{}")
        write(market / "README.md", "# Market\n")
        plugin = market / "plugins" / "demo"
        write(plugin / ".claude-plugin" / "plugin.json", '{"name": "demo"}')
        skill = plugin / "skills" / "demo" / "SKILL.md"
        write(skill, "---\nname: demo\ndescription: d\n---\n")
        return Tree(root, folder, stub, root / "calls.log", market, plugin, skill)

    def test_valid_plugin_is_silent(self) -> None:
        """An edit in a plugin that validates exits 0 with no output."""
        tree = self.tree()
        out = run_hook(tree, event("Edit", str(tree.skill)))
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.plugin}"])

    def test_findings_reach_claude(self) -> None:
        """A failing validation exits 2 with the validator's report on stderr."""
        tree = self.tree()
        out = run_hook(
            tree,
            event("Write", str(tree.skill)),
            STUB_EXIT_validate="1",
            STUB_OUT_validate="bogus: x",
        )
        self.assertEqual(out.code, FINDINGS)
        self.assertIn(f"claude plugin validate --strict {tree.plugin} fails", out.stderr)
        self.assertIn("bogus: x", out.stderr)
        self.assertEqual(out.stdout, "")

    def test_marketplace_manifest_validates_the_marketplace(self) -> None:
        """An edit in a marketplace's own .claude-plugin/ folder validates the marketplace."""
        tree = self.tree()
        manifest = tree.market / ".claude-plugin" / "marketplace.json"
        out = run_hook(tree, event("Edit", str(manifest)))
        self.assertEqual(out.code, 0)
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.market}"])

    def test_marketplace_root_file_is_skipped(self) -> None:
        """Another file at a marketplace root, outside every plugin, validates nothing."""
        tree = self.tree()
        out = run_hook(tree, event("Write", str(tree.market / "README.md")))
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(calls(tree), [])

    def test_file_outside_any_plugin_is_skipped(self) -> None:
        """A file in no plugin and no marketplace validates nothing."""
        tree = self.tree()
        loose = tree.root / "elsewhere" / "notes.md"
        write(loose, "x\n")
        out = run_hook(tree, event("Edit", str(loose)))
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(calls(tree), [])

    def test_other_tools_are_skipped(self) -> None:
        """A tool other than Edit or Write validates nothing."""
        tree = self.tree()
        out = run_hook(tree, event("Read", str(tree.skill)))
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(calls(tree), [])

    def test_input_that_is_not_an_event_is_skipped(self) -> None:
        """Input that is not one JSON object exits 0 and validates nothing."""
        tree = self.tree()
        out = run_hook(tree, "not json")
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(calls(tree), [])

    def test_backslash_path_is_normalized(self) -> None:
        """A Windows-style path with backslashes still finds its plugin."""
        tree = self.tree()
        out = run_hook(tree, event("Edit", str(tree.skill).replace("/", "\\")))
        self.assertEqual(out.code, 0)
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.plugin}"])

    def test_claude_on_path_is_the_fallback(self) -> None:
        """Without CLAUDE_CODE_EXECPATH, the hook validates with the claude first on PATH."""
        tree = self.tree()
        (tree.bin / "claude").symlink_to(tree.stub)
        out = run_hook(tree, event("Edit", str(tree.skill)), CLAUDE_CODE_EXECPATH="")
        self.assertEqual(out.code, 0)
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.plugin}"])

    def test_missing_binary_is_a_hook_failure(self) -> None:
        """With no claude binary at all, the hook exits 1 and says why."""
        tree = self.tree()
        out = run_hook(tree, event("Edit", str(tree.skill)), CLAUDE_CODE_EXECPATH="")
        self.assertEqual(out.code, HOOK_FAILED)
        self.assertIn("found no claude binary", out.stderr)

    def test_unexpected_validator_exit_is_a_hook_failure(self) -> None:
        """A validator exit code other than 0 or 1 exits 1, not 2."""
        tree = self.tree()
        out = run_hook(
            tree, event("Write", str(tree.skill)), STUB_EXIT_validate="3", STUB_OUT_validate="crash"
        )
        self.assertEqual(out.code, HOOK_FAILED)
        self.assertIn("exited 3 instead of 0 or 1", out.stderr)
        self.assertIn("crash", out.stderr)

    def test_long_report_reaches_claude_whole(self) -> None:
        """A validator report of hundreds of lines reaches Claude with every line, the last too."""
        tree = self.tree()
        report = "\n".join(f"error {n}: field {n} is wrong" for n in range(1, 301))
        out = run_hook(
            tree, event("Edit", str(tree.skill)), STUB_EXIT_validate="1", STUB_OUT_validate=report
        )
        self.assertEqual(out.code, FINDINGS)
        self.assertIn("error 1: field 1 is wrong", out.stderr)
        self.assertIn("error 300: field 300 is wrong", out.stderr)

    def test_mod_code_edit_runs_the_mod_tests(self) -> None:
        """Editing code in a plugin with mod tests validates it and runs claude plugin test."""
        tree = self.tree()
        write(tree.plugin / "tests" / "pane.test.ts", "test('x', () => {})\n")
        code = tree.plugin / "hooks" / "register.ts"
        write(code, "export {}\n")
        out = run_hook(tree, event("Write", str(code)))
        self.assertEqual(out, Outcome(0, "", ""))
        self.assertEqual(
            calls(tree),
            [f"plugin validate --strict {tree.plugin}", f"plugin test {tree.plugin}"],
        )

    def test_non_code_edit_skips_the_mod_tests(self) -> None:
        """Editing a skill in a plugin with mod tests only validates it."""
        tree = self.tree()
        write(tree.plugin / "tests" / "pane.test.ts", "test('x', () => {})\n")
        out = run_hook(tree, event("Edit", str(tree.skill)))
        self.assertEqual(out.code, 0)
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.plugin}"])

    def test_code_edit_without_mod_tests_skips_them(self) -> None:
        """Editing code in a plugin with no mod tests only validates it."""
        tree = self.tree()
        code = tree.plugin / "scripts" / "run.mjs"
        write(code, "export {}\n")
        out = run_hook(tree, event("Edit", str(code)))
        self.assertEqual(out.code, 0)
        self.assertEqual(calls(tree), [f"plugin validate --strict {tree.plugin}"])

    def test_failing_mod_tests_and_validation_both_reach_claude(self) -> None:
        """When the validator and the mod tests both fail, Claude gets both reports."""
        tree = self.tree()
        write(tree.plugin / "tests" / "pane.test.ts", "test('x', () => {})\n")
        code = tree.plugin / "hooks" / "register.ts"
        write(code, "export {}\n")
        out = run_hook(
            tree,
            event("Edit", str(code)),
            STUB_EXIT_validate="1",
            STUB_OUT_validate="bogus: x",
            STUB_EXIT_test="1",
            STUB_OUT_test="1 test failed: pane draws",
        )
        self.assertEqual(out.code, FINDINGS)
        self.assertIn("bogus: x", out.stderr)
        self.assertIn("1 test failed: pane draws", out.stderr)
        self.assertIn(f"claude plugin test {tree.plugin} fails", out.stderr)

    def test_mods_turned_off_is_a_hook_failure(self) -> None:
        """When mods can't load in the shell, the mod tests count as a check that couldn't run."""
        tree = self.tree()
        write(tree.plugin / "tests" / "pane.test.ts", "test('x', () => {})\n")
        code = tree.plugin / "hooks" / "register.ts"
        write(code, "export {}\n")
        out = run_hook(
            tree,
            event("Edit", str(code)),
            STUB_EXIT_test="1",
            STUB_OUT_test="claude plugin test: hooks modules are turned off here",
        )
        self.assertEqual(out.code, HOOK_FAILED)
        self.assertIn("mods can't load in this shell", out.stderr)


if __name__ == "__main__":
    _ = unittest.main()
