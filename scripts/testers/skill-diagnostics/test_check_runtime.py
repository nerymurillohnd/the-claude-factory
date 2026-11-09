#!/usr/bin/env python3
"""Tests for skills-best-practices' check-runtime.py, plus the three scripts run in order.

Run: python3 -m unittest discover -s scripts/testers/skill-diagnostics -p 'test_check_*.py' -v
Standard library only. Each case builds a skill folder in a temporary directory and runs the
script on it as a separate process.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, cast, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "plugins" / "skill-diagnostics" / "skills" / "skills-best-practices" / "scripts"
SCRIPT = SCRIPTS / "check-runtime.py"
MAX_CHECKS = 200
MAX_DETAIL = 300
NAME = "name: tiny-skill"
DESCRIPTION = "description: Formats tiny reports. Use when the user asks for a tiny report."


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


@dataclass(frozen=True)
class Run:
    """One run of a script: exit code, stdout and stderr."""

    code: int
    stdout: str
    stderr: str

    def json(self) -> JsonObject:
        """The JSON object the script printed."""
        value = _decode(self.stdout)
        if not isinstance(value, JsonObject):
            msg = f"no JSON object on stdout: {self.stdout[:200]!r}"
            raise TypeError(msg)
        return value

    def checks(self) -> list[JsonObject]:
        """Every check result."""
        value = self.json().get("checks")
        if not isinstance(value, list):
            msg = "checks is not a list"
            raise TypeError(msg)
        return [c for c in cast("list[object]", value) if isinstance(c, JsonObject)]

    def having(self, check: str, status: str | None = None) -> list[JsonObject]:
        """The results of one check id, optionally with one status."""
        return [
            c
            for c in self.checks()
            if c.get("check") == check and (status is None or c.get("status") == status)
        ]

    def failed(self) -> list[str]:
        """'<id> <location>' of every failure."""
        return [
            f"{c.get('check')} {c.get('location')}"
            for c in self.checks()
            if c.get("status") == "fail"
        ]

    def locations(self, check: str, status: str = "fail") -> list[str]:
        """Locations of one check's results with one status."""
        return [str(c.get("location")) for c in self.having(check, status)]


def run_script(script: Path, skill: Path, *args: str) -> Run:
    """Run one validation script on a skill folder."""
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str(skill.parent / "no-config")
    cmd = [sys.executable, "-I", str(script), str(skill), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60, env=env)
    return Run(proc.returncode, proc.stdout, proc.stderr)


def skill_md(*fields: str, body: str) -> str:
    """A SKILL.md with name, description, the extra fields and the body."""
    lines = [NAME, DESCRIPTION, *fields]
    return "---\n" + "".join(line + "\n" for line in lines) + "---\n" + body


def executable(path: Path) -> None:
    """Set the executable bits."""
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class Base(unittest.TestCase):
    """Builds skills under a temporary root."""

    root: Path = Path()

    @override
    def setUp(self) -> None:
        """Create the temporary root."""
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.root)

    def skill(self, files: dict[str, str]) -> Path:
        """Write the files into <root>/tiny-skill; every file under scripts/ is executable."""
        folder = self.root / "tiny-skill"
        for rel, text in files.items():
            path = folder / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(text, encoding="utf-8")
            if rel.startswith("scripts/"):
                executable(path)
        return folder

    def check(self, files: dict[str, str], *args: str) -> Run:
        """Write the skill and run check-runtime.py; expect exit 0."""
        result = run_script(SCRIPT, self.skill(files), *args)
        self.assertEqual(result.code, 0, result.stderr)
        return result

    def body(self, body: str, *fields: str, extra: dict[str, str] | None = None) -> Run:
        """Check a skill with this body and frontmatter fields."""
        return self.check({"SKILL.md": skill_md(*fields, body=body), **(extra or {})})


SCRIPT_FILE = {"scripts/x.py": "#!/usr/bin/env python3\nprint(1)\n"}
SHELL_FILE = {"scripts/x.sh": "#!/usr/bin/env bash\necho 1\n"}


