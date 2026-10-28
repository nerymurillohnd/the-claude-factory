#!/usr/bin/env python3
"""Tests for the hook-development skill's scripts in plugins/hook-engineering.

Run: python3 -m unittest discover -s scripts/testers/hook-engineering -v
Standard library only. The hook-changes.sh cases need bash on PATH (Git Bash on Windows)
and use a stub curl, so they make no network calls.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "plugins" / "hook-engineering" / "skills" / "hook-development" / "scripts"
LINT = SCRIPTS / "lint-hooks-config.py"
PROBE = SCRIPTS / "probe-hook.py"
CHANGES = SCRIPTS / "hook-changes.sh"

VALID = {
    "hooks": {
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "x", "timeout": 10}]}
        ]
    }
}

CHANGELOG = """# Changelog

## 2.1.306

- Fixed a PreToolUse hook bug
- Unrelated fix

## 2.1.305

- Added a Stop hook field

## 2.1.304

- Older hook entry
"""


def scratch(case: unittest.TestCase) -> Path:
    """Create a temporary folder that is removed when the test ends."""
    root = Path(tempfile.mkdtemp())
    case.addCleanup(shutil.rmtree, root)
    return root


def run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and capture its text output."""
    return subprocess.run(args, capture_output=True, text=True, check=False, env=env, timeout=60)


