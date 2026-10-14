"""Shared fixture for agent-context-audit's tests: paths, a project with known defects, a runner.

Importing this module puts the plugin's scripts folder on sys.path, so the tests import the `aca`
package the way the entry script does. The fixture builds a throwaway HOME and git repository
whose instruction files hold defects with known answers; the runner calls the entry script with
a minimal environment and the fake claude CLI, so no test reads the real user's files or spends
anything.
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
PLUGIN = REPO_ROOT / "plugins" / "agent-context-audit"
SCRIPTS = PLUGIN / "skills" / "audit" / "scripts"
ENTRY = SCRIPTS / "agent_context_audit.py"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
FAKE_CLAUDE = TESTS / "fake_claude.py"
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

CODEX_RULES = """\
prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
)
"""

MARKDOWN_FILES = {
    "CLAUDE.local.md": (
        "# Local notes\n\n- My sandbox runs on port 3000.\n"
        "- Run `npm run lint` before every commit to keep the style consistent.\n"
    ),
    "packages/web/CLAUDE.md": "# Web package\n\nUse the web package's own test command.\n",
    "packages/web/AGENTS.md": "# Web agents\n\nKeep components small.\n",
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
        "enabledPlugins": {"agent-context-audit@the-claude-factory": True},
        "permissions": {"allow": ["Bash(npm test)"], "deny": ["Bash(npm test)"]},
    }
    write_json(home / ".claude" / "settings.json", settings)
    servers: dict[str, object] = {"notes": {"command": "notes-server"}}
    local: dict[str, object] = {"mcpServers": {"local": {"command": "local-server"}}}
    claude_json: dict[str, object] = {
        "numStartups": 3,
        "mcpServers": servers,
        "projects": {str(repo.resolve()): local},
    }
    write_json(home / ".claude.json", claude_json)
    write(home / ".codex" / "config.toml", CODEX_CONFIG)


def _project_files(repo: Path) -> None:
    write(repo / "CLAUDE.md", PROJECT_CLAUDE_MD)
    write(repo / "docs" / "guide.md", GUIDE_MD)
    write(repo / "AGENTS.md", AGENTS_MD)
    write(repo / ".claude" / "rules" / "typescript.md", RULE_MD)
    write(repo / ".claude" / "agents" / "reviewer.md", SUBAGENT_MD)
    write_json(repo / "package.json", {"name": "fixture", "scripts": {"test": "node --test"}})
    hook: dict[str, object] = {"type": "command", "command": ".claude/hooks/missing.sh"}
    settings: dict[str, object] = {
        "fixtureUnknownKey": True,
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [hook]}]},
    }
    write_json(repo / ".claude" / "settings.json", settings)
    write_json(repo / ".claude" / "settings.local.json", {"permissions": {"allow": ["Read"]}})
    write(repo / "src" / "app.js", "export const app = 1;\n")
    for name, text in MARKDOWN_FILES.items():
        write(repo / name, text)
    mcp: dict[str, object] = {"docs": {"type": "http", "url": "https://example.com/mcp"}}
    write_json(repo / ".mcp.json", {"mcpServers": mcp})
    write(repo / ".codex" / "config.toml", 'model = "gpt-5"\n')
    write(repo / ".codex" / "rules" / "default.rules", CODEX_RULES)


def _bin(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, target in (("git", git_exe()), ("python3", sys.executable)):
        link = folder / name
        if not link.exists():
            link.symlink_to(target)


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


def environment(fixture: Fixture, scenario: str = "clean", **extra: str) -> dict[str, str]:
    """A minimal environment: the fixture HOME, a PATH with only git and python3, the fake CLI."""
    env = {
        "HOME": str(fixture.home),
        "PATH": str(fixture.bin),
        "LANG": "C.UTF-8",
        "TMPDIR": str(fixture.base),
        "AGENT_CONTEXT_AUDIT_CLAUDE": str(FAKE_CLAUDE),
        "FAKE_CLAUDE_SCENARIO": scenario,
    }
    env.update(extra)
    return env


def run_cli(
    args: list[str],
    env: dict[str, str],
    stdin: str = "",
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the entry script with this interpreter and return what it did."""
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
        timeout=RUN_TIMEOUT,
        check=False,
    )


def audit(
    fixture: Fixture, scenario: str = "clean", *args: str
) -> subprocess.CompletedProcess[str]:
    """Run an offline audit of the fixture repository with the fake CLI and --json output."""
    argv = ["run", "--repo", str(fixture.repo), "--offline", "--json", *args]
    return run_cli(argv, environment(fixture, scenario))


def parse(text: str) -> object:
    """Decode JSON text."""
    return cast("object", json.loads(text))


def load(path: Path) -> object:
    """Decode a JSON file."""
    return cast("object", json.loads(path.read_text(encoding="utf-8")))


def digests(fixture: Fixture) -> dict[str, str]:
    """Content of every fixture file outside .git and the report folder, for before/after checks."""
    seen: dict[str, str] = {}
    for root in (fixture.home, fixture.repo):
        for path in sorted(root.rglob("*")):
            parts = path.relative_to(root).parts
            if ".git" in parts or "agent-context-audit" in parts or not path.is_file():
                continue
            seen[str(path)] = path.read_text(encoding="utf-8", errors="replace")
    return seen
