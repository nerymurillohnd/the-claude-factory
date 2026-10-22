#!/usr/bin/env python3
"""Tests for python-lsp-intelligence's hooks/check.py.

Run: python3 -m unittest discover -s scripts/tests/python-lsp-intelligence -v
Standard library only. The tool cases need ruff and basedpyright on PATH.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "python-lsp-intelligence" / "hooks" / "check.py"
HAVE_TOOLS = shutil.which("ruff") is not None and shutil.which("basedpyright") is not None
REPORT_CEILING = 9_100
MANY = 23
LONG_AGO = 600
SKILL_HINT = (
    "Use the python-lsp-intelligence:python-lsp-intelligence skill and apply all its knowledge "
    "when working on Python files."
)


def event(tool: str, path: Path | None = None, **extra: object) -> str:
    """Build one hook event as JSON."""
    data: dict[str, object] = {"hook_event_name": "PostToolUse", "tool_name": tool}
    if path is not None:
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        data["tool_input"] = {key: str(path)}
    data.update(extra)
    return json.dumps(data)


def fire(payload: str, cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run the hook on one event; return exit code, stdout and stderr."""
    run_env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}
    run_env["CLAUDE_PLUGIN_ROOT"] = str(HOOK.parent.parent)
    if env:
        run_env.update(env)
    done = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=run_env,
        check=False,
    )
    return done.returncode, done.stdout, done.stderr


def age(path: Path) -> None:
    """Move a file's mtime ten minutes into the past."""
    then = time.time() - LONG_AGO
    os.utime(path, (then, then))


