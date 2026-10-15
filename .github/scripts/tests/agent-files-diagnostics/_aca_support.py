"""Shared fixture for agent-files-diagnostics' tests: paths, a project with known defects, a runner.

Importing this module puts the plugin's scripts folder on sys.path, so the tests import the `aca`
package the way the entry script does. The fixture builds a throwaway HOME and git repository
whose instruction files hold defects with known answers. The runner calls the entry script with a
minimal environment, and `fake_run` writes the journal and transcripts a workflow run would leave,
so no test reads the real user's files, starts a model, or spends anything.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import cast

TESTS = Path(__file__).resolve().parent
REPO_ROOT = TESTS.parents[3]
PLUGIN = REPO_ROOT / "plugins" / "agent-files-diagnostics"
SCRIPTS = PLUGIN / "skills" / "agent-context-audit" / "scripts"
ENTRY = SCRIPTS / "agent_context_audit.py"
FAKE_CLAUDE = TESTS / "fake_claude_version.sh"
POSIX = os.name == "posix"
NOT_KEY_CHAR = re.compile(r"[^A-Za-z0-9-]")
RUN_TIMEOUT = 300
Done = subprocess.CompletedProcess[str]

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

USER_CLAUDE_MD = """\
# Personal preferences

- Prefer short answers.
@~/.claude/missing-personal.md
"""

PROJECT_CLAUDE_MD = """\
# Project guide

Run `npm run lint` before every commit to keep the style consistent.

@docs/missing.md

See @docs/guide.md for the writing rules.

<!-- maintainers: always refresh this file before a release -->
"""

GUIDE_MD = """\
# Writing rules

Use sentence case in headings.

