"""Locations the audit reads and writes, and the read-only git calls it makes."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

GIT_TIMEOUT = 30
REPORT_DIR_ENV = "AGENT_CONTEXT_AUDIT_REPORT_DIR"
IN_REPO_REPORT_DIR = (".claude", "agent-context-audit")
NOT_KEY_CHAR = re.compile(r"[^A-Za-z0-9-]")
MANAGED_DIRS = {
    "macos": Path("/Library/Application Support/ClaudeCode"),
    "linux": Path("/etc/claude-code"),
    "wsl": Path("/etc/claude-code"),
}


@dataclass(frozen=True)
class Env:
    """Where this user's Claude Code and Codex files live."""

    home: Path
    claude_dir: Path
    claude_json: Path
    codex_home: Path
    platform: str
    managed_dir: Path | None


def detect_platform() -> str:
    """Return macos, linux, wsl or windows."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    try:
        version = Path("/proc/version").read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        version = ""
    return "wsl" if "microsoft" in version else "linux"


def detect_env(environ: Mapping[str, str]) -> Env:
    """Resolve the user's configuration directories from the environment."""
    home = Path(environ.get("HOME") or str(Path.home()))
    config = environ.get("CLAUDE_CONFIG_DIR", "")
    claude_dir = Path(config).expanduser() if config else home / ".claude"
    claude_json = claude_dir / ".claude.json" if config else home / ".claude.json"
    codex = environ.get("CODEX_HOME", "")
    codex_home = Path(codex).expanduser() if codex else home / ".codex"
    platform = detect_platform()
    return Env(
        home=resolve(home),
        claude_dir=resolve(claude_dir),
        claude_json=resolve(claude_json),
        codex_home=resolve(codex_home),
        platform=platform,
        managed_dir=MANAGED_DIRS.get(platform),
    )


def resolve(path: Path) -> Path:
    """Return the canonical path when it can be resolved, else the absolute path."""
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def git_executable() -> str | None:
    """Return the git executable on PATH, if any."""
    return shutil.which("git")


def run_git(repo: Path, args: Sequence[str]) -> str | None:
    """Run a read-only git command that never takes optional locks; None when it fails."""
    exe = git_executable()
    if exe is None:
        return None
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
    try:
        done = subprocess.run(
            [exe, "--no-optional-locks", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
            check=False,
            env=env,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def repo_root(start: Path) -> Path:
    """Return the git top-level directory containing start, or start itself."""
    out = run_git(start, ["rev-parse", "--show-toplevel"])
    if out and out.strip():
        return resolve(Path(out.strip()))
    return resolve(start)


def memory_root(repo: Path) -> Path:
    """Return the main worktree root, which keys the auto memory directory of every worktree."""
    out = run_git(repo, ["rev-parse", "--path-format=absolute", "--git-common-dir"])
    if out and out.strip():
        common = resolve(Path(out.strip()))
        if common.name == ".git":
            return common.parent
    return repo


def project_key(path: Path) -> str:
    """Name Claude Code gives a project's directory under its projects folder."""
    return NOT_KEY_CHAR.sub("-", str(path))


def display(path: Path, repo: Path, home: Path) -> str:
    """Show a path relative to the repository, then to the home directory, else absolute."""
    for base, prefix in ((repo, ""), (home, "~/")):
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        text = relative.as_posix()
        return (prefix + text) if text != "." else (prefix.rstrip("/") or ".")
    return path.as_posix()


def report_root(repo: Path, environ: Mapping[str, str], out: str | None) -> Path:
    """Return where this repository's reports go: the per-run choice, the variable, or in-repo."""
    chosen = out or environ.get(REPORT_DIR_ENV, "")
    if chosen:
        return resolve(Path(chosen).expanduser()) / project_key(repo)
    return repo.joinpath(*IN_REPO_REPORT_DIR)


def in_directory(path: Path, directory: Path) -> bool:
    """True when path is directory or lies under it."""
    try:
        _ = path.relative_to(directory)
    except ValueError:
        return False
    return True