class Workspace(unittest.TestCase):
    """A temporary home (no user-level config) and a project folder."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="pylsp-"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        self.env = {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config")}

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name: str, text: str) -> Path:
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        # Bytes keep LF on Windows too; Path.write_text(newline=) needs Python 3.10.
        path.write_bytes(text.encode("utf-8"))
        return path


class NonPythonAndBadInput(Workspace):
    def test_markdown_edit_is_silent(self) -> None:
        path = self.write("notes.md", "# hi\n")
        assert fire(event("Edit", path), self.project, self.env) == (0, "", "")

    def test_unreadable_stdin_is_silent(self) -> None:
        assert fire("not json", self.project, self.env) == (0, "", "")

    def test_venv_file_is_skipped(self) -> None:
        path = self.write(".venv/lib/x.py", "x=1\n")
        assert fire(event("Edit", path), self.project, self.env) == (0, "", "")

    def test_read_only_bash_is_silent(self) -> None:
        age(self.write("a.py", "x = 1\n"))
        payload = event("Bash", duration_ms=0, tool_input={"command": "ls"})
        assert fire(payload, self.project, self.env) == (0, "", "")


@unittest.skipUnless(HAVE_TOOLS, "ruff and basedpyright are not on PATH")
class WithTools(Workspace):
    def test_clean_file_confirms(self) -> None:
        body = '"""Doc."""\n\n\ndef add(left: int, right: int) -> int:\n    """Add."""\n'
        path = self.write("clean.py", body + "    return left + right\n")
        code, out, err = fire(event("Edit", path), self.project, self.env)
        assert (code, err) == (0, "")
        payload = json.loads(out)
        assert (
            "python-lsp-intelligence: ruff check, ruff format, basedpyright passed"
            in payload["systemMessage"]
        )
        assert "clean.py" in payload["systemMessage"]
        assert "hookSpecificOutput" not in payload
        assert "apply all its knowledge" not in out

    def test_format_rewrite_asks_for_reread(self) -> None:
        path = self.write("fmt.py", '"""Doc."""\n\nVALUE=1\n')
        code, out, _ = fire(event("Write", path), self.project, self.env)
        assert code == 0
        payload = json.loads(out)  # one JSON object carrying both fields
        assert set(payload) == {"systemMessage", "hookSpecificOutput"}
        assert "passed" in payload["systemMessage"]
        assert "re-read" in payload["hookSpecificOutput"]["additionalContext"]
        assert payload["hookSpecificOutput"]["additionalContext"].endswith(SKILL_HINT)
        assert payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert path.read_text(encoding="utf-8") == '"""Doc."""\n\nVALUE = 1\n'

    def test_findings_block_with_exit_2(self) -> None:
        path = self.write("bad.py", '"""Doc."""\n\n\ndef f(x):\n    return undefined_name\n')
        code, out, err = fire(event("Edit", path), self.project, self.env)
        assert (code, out) == (2, "")
        assert "F821" in err
        assert "reportMissingParameterType" in err
        assert "Fix these findings in" in err
        assert err.endswith(f"{SKILL_HINT}\n")

    def test_user_config_wins_over_defaults(self) -> None:
        self.write("ruff.toml", "[lint]\nselect = []\n")
        self.write(
            "pyrightconfig.json", '{"typeCheckingMode": "off", "reportUndefinedVariable": false}\n'
        )
        path = self.write("pkg/loose.py", "def f(x):\n    return undefined_name\n")
        code, out, err = fire(event("Edit", path), self.root, self.env)  # cwd above the project
        assert (code, err) == (0, "")
        assert "passed" in json.loads(out)["systemMessage"]

    def test_pyright_config_found_above_subfolder(self) -> None:
        self.write("pyrightconfig.json", '{"typeCheckingMode": "strict"}\n')
        self.write("ruff.toml", "[lint]\nselect = []\n")
        path = self.write("src/pkg/mod.py", "def f(x):\n    return x\n")
        code, _, err = fire(event("Edit", path), self.home, self.env)
        assert code == 2
        assert "reportMissingParameterType" in err

    def test_broken_user_config_is_a_failure(self) -> None:
        self.write("pyproject.toml", "[tool.ruff]\nline-length = 'ten'\n")
        path = self.write("a.py", "x = 1\n")
        code, _, err = fire(event("Edit", path), self.project, self.env)
        assert code == 2
        assert "ruff check" in err
        assert "was not checked" in err

    def test_path_with_spaces_and_unicode(self) -> None:
        path = self.write("mi carpeta/código.py", '"""Doc."""\n\nVALUE = 1\n')
        code, out, err = fire(event("Edit", path), self.project, self.env)
        assert (code, err) == (0, "")
        assert "mi carpeta/código.py" in json.loads(out)["systemMessage"]

    def test_notebook_runs_ruff_only(self) -> None:
        cells = {
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": ["x = 1\n"],
                    "outputs": [],
                    "execution_count": None,
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        path = self.write("nb.ipynb", json.dumps(cells))
        code, out, err = fire(event("NotebookEdit", path), self.project, self.env)
        assert (code, err) == (0, "")
        assert "ruff check, ruff format passed" in json.loads(out)["systemMessage"]

    def test_bash_with_edit_diff(self) -> None:
        path = self.write("b.py", "def f(x):\n    return undefined_name\n")
        payload = event(
            "Bash",
            tool_response={"bashEditDiff": {"changedFiles": [str(path)]}},
            tool_input={"command": "sed -i s/a/b/ b.py"},
        )
        code, _, err = fire(payload, self.project, self.env)
        assert code == 2
        assert "F821" in err

    def test_bash_without_diff_in_git(self) -> None:
        git = shutil.which("git") or "git"
        subprocess.run([git, "init", "-q", str(self.project)], check=True)
        age(self.write("old.py", "def f(x):\n    return undefined_name\n"))
        self.write("new.py", "def f(x):\n    return undefined_name\n")
        payload = event("Bash", duration_ms=50, cwd=str(self.project), tool_input={"command": "x"})
        code, _, err = fire(payload, self.project, self.env)
        assert code == 2
        assert "new.py" in err
        assert "old.py" not in err

    def test_bash_without_diff_outside_git(self) -> None:
        self.write("sub/x.py", "def f(x):\n    return undefined_name\n")
        payload = event("Bash", tool_input={"command": "x"})  # no duration_ms: 30 s window
        env = {**self.env, "CLAUDE_PROJECT_DIR": str(self.project)}
        code, _, err = fire(payload, self.home, env)
        assert code == 2
        assert "sub/x.py" in err

    def test_unreadable_folder_is_skipped_by_the_walk(self) -> None:
        locked = self.project / "locked"
        locked.mkdir()
        locked.chmod(0o000)
        self.write("new.py", "def f(x):\n    return undefined_name\n")
        payload = event("Bash", duration_ms=20, tool_input={"command": "x"})
        env = {**self.env, "CLAUDE_PROJECT_DIR": str(self.project)}
        try:
            code, _, err = fire(payload, self.home, env)
        finally:
            locked.chmod(0o755)
        assert "Traceback" not in err
        assert code == 2
        assert "new.py" in err

    def test_home_is_never_walked(self) -> None:
        self.write("new.py", "def f(x):\n    return undefined_name\n")
        payload = event("Bash", duration_ms=20, tool_input={"command": "x"})
        env = {
            **self.env,
            "HOME": str(self.project),
            "USERPROFILE": str(self.project),
            "CLAUDE_PROJECT_DIR": str(self.project),
        }
        assert fire(payload, self.project, env) == (0, "", "")

    def test_default_profile_resolves_first_party_imports(self) -> None:
        self.write("pyproject.toml", '[project]\nname = "demo"\nversion = "0.1.0"\n')
        self.write("mypkg/__init__.py", '"""Pkg."""\n\nVALUE = 1\n')
        body = '"""Mod."""\n\nfrom mypkg import VALUE\n\n\ndef f() -> int:\n    """Use."""\n'
        path = self.write("mypkg/sub/mod.py", body + "    return VALUE\n")
        code, out, err = fire(event("Edit", path), self.home, self.env)  # cwd elsewhere on purpose
        assert (code, err) == (0, "")
        assert "passed" in json.loads(out)["systemMessage"]

    def test_default_profile_resolves_src_layout_imports(self) -> None:
        self.write("pyproject.toml", '[project]\nname = "demo"\nversion = "0.1.0"\n')
        self.write("src/pkg2/__init__.py", '"""Pkg."""\n\nX = 2\n')
        path = self.write(
            "src/pkg2/use.py",
            '"""Use."""\n\nfrom pkg2 import X\n\n\ndef g() -> int:\n    """Use."""\n    return X\n',
        )
        code, out, err = fire(event("Edit", path), self.home, self.env)
        assert (code, err) == (0, "")
        assert "passed" in json.loads(out)["systemMessage"]

    def test_post_tool_use_failure_names_its_event(self) -> None:
        self.write("c.py", '"""Doc."""\n\nVALUE=1\n')
        payload = json.dumps(
            {
                "hook_event_name": "PostToolUseFailure",
                "tool_name": "Bash",
                "tool_input": {"command": "x"},
                "error": "Exit code 1",
                "duration_ms": 10,
            },
        )
        code, out, _ = fire(payload, self.project, self.env)
        assert code == 0
        assert json.loads(out)["hookSpecificOutput"]["hookEventName"] == "PostToolUseFailure"

    def test_findings_after_a_failed_bash_call_name_the_skill_too(self) -> None:
        path = self.write("bad2.py", "def f(x):\n    return undefined_name\n")
        payload = event(
            "Bash",
            hook_event_name="PostToolUseFailure",
            tool_response={"bashEditDiff": {"changedFiles": [str(path)]}},
            tool_input={"command": "x"},
        )
        code, _, err = fire(payload, self.project, self.env)
        assert code == 2
        assert "F821" in err
        assert err.endswith(f"{SKILL_HINT}\n")

    def test_more_than_twenty_files_reports_the_rest(self) -> None:
        paths = [self.write(f"many/f{i}.py", '"""Doc."""\n\nVALUE = 1\n') for i in range(MANY)]
        payload = event(
            "Bash",
            tool_response={"bashEditDiff": {"changedFiles": [str(p) for p in paths]}},
            tool_input={"command": "x"},
        )
        code, _, err = fire(payload, self.project, self.env)
        assert code == 2
        assert "not checked" in err
        unchecked = [line for line in err.splitlines() if line.startswith("  many/f")]
        assert len(unchecked) == 3
        assert "many/f0.py\n" not in "\n".join(unchecked) + "\n"

    def test_oversized_report_is_cut(self) -> None:
        body = "".join(f"v{i} = undefined_{i}\n" for i in range(800))
        path = self.write("huge.py", body)
        code, _, err = fire(event("Edit", path), self.project, self.env)
        assert code == 2
        assert len(err) <= REPORT_CEILING
        assert "more lines" in err
        assert err.endswith(f"{SKILL_HINT}\n")


class MissingTools(Workspace):
    def test_missing_ruff_is_reported(self) -> None:
        path = self.write("a.py", "x = 1\n")
        empty = self.root / "bin"
        empty.mkdir()
        code, out, err = fire(event("Edit", path), self.project, {**self.env, "PATH": str(empty)})
        assert (code, out) == (2, "")
        assert "ruff is not installed" in err
        assert "uv tool install ruff" in err
        assert err.endswith(f"{SKILL_HINT}\n")


if __name__ == "__main__":
    unittest.main()