Follow [the style guide](style.md#headings) and [the project guide](../CLAUDE.md).
"""

AGENTS_MD = """\
# Agent guide

Run `npm run lint` before every commit to keep the style consistent.
"""

RULE_MD = """\
---
paths:
  - "src/**/*.ts"
---

# TypeScript style

Prefer named exports in TypeScript modules.
"""

SUBAGENT_MD = """\
---
name: reviewer
description: Reviews a change for style problems.
tools: Read, Grep
---

You review the change and list style problems.
"""

CODEX_CONFIG = """\
model = "gpt-5"
experimental_instructions_file = "instructions.md"
"""

MARKDOWN_FILES = {
    "CLAUDE.local.md": (
        "# Local notes\n\n- My sandbox runs on port 3000.\n"
        "- Run `npm run lint` before every commit to keep the style consistent.\n"
    ),
    "packages/web/CLAUDE.md": "# Web package\n\nUse the web package's own test command.\n",
    "packages/web/AGENTS.md": "# Web agents\n\nKeep components small.\n",
    "node_modules/left-pad/CLAUDE.md": "# left-pad\n\nRun the package's own tests.\n",
    ".claude/output-styles/terse.md": "---\nname: Terse\ndescription: Short\n---\n\nBe terse.\n",
    ".claude/loop.md": "Check the build and report what changed.\n",
    ".claude/skills/demo/SKILL.md": "---\nname: demo\ndescription: A demo skill.\n---\n\nSay hi.\n",
    ".claude/commands/hello.md": "Say hello.\n",
}


def write(path: Path, text: str) -> None:
    """Write a fixture file, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    """Write a fixture JSON file."""
    write(path, json.dumps(value, indent=2) + "\n")


def git_exe() -> str:
    """The git executable on PATH (the tests need it)."""
    found = shutil.which("git")
    if found is None:
        message = "git is required for these tests"
        raise RuntimeError(message)
    return found


def git(repo: Path, *args: str) -> str:
    """Run git in the fixture repository and return its output."""
    done = subprocess.run(
        [git_exe(), "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return done.stdout


@dataclass
class Fixture:
    """A throwaway HOME, a git repository with known defects, and a bin folder for PATH."""

    base: Path
    home: Path
    repo: Path
    bin: Path

    @property
    def report_root(self) -> Path:
        """The in-repo report folder."""
        return self.repo / ".claude" / "agent-context-audit"

    @property
    def claude_dir(self) -> Path:
        """The fixture's ~/.claude."""
        return self.home / ".claude"


def memory_dir(home: Path, repo: Path) -> Path:
    """Claude Code's auto memory folder for repo: the path with every other character as '-'."""
    return home / ".claude" / "projects" / NOT_KEY_CHAR.sub("-", str(repo.resolve())) / "memory"


def _user_files(home: Path, repo: Path) -> None:
    write(home / ".claude" / "CLAUDE.md", USER_CLAUDE_MD)
    write(home / ".claude" / "agents" / "helper.md", SUBAGENT_MD.replace("reviewer", "helper"))
    memory = memory_dir(home, repo)
    write(memory / "MEMORY.md", "# Memory\n\n- [Build](build.md): the build needs Node.\n")
    write(memory / "build.md", "The build needs Node.\n")
    write(home / ".codex" / "AGENTS.md", "# Codex\n\nAnswer briefly.\n")
    settings: dict[str, object] = {
        "permissions": {"allow": ["Bash(npm test)"], "deny": ["Bash(npm test)"]},
    }
    write_json(home / ".claude" / "settings.json", settings)
    servers: dict[str, object] = {"notes": {"command": "notes-server"}}
    claude_json: dict[str, object] = {"numStartups": 3, "mcpServers": servers}
    write_json(home / ".claude.json", claude_json)
    write(home / ".codex" / "config.toml", CODEX_CONFIG)


def _project_files(repo: Path) -> None:
    write(repo / "CLAUDE.md", PROJECT_CLAUDE_MD)
    write(repo / "docs" / "guide.md", GUIDE_MD)
    write(repo / "AGENTS.md", AGENTS_MD)
    write(repo / ".claude" / "rules" / "typescript.md", RULE_MD)
    write(repo / ".claude" / "agents" / "reviewer.md", SUBAGENT_MD)
    write_json(repo / "package.json", {"name": "fixture", "scripts": {"test": "node --test"}})
    write_json(repo / ".claude" / "settings.json", {"fixtureUnknownKey": True})
    write(repo / "src" / "app.js", "export const app = 1;\n")
    for name, text in MARKDOWN_FILES.items():
        write(repo / name, text)
    mcp: dict[str, object] = {"docs": {"type": "http", "url": "https://example.com/mcp"}}
    write_json(repo / ".mcp.json", {"mcpServers": mcp})
    write(repo / ".codex" / "config.toml", 'model = "gpt-5"\n')


def _bin(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, target in (("git", git_exe()), ("python3", sys.executable)):
        link = folder / name
        if not link.exists():
            link.symlink_to(target)
    claude = folder / "claude"
    if not claude.exists():
        write(claude, '#!/bin/sh\necho "2.1.300 (Claude Code)"\n')
        claude.chmod(0o755)


def build(base: Path) -> Fixture:
    """Create the fixture under base (an empty temporary folder)."""
    fixture = Fixture(base=base, home=base / "home", repo=base / "repo", bin=base / "bin")
    fixture.repo.mkdir(parents=True)
    _project_files(fixture.repo)
    _user_files(fixture.home, fixture.repo)
    _bin(fixture.bin)
    _ = git(fixture.repo, "init", "-q", "-b", "main")
    _ = git(fixture.repo, "add", "-A")
    _ = git(
        fixture.repo,
        "-c",
        "user.name=fixture",
        "-c",
        "user.email=fixture@example.com",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "-m",
        "fixture",
    )
    return fixture


def environment(fixture: Fixture, **extra: str) -> dict[str, str]:
    """A minimal environment: the fixture HOME, a PATH with git, python3 and a fake claude."""
    env = {
        "HOME": str(fixture.home),
        "PATH": str(fixture.bin),
        "LANG": "C.UTF-8",
        "TMPDIR": str(fixture.base),
    }
    env.update(extra)
    return env


def run_cli(args: list[str], env: dict[str, str], cwd: Path | None = None) -> Done:
    """Run the entry script with this interpreter and return what it did."""
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
        timeout=RUN_TIMEOUT,
        check=False,
    )


def parse(text: str) -> object:
    """Decode JSON text."""
    return cast("object", json.loads(text))


def load(path: Path) -> object:
    """Decode a JSON file."""
    return cast("object", json.loads(path.read_text(encoding="utf-8")))


# Interpreter caches under the throwaway HOME: Apple's /usr/bin/python3 writes the standard
# library's bytecode to ~/Library/Caches/com.apple.python when the runner starts.
OS_CACHES = ("Library", "Caches")


def digests(fixture: Fixture) -> dict[str, str]:
    """Content of every fixture file outside .git and the report folder, for before/after checks."""
    seen: dict[str, str] = {}
    for root in (fixture.home, fixture.repo):
        for path in sorted(root.rglob("*")):
            parts = path.relative_to(root).parts
            if ".git" in parts or "agent-context-audit" in parts or not path.is_file():
                continue
            if root == fixture.home and parts[:2] == OS_CACHES:
                continue
            if ".claude" in parts and "projects" in parts and "subagents" in parts:
                continue
            seen[str(path)] = path.read_text(encoding="utf-8", errors="replace")
    return seen


# --- a fake workflow run ----------------------------------------------------------------------


def numbered(lines: list[str], offset: int, limit: int) -> str:
    """What the Read tool returns for a chunk: 'N<TAB>text' lines."""
    chunk = lines[offset - 1 : offset - 1 + limit]
    return "\n".join(f"{offset + index}\t{text}" for index, text in enumerate(chunk))


@dataclass
class Scenario:
    """What a fake workflow run returns and reads.

    `results` maps each agent label to its structured result. `reads` maps a label to the files
    it read, as (snapshot path, offset, limit); every read returns the real numbered text of the
    copy, except the line `skip` names for that label, which is left out. `tools` adds extra tool
    calls to a label's transcript.
    """

    results: dict[str, object]
    reads: dict[str, list[tuple[Path, int, int]]]
    tools: dict[str, list[str]]
    skip: dict[str, int]


def _read_events(scenario: Scenario, label: str, number: int) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for index, (path, offset, limit) in enumerate(scenario.reads.get(label, [])):
        lines = path.read_text(encoding="utf-8").split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        text = numbered(lines, offset, limit)
        dropped = scenario.skip.get(label)
        if dropped is not None:
            text = "\n".join(
                line for line in text.split("\n") if not line.startswith(f"{dropped}\t")
            )
        use = f"toolu_{number}_{index}"
        call = {
            "type": "tool_use",
            "id": use,
            "name": "Read",
            "input": {"file_path": str(path), "offset": offset, "limit": limit},
        }
        usage = {"input_tokens": 10, "output_tokens": 5}
        message = {"model": "claude-sonnet-5-5", "usage": usage, "content": [call]}
        events.append({"type": "assistant", "message": message})
        result = {"type": "tool_result", "tool_use_id": use, "content": text}
        events.append({"type": "user", "message": {"content": [result]}})
    return events


def fake_run(fixture: Fixture, run_id: str, scenario: Scenario) -> Path:
    """Write the journal and transcripts of a workflow run under the fixture's session folders."""
    session = fixture.claude_dir / "projects" / "fixture" / "session"
    run_dir = session / "subagents" / "workflows" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    journal: list[dict[str, object]] = [{"type": "launched"}]
    for number, (label, result) in enumerate(scenario.results.items(), start=1):
        agent = f"a{number:016d}"
        journal.append({"type": "started", "key": f"v2:{label}", "agentId": agent, "label": label})
        journal.append({"type": "result", "key": f"v2:{label}", "agentId": agent, "result": result})
        events = _read_events(scenario, label, number)
        for name in scenario.tools.get(label, []):
            call = {"type": "tool_use", "id": f"x{name}", "name": name, "input": {}}
            message = {"model": "claude-sonnet-5-5", "content": [call]}
            events.append({"type": "assistant", "message": message})
        final = {"type": "tool_use", "id": "out", "name": "StructuredOutput", "input": result}
        usage = {"input_tokens": 20, "output_tokens": 50}
        events.append(
            {
                "type": "assistant",
                "message": {"model": "claude-sonnet-5-5", "usage": usage, "content": [final]},
            }
        )
        with (run_dir / f"agent-{agent}.jsonl").open("w", encoding="utf-8") as handle:
            for event in events:
                _ = handle.write(json.dumps(event) + "\n")
    with (run_dir / "journal.jsonl").open("w", encoding="utf-8") as handle:
        for entry in journal:
            _ = handle.write(json.dumps(entry) + "\n")
    return run_dir