class Substitutions(Base):
    """CF-1: escaping of literal $ and use of declared arguments."""

    def test_doubled_backslash_does_not_escape(self) -> None:
        """A doubled backslash before $1 doesn't escape it: R-1 fails at its line."""
        result = self.body("# T\n\nPrice: \\\\$1 each.\n")
        self.assertEqual(result.locations("R-1"), ["SKILL.md:7"])

    def test_money_amount_is_a_literal(self) -> None:
        """'$1.00' is a price that $1 substitution would break."""
        result = self.body("# T\n\nIt costs $1.00.\n")
        self.assertTrue(result.having("R-1", "fail"))

    def test_single_backslash_escapes(self) -> None:
        """One backslash before $1.00 escapes it."""
        result = self.body("# T\n\nIt costs \\$1.00.\n")
        self.assertFalse(result.having("R-1", "fail"))
        self.assertFalse(result.having("R-2"))
        self.assertTrue(result.having("R-1", "pass"))

    def test_placeholder_in_code_is_a_lead(self) -> None:
        """'$1' inside a code block may be shell syntax: a lead to confirm."""
        result = self.body("# T\n\n```bash\nawk '{print $1}' file\n```\n")
        self.assertEqual(result.locations("R-2", "lead"), ["SKILL.md:8"])
        self.assertEqual(result.having("R-2")[0].get("kind"), "lead")

    def test_placeholder_in_prose_is_intended(self) -> None:
        """'$ARGUMENTS' in prose is the documented placeholder: no finding."""
        result = self.body("# T\n\nFind the commits that match: $ARGUMENTS\n")
        self.assertEqual(result.failed(), [])
        self.assertFalse(result.having("R-2"))

    def test_claude_variables_are_fine(self) -> None:
        """${CLAUDE_SKILL_DIR} and friends are not argument placeholders."""
        result = self.body("# T\n\n```bash\necho ${CLAUDE_SKILL_DIR} ${CLAUDE_SESSION_ID}\n```\n")
        self.assertFalse(result.having("R-1", "fail"))
        self.assertFalse(result.having("R-2"))

    def test_declared_name_in_code_is_a_lead(self) -> None:
        """A declared $name inside code is a lead too."""
        result = self.body("# T\n\nUse $issue.\n\n`echo $issue`\n", "arguments: [issue]")
        self.assertEqual(result.locations("R-2", "lead"), ["SKILL.md:10"])

    def test_unused_argument_name(self) -> None:
        """Every declared argument appears as $name."""
        result = self.body("# T\n\nOpen $issue.\n", "arguments: [issue, branch]")
        fails = result.having("R-3", "fail")
        self.assertEqual(len(fails), 1)
        self.assertIn("branch", str(fails[0].get("detail")))
        self.assertEqual(fails[0].get("item"), "CF-1")

    def test_escaped_name_is_not_a_use(self) -> None:
        """An escaped $issue is literal text, so issue is unused."""
        result = self.body("# T\n\nOpen \\$issue.\n", "arguments: issue")
        self.assertTrue(result.having("R-3", "fail"))


class DynamicContext(Base):
    """CF-4 (and its SE-4 lead): no argument placeholder inside a ! command."""

    def test_arguments_in_bang_line(self) -> None:
        """!`git log $ARGUMENTS` is injectable."""
        result = self.body("# T\n\n!`git log --grep $ARGUMENTS`\n")
        self.assertEqual(result.locations("R-4"), ["SKILL.md:7"])
        self.assertTrue(result.having("R-17", "lead"))

    def test_positional_in_bang_fence(self) -> None:
        """A ```! block with $1."""
        result = self.body("# T\n\n```!\ngit show $1\n```\n")
        self.assertEqual(result.locations("R-4"), ["SKILL.md:8"])

    def test_declared_name_in_bang_line(self) -> None:
        """A declared $name inside a ! command."""
        result = self.body("# T\n\n!`gh issue view $issue`\n\nUse $issue.\n", "arguments: issue")
        self.assertTrue(result.having("R-4", "fail"))

    def test_bang_line_without_placeholder(self) -> None:
        """!`git status` is fine."""
        result = self.body("# T\n\n!`git status --short`\n")
        self.assertFalse(result.having("R-4", "fail"))
        self.assertTrue(result.having("R-4", "pass"))