def write_json(path: Path, value: object) -> Path:
    """Write a JSON value to path, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(json.dumps(value), encoding="utf-8")
    return path


def lint(*files: Path) -> subprocess.CompletedProcess[str]:
    """Run the linter on files."""
    return run([sys.executable, str(LINT), *(str(f) for f in files)])


def probe(root: Path, event: str, code: int, stdout: str = "", *extra: str) -> str:
    """Probe a hook that prints stdout, writes a reason to stderr and exits with code."""
    sample = write_json(
        root / "in.json",
        {"hook_event_name": event, "tool_name": "Bash", "tool_input": {"command": "ls"}},
    )
    hook = f"import sys; sys.stdout.write({stdout!r}); sys.stderr.write('reason'); sys.exit({code})"
    command = [sys.executable, str(PROBE), "--input", str(sample), *extra, "--"]
    result = run([*command, sys.executable, "-c", hook])
    assert result.returncode == 0, result.stderr
    return result.stdout


def outcome(report: str) -> str:
    """Return the text of the single outcome line."""
    lines = [line for line in report.splitlines() if line.startswith("outcome: ")]
    assert len(lines) == 1, report
    return lines[0].removeprefix("outcome: ")


def changes(root: Path, body: str, code: int, *args: str) -> subprocess.CompletedProcess[str]:
    """Run hook-changes.sh with a stub curl that prints body and exits with code."""
    stub = root / "bin"
    stub.mkdir()
    _ = (root / "body.txt").write_text(body, encoding="utf-8")
    curl = stub / "curl"
    _ = curl.write_text(
        f'#!/usr/bin/env bash\ncat "{(root / "body.txt").as_posix()}"\nexit {code}\n',
        encoding="utf-8",
    )
    curl.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{stub}{os.pathsep}{env.get('PATH', '')}"
    return run(["bash", str(CHANGES), *args], env)


class LintTest(unittest.TestCase):
    """lint-hooks-config.py: findings, exit codes and per-file isolation."""

    def test_valid_config_exits_zero(self) -> None:
        """A well-formed hooks object has no ERROR."""
        result = lint(write_json(scratch(self) / "ok.json", VALID))
        assert result.returncode == 0, result.stdout
        assert "ERROR" not in result.stdout

    def test_unknown_event_and_flat_handler_are_errors(self) -> None:
        """A wrong-case event and a handler outside a group both fail."""
        bad = {"hooks": {"PreToolUse": [{"type": "command", "command": "x"}], "stop": []}}
        result = lint(write_json(scratch(self) / "bad.json", bad))
        assert result.returncode == 1
        assert "unknown event 'stop'" in result.stdout
        assert "handler outside a group's 'hooks' array" in result.stdout

    def test_missing_file_is_an_error_and_the_next_file_is_linted(self) -> None:
        """An unreadable file is reported and does not stop the run."""
        root = scratch(self)
        ok = write_json(root / "ok.json", VALID)
        result = lint(root / "missing.json", ok)
        assert result.returncode == 1
        assert "cannot read the file" in result.stdout
        assert f"== {ok}:" in result.stdout

    def test_plugin_manifest_that_is_not_an_object(self) -> None:
        """A plugin.json array is an ERROR for that file, not a crash."""
        root = scratch(self)
        hooks = write_json(root / "plugin" / "hooks" / "hooks.json", VALID)
        _ = write_json(root / "plugin" / ".claude-plugin" / "plugin.json", [])
        ok = write_json(root / "other.json", VALID)
        result = lint(hooks, ok)
        assert "Traceback" not in result.stderr, result.stderr
        assert result.returncode == 1
        assert "cannot read the plugin manifest" in result.stdout
        assert f"== {ok}:" in result.stdout

    def test_invalid_plugin_mcp_json(self) -> None:
        """A broken .mcp.json next to a plugin is an ERROR, and the next file is linted."""
        root = scratch(self)
        hooks = write_json(root / "plugin" / "hooks" / "hooks.json", VALID)
        _ = write_json(root / "plugin" / ".claude-plugin" / "plugin.json", {"name": "demo"})
        _ = (root / "plugin" / ".mcp.json").write_text("{bad", encoding="utf-8")
        ok = write_json(root / "other.json", VALID)
        result = lint(hooks, ok)
        assert "Traceback" not in result.stderr, result.stderr
        assert "cannot read the plugin manifest" in result.stdout
        assert f"== {ok}:" in result.stdout


class ProbeTest(unittest.TestCase):
    """probe-hook.py: the predicted outcome per event and exit code."""

    def test_exit2_blocks_on_pretooluse(self) -> None:
        """Exit 2 on PreToolUse is a blocking error."""
        text = outcome(probe(scratch(self), "PreToolUse", 2))
        assert text == "blocking error: stderr is the reason"

    def test_exit2_does_not_block_where_the_event_ignores_it(self) -> None:
        """Exit 2 on PermissionRequest and PostToolUse is not reported as a block."""
        for event in ("PermissionRequest", "PostToolUse"):
            with self.subTest(event=event):
                text = outcome(probe(scratch(self), event, 2))
                assert text.startswith("exit 2 does not block"), text

    def test_on_failure_block_denies_a_permission_request(self) -> None:
        """A failing PermissionRequest hook with onFailure block denies the request."""
        report = probe(scratch(self), "PermissionRequest", 1, "", "--on-failure", "block")
        assert "permission request is denied" in outcome(report)

    def test_on_failure_block_on_pretooluse(self) -> None:
        """A failing PreToolUse hook with onFailure block acts like exit 2."""
        report = probe(scratch(self), "PreToolUse", 1, "", "--on-failure", "block")
        assert "acts like exit 2" in outcome(report)

    def test_json_deny_is_read_as_json(self) -> None:
        """One JSON object on stdout is classified as JSON."""
        deny = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "no",
                }
            }
        )
        assert "stdout: json" in probe(scratch(self), "PreToolUse", 0, deny)

    def test_banner_before_json_is_plain_text(self) -> None:
        """A line before the JSON object turns stdout into plain text."""
        report = probe(scratch(self), "PreToolUse", 0, 'hello\n{"continue": true}')
        assert "stdout: plain" in report


@unittest.skipUnless(shutil.which("bash"), "bash is not on PATH")
class ChangesTest(unittest.TestCase):
    """hook-changes.sh with a stub curl: entries, tags and loud failures."""

    def test_lists_entries_after_the_baseline_and_tags_newer(self) -> None:
        """Entries above since are listed; those above installed are tagged."""
        result = changes(scratch(self), CHANGELOG, 0, "2.1.304", "2.1.305")
        assert result.returncode == 0, result.stderr
        assert "## 2.1.306 [newer than installed]" in result.stdout
        assert "- Fixed a PreToolUse hook bug" in result.stdout
        assert "## 2.1.305\n- Added a Stop hook field" in result.stdout
        assert "Unrelated fix" not in result.stdout
        assert "Older hook entry" not in result.stdout

    def test_no_entries_after_the_newest(self) -> None:
        """Nothing after the newest version prints the no-entries line."""
        result = changes(scratch(self), CHANGELOG, 0, "2.1.306")
        assert result.returncode == 0, result.stderr
        assert "No hook-related changelog entries after 2.1.306." in result.stdout

    def test_download_failure_exits_3_without_claiming_no_changes(self) -> None:
        """A failed download is an error, never "no changes"."""
        result = changes(scratch(self), "", 7, "2.1.300")
        assert result.returncode == 3
        assert "could not download" in result.stderr
        assert "No hook-related" not in result.stdout

    def test_page_without_versions_exits_3(self) -> None:
        """A body with no version headings is not read as "no changes"."""
        result = changes(scratch(self), "<html>rate limited</html>\n", 0, "2.1.300")
        assert result.returncode == 3
        assert "has no version headings" in result.stderr
        assert "No hook-related" not in result.stdout

    def test_rejects_a_leading_v(self) -> None:
        """A version with a leading v is a usage error."""
        result = changes(scratch(self), CHANGELOG, 0, "v2.1.305")
        assert result.returncode == 2
        assert "not a bare version number" in result.stderr


if __name__ == "__main__":
    _ = unittest.main()
