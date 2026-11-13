#!/usr/bin/env python3
"""Shared pieces of the plugin hook tests: an isolated PATH, stub tools, Git fixtures, a runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import TYPE_CHECKING, NamedTuple, cast
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

PLUGINS = Path(__file__).resolve().parents[3] / "plugins"
_decode: Callable[[str], object] = json.JSONDecoder().decode

# A stub tool logs its name and arguments, then exits with STUB_EXIT_<name> (0 by default).
STUB = """#!/usr/bin/env bash
name="${0##*/}"
printf '%s %s\\n' "${name}" "$*" >> "${STUB_LOG}"
code_var="STUB_EXIT_${name}"
exit "${!code_var:-0}"
"""

# A neutral Git identity and configuration, so the maintainer's own settings never apply.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}
# A commit date long before any test session, for the commits a repository already had.
LONG_AGO = "2026-01-01T00:00:00Z"


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


def need(name: str) -> str:
    """The path of tool `name`; the test is skipped when it is not installed."""
    found = shutil.which(name)
    if found is None:
        message = f"{name} is not installed"
        raise unittest.SkipTest(message)
    return found


def tool_dir(tmp: Path, real: tuple[str, ...], stubs: tuple[str, ...] = ()) -> Path:
    """A folder to stand as the whole PATH: links to the real tools named, plus stub tools."""
    folder = tmp / "bin"
    folder.mkdir()
    for name in real:
        (folder / name).symlink_to(need(name))
    for name in stubs:
        stub = folder / name
        _ = stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
    return folder


def run_hook(argv: list[str], event: dict[str, object], env: dict[str, str]) -> Outcome:
    """Run a hook command with event on stdin and exactly env as its environment."""
    done = subprocess.run(
        argv, input=json.dumps(event), env=env, capture_output=True, text=True, check=False
    )
    return Outcome(done.returncode, done.stdout, done.stderr)


def git(folder: Path, *args: str, when: str = "") -> None:
    """Run git in folder with the neutral configuration; `when` dates a commit it creates."""
    env = {**os.environ, **GIT_ENV}
    if when:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    _ = subprocess.run(
        [need("git"), "-C", str(folder), *args], env=env, check=True, capture_output=True
    )


def write(path: Path, text: str) -> None:
    """Write text to path, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")


def repository(folder: Path, files: dict[str, str]) -> None:
    """Create folder as a Git repository whose only commit, made long ago, holds files."""
    folder.mkdir(parents=True)
    git(folder, "init", "-q", "-b", "main")
    for name, text in files.items():
        write(folder / name, text)
    git(folder, "add", "-A")
    git(folder, "commit", "-q", "-m", "first", when=LONG_AGO)


def clone(origin: Path, target: Path) -> None:
    """Clone origin into target, as a session's `git clone` does."""
    target.parent.mkdir(parents=True, exist_ok=True)
    git(target.parent, "clone", "-q", str(origin), str(target))


def age(path: Path, seconds: int) -> None:
    """Set the modification time of path, and of everything under it, to `seconds` ago."""
    then = time.time() - seconds
    targets = [path, *path.rglob("*")] if path.is_dir() else [path]
    for target in targets:
        os.utime(target, (then, then))


def logged(log: Path) -> list[str]:
    """The stub calls logged so far, one per line."""
    return log.read_text(encoding="utf-8").splitlines() if log.is_file() else []


def field(stdout: str, *keys: str) -> str:
    """The string under keys in the JSON object a hook printed; "" when absent or not text."""
    value = _decode(stdout)
    for key in keys:
        if not isinstance(value, dict):
            return ""
        value = cast("dict[str, object]", value).get(key)
    return value if isinstance(value, str) else ""