class AllowedTools(Base):
    """CF-2 and SE-4 leads for bare Bash; CF-3 patterns against the body's commands."""

    CMD: str = "python3 ${CLAUDE_SKILL_DIR}/scripts/x.py"

    def test_bare_bash(self) -> None:
        """A bare Bash pre-approves every command: leads for CF-2 and SE-4."""
        result = self.body("# T\n\nRun `ls`.\n", "allowed-tools: Read Bash")
        self.assertTrue(result.having("R-5", "lead"))
        self.assertTrue(result.having("R-6", "lead"))
        self.assertEqual(result.having("R-5")[0].get("item"), "CF-2")
        self.assertEqual(result.having("R-6")[0].get("item"), "SE-4")

    def test_matching_interpreter_pattern(self) -> None:
        """Pattern and body use the same interpreter-prefix form."""
        result = self.body(
            f"# T\n\nRun `{self.CMD} report.txt`.\n",
            f"allowed-tools: Bash({self.CMD} *)",
            extra=SCRIPT_FILE,
        )
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("R-10", "pass"))
        self.assertTrue(result.having("R-11", "pass"))

    def test_pattern_in_direct_form_but_body_uses_prefix(self) -> None:
        """The pattern names the direct form; the body runs python3 ...: both directions fail."""
        result = self.body(
            f"# T\n\nRun `{self.CMD} report.txt`.\n",
            "allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.py *)",
            extra=SCRIPT_FILE,
        )
        self.assertEqual(result.locations("R-10"), ["SKILL.md:4"])
        self.assertEqual(result.locations("R-11"), ["SKILL.md:8"])

    def test_direct_pattern_and_direct_body(self) -> None:
        """Direct form in both places matches (SC-8 still reports the direct call)."""
        result = self.body(
            "# T\n\nRun `${CLAUDE_SKILL_DIR}/scripts/x.sh out`.\n",
            "allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)",
            extra=SHELL_FILE,
        )
        self.assertFalse(result.having("R-10", "fail"))
        self.assertFalse(result.having("R-11", "fail"))
        self.assertTrue(result.having("R-8", "fail"))

    def test_list_form_and_non_script_pattern(self) -> None:
        """A YAML list of patterns; a git pattern matched by a git command in the body."""
        result = self.body(
            f"# T\n\nRun `git status --short`, then `{self.CMD}`.\n",
            "allowed-tools:",
            "  - Read",
            "  - Bash(git status *)",
            f"  - Bash({self.CMD} *)",
            extra=SCRIPT_FILE,
        )
        self.assertEqual(result.failed(), [])

    def test_no_allowed_tools_no_cf3(self) -> None:
        """Without allowed-tools, body commands need no pattern."""
        result = self.body(f"# T\n\nRun `{self.CMD}`.\n", extra=SCRIPT_FILE)
        self.assertFalse(result.having("R-11", "fail"))


class ScriptCalls(Base):
    """SC-7, SC-8 and BS-4: how the body calls bundled scripts."""

    def test_relative_script_path(self) -> None:
        """python3 scripts/x.py runs from the session's folder, not the skill's."""
        result = self.body("# T\n\nRun `python3 scripts/x.py`.\n", extra=SCRIPT_FILE)
        self.assertEqual(result.locations("R-7"), ["SKILL.md:7"])

    def test_script_through_skill_dir(self) -> None:
        """python3 ${CLAUDE_SKILL_DIR}/scripts/x.py passes SC-7 and SC-8."""
        result = self.body(
            "# T\n\n```bash\npython3 ${CLAUDE_SKILL_DIR}/scripts/x.py --json\n```\n",
            extra=SCRIPT_FILE,
        )
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("R-7", "pass"))
        self.assertTrue(result.having("R-8", "pass"))

    def test_direct_call(self) -> None:
        """A script called without its interpreter fails SC-8 for the reviewer to judge."""
        result = self.body("# T\n\nRun `${CLAUDE_SKILL_DIR}/scripts/x.sh out`.\n", extra=SHELL_FILE)
        fails = result.having("R-8", "fail")
        self.assertEqual(len(fails), 1)
        self.assertEqual(fails[0].get("item"), "SC-8")

    def test_path_leaving_the_skill(self) -> None:
        """${CLAUDE_SKILL_DIR}/../ climbs out of the skill."""
        result = self.body("# T\n\nRun `python3 ${CLAUDE_SKILL_DIR}/../other/x.py`.\n")
        self.assertEqual(result.locations("R-9"), ["SKILL.md:7"])

    def test_path_staying_inside(self) -> None:
        """A path after the variable that stays inside passes BS-4."""
        result = self.body("# T\n\nRead `${CLAUDE_SKILL_DIR}/references/../SKILL.md`.\n")
        self.assertFalse(result.having("R-9", "fail"))


class Hooks(Base):
    """CF-6: frontmatter hooks."""

    def hook(self, event: str, *lines: str) -> Run:
        """A skill with one hook on event, whose fields are the given lines."""
        fields = ["hooks:", f"  {event}:", "    - hooks:", "        - type: command"]
        fields += [f"          {line}" for line in lines]
        return self.body("# T\n\nDo it.\n", *fields)

    def test_skill_dir_in_hook(self) -> None:
        """Hook commands don't get ${CLAUDE_SKILL_DIR}."""
        result = self.hook("PostToolUse", 'command: "bash \\"${CLAUDE_SKILL_DIR}/x.sh\\""')
        self.assertEqual(result.locations("R-12"), ["SKILL.md:8"])

    def test_plugin_data_in_hook(self) -> None:
        """Claude Code refuses a skill hook that names ${CLAUDE_PLUGIN_DATA}."""
        result = self.hook("PostToolUse", "command: 'bash \"${CLAUDE_PLUGIN_DATA}/x.sh\"'")
        self.assertEqual(result.locations("R-12"), ["SKILL.md:8"])

    def test_relative_path_in_hook(self) -> None:
        """A relative path resolves against the session folder."""
        result = self.hook("PostToolUse", "command: bash scripts/check.sh")
        self.assertTrue(result.having("R-12", "fail"))

    def test_unquoted_placeholder_in_shell_form(self) -> None:
        """Shell form must double-quote each placeholder."""
        result = self.hook("PostToolUse", "command: bash ${CLAUDE_PLUGIN_ROOT}/hooks/x.sh")
        self.assertEqual(result.locations("R-13"), ["SKILL.md:8"])
        self.assertFalse(result.having("R-12", "fail"))

    def test_quoted_placeholder_in_shell_form(self) -> None:
        """A double-quoted placeholder passes."""
        result = self.hook("PostToolUse", "command: 'bash \"${CLAUDE_PLUGIN_ROOT}/hooks/x.sh\"'")
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("R-13", "pass"))

    def test_exec_form_needs_no_quotes(self) -> None:
        """Exec form (args) passes the placeholder as one argument."""
        result = self.hook(
            "PostToolUse", "command: bash", "args: ['${CLAUDE_PLUGIN_ROOT}/hooks/x.sh']"
        )
        self.assertFalse(result.having("R-13", "fail"))
        self.assertFalse(result.having("R-12", "fail"))

    def test_on_failure_on_stop(self) -> None:
        """OnFailure does nothing on Stop."""
        result = self.hook("Stop", 'command: "echo ok"', "onFailure: block")
        self.assertEqual(result.locations("R-14"), ["SKILL.md:9"])

    def test_on_failure_on_pre_tool_use(self) -> None:
        """OnFailure on PreToolUse is fine."""
        result = self.hook("PreToolUse", 'command: "echo ok"', "onFailure: block")
        self.assertFalse(result.having("R-14", "fail"))


class Signals(Base):
    """SE-1 and SE-3 leads in every file."""

    def test_network_signal_in_script(self) -> None:
        """Curl in a script is a network lead."""
        result = self.body(
            "# T\n\nRun `bash ${CLAUDE_SKILL_DIR}/scripts/x.sh`.\n",
            extra={"scripts/x.sh": "#!/usr/bin/env bash\ncurl -s https://example.com\n"},
        )
        leads = result.having("R-15", "lead")
        self.assertTrue(leads)
        self.assertEqual(leads[0].get("location"), "scripts/x.sh:2")
        self.assertEqual(leads[0].get("item"), "SE-1")

    def test_credential_read_in_reference(self) -> None:
        """~/.ssh in a reference is a credentials lead."""
        result = self.body(
            "# T\n\nRead [r](references/r.md).\n",
            extra={"references/r.md": "# R\n\nCopy the key from ~/.ssh/id_rsa first.\n"},
        )
        leads = result.having("R-16", "lead")
        self.assertTrue(leads)
        self.assertEqual(leads[0].get("item"), "SE-3")

    def test_process_env_is_not_dotenv(self) -> None:
        """process.env is not a .env file."""
        result = self.body(
            "# T\n\nRun `node ${CLAUDE_SKILL_DIR}/scripts/x.js`.\n",
            extra={"scripts/x.js": "#!/usr/bin/env node\nconsole.log(process.env.HOME);\n"},
        )
        self.assertFalse(result.having("R-16"))

    def test_previous_inventory_is_the_file_list(self) -> None:
        """With --previous, only the inventory's files are scanned."""
        folder = self.skill(
            {
                "SKILL.md": skill_md(body="# T\n\nDo it.\n"),
                "notes.txt": "curl https://example.com\n",
            }
        )
        previous = self.root / "structure.json"
        inventory = [{"path": "SKILL.md", "lines": 7, "executable": False}]
        _ = previous.write_text(json.dumps({"script": "check-structure", "inventory": inventory}))
        with_previous = run_script(SCRIPT, folder, "--previous", str(previous))
        self.assertEqual(with_previous.code, 0, with_previous.stderr)
        self.assertFalse(with_previous.having("R-15"))
        without = run_script(SCRIPT, folder)
        self.assertTrue(without.having("R-15", "lead"))

    def test_bad_previous_is_a_usage_error(self) -> None:
        """A --previous file that isn't check-structure JSON exits 2."""
        folder = self.skill({"SKILL.md": skill_md(body="# T\n")})
        previous = self.root / "bad.json"
        _ = previous.write_text("not json")
        result = run_script(SCRIPT, folder, "--previous", str(previous))
        self.assertEqual(result.code, 2)
        self.assertIn("--previous", result.stderr)

    def test_missing_previous_falls_back_to_walk(self) -> None:
        """A --previous file that doesn't exist (check-structure couldn't run) warns and walks."""
        folder = self.skill({"SKILL.md": skill_md(body="# T\n")})
        result = run_script(SCRIPT, folder, "--previous", str(self.root / "absent.json"))
        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("walking the skill folder instead", result.stderr)


class Contract(Base):
    """Exit codes, help, bounded output and the result shape."""

    def test_findings_exit_zero(self) -> None:
        """A skill with failures still exits 0 and prints one JSON object."""
        result = self.body("# T\n\nRun `python3 scripts/x.py` for $1.00.\n", extra=SCRIPT_FILE)
        self.assertTrue(result.failed())
        self.assertEqual(result.json().get("script"), "check-runtime")
        for check in result.checks():
            self.assertIn(check.get("kind"), ("proved", "lead"))
            self.assertLessEqual(len(str(check.get("detail"))), MAX_DETAIL)

    def test_usage_exit_2(self) -> None:
        """No such folder, or no SKILL.md, is a usage error."""
        self.assertEqual(run_script(SCRIPT, self.root / "nope").code, 2)
        empty = self.root / "empty"
        empty.mkdir()
        result = run_script(SCRIPT, empty)
        self.assertEqual(result.code, 2)
        self.assertIn("SKILL.md", result.stderr)

    def test_help(self) -> None:
        """--help exits 0."""
        result = run_script(SCRIPT, self.root, "--help")
        self.assertEqual(result.code, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_output_is_bounded(self) -> None:
        """250 failures: at most 200 checks, the rest counted in truncated."""
        result = self.body("# T\n\n" + "Costs $1.00.\n" * 250)
        self.assertLessEqual(len(result.checks()), MAX_CHECKS)
        truncated = result.json().get("truncated")
        self.assertIsInstance(truncated, int)
        self.assertGreater(truncated if isinstance(truncated, int) else 0, 0)

    def test_output_file_matches_stdout(self) -> None:
        """--output writes the same JSON object as stdout, creating parent folders."""
        folder = self.skill({"SKILL.md": skill_md(body="# T\n")})
        out = self.root / "results" / "nested" / "runtime.json"
        result = run_script(SCRIPT, folder, "--output", str(out))
        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(out.read_text(encoding="utf-8"), result.stdout)
        self.assertEqual(result.json().get("script"), "check-runtime")

    def test_unwritable_output_exits_1(self) -> None:
        """An --output path that can't be written exits 1 and names the path on stderr."""
        folder = self.skill({"SKILL.md": skill_md(body="# T\n")})
        blocker = self.root / "a-file"
        _ = blocker.write_text("x", encoding="utf-8")
        out = blocker / "runtime.json"
        result = run_script(SCRIPT, folder, "--output", str(out))
        self.assertEqual(result.code, 1)
        self.assertIn("--output", result.stderr)
        self.assertIn(str(out), result.stderr)

    def test_proved_checks_only_on_owned_items(self) -> None:
        """check-runtime proves only BS-4, SC-7, SC-8, CF-1, CF-3, CF-4 and CF-6."""
        result = self.body(
            "# T\n\n!`git log $1`\n\nRun `python3 scripts/x.py`.\n",
            "allowed-tools: Bash",
            extra={"scripts/x.py": "#!/usr/bin/env python3\nimport urllib.request\n"},
        )
        owned = ("BS-4", "SC-7", "SC-8", "CF-1", "CF-3", "CF-4", "CF-6")
        for check in result.checks():
            if check.get("kind") == "proved":
                self.assertIn(check.get("item"), owned)
            else:
                self.assertEqual(check.get("status"), "lead")


class Pipeline(Base):
    """The three scripts in order, check-runtime reading check-structure's result."""

    def test_valid_skill_has_no_failure(self) -> None:
        """A small valid skill: every script runs and none reports a failure."""
        cmd = "python3 ${CLAUDE_SKILL_DIR}/scripts/fmt.py"
        folder = self.skill(
            {
                "SKILL.md": skill_md(
                    f"allowed-tools: Bash({cmd} *)",
                    body=(
                        "# Tiny skill\n\n"
                        f"Run `{cmd} <file>` and read its JSON.\n\n"
                        "Read [the guide](references/guide.md) when formatting.\n"
                    ),
                ),
                "scripts/fmt.py": "#!/usr/bin/env python3\nprint('{}')\n",
                "references/guide.md": "# Guide\n\n## Rules\n\nKeep it short.\n",
            }
        )
        failures: list[str] = []
        previous: Path | None = None
        for name in ("check-metadata.py", "check-structure.py", "check-runtime.py"):
            output = self.root / "results" / name.replace(".py", ".json")
            args = ("--previous", str(previous)) if previous else ()
            result = run_script(SCRIPTS / name, folder, *args, "--output", str(output))
            self.assertEqual(result.code, 0, f"{name}: {result.stderr}")
            self.assertEqual(result.json().get("ran"), True)
            self.assertEqual(output.read_text(encoding="utf-8"), result.stdout)
            failures += [f"{name}: {f}" for f in result.failed()]
            previous = output
        self.assertEqual(failures, [])


if __name__ == "__main__":
    _ = unittest.main()
