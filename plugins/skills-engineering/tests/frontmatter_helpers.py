"""Shared helpers for the frontmatter check tests: paths, JSON narrowing and script runs.

Every check is run the way the main session runs it, through `frontmatter-checks.py`, on a
throwaway skill folder, so the tests see exactly the bytes a reviewer would receive.
"""

from collections.abc import Callable
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TypeGuard

# Tests that import the scripts in process put SCRIPTS on sys.path after importing this module;
# without this, Python would write bytecode into the plugin's scripts folder.
sys.dont_write_bytecode = True

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ENTRY = SCRIPTS / "frontmatter-checks.py"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded JSON value to an array."""
    return isinstance(value, list)


def parse_object(text: str) -> JsonObject:
    """Parse one line of JSON that must be an object."""
    data = parse_json(text)
    if not isinstance(data, JsonObject):
        msg = f"expected one JSON object, got: {text!r}"
        raise TypeError(msg)
    return data


def run_python(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    python: str = sys.executable,
) -> subprocess.CompletedProcess[str]:
    """Run a Python command line and capture its text output, decoded as UTF-8."""
    return subprocess.run(
        [python, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=cwd,
        env=env,
    )


def run_check(
    check_id: str,
    skill_md: str | bytes,
    *,
    folder: str = "demo-skill",
    args: tuple[str, ...] = (),
    python: str = sys.executable,
) -> tuple[int, JsonObject]:
    """Write <tmp>/<folder>/SKILL.md, run one check on it, return the exit code and its JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = Path(tmp) / folder / "SKILL.md"
        skill.parent.mkdir(parents=True)
        if isinstance(skill_md, bytes):
            _ = skill.write_bytes(skill_md)
        else:
            _ = skill.write_text(skill_md, encoding="utf-8", newline="")
        done = run_python([str(ENTRY), "check", check_id, str(skill), *args], python=python)
    if done.returncode != 0:
        return done.returncode, JsonObject()
    return done.returncode, parse_object(done.stdout)


def rules(result: JsonObject) -> list[tuple[str, int | None]]:
    """The (rule, line) pairs of a result's findings, in the order printed."""
    findings = result.get("findings")
    items = findings if is_list(findings) else []
    pairs: list[tuple[str, int | None]] = []
    for item in items:
        if isinstance(item, JsonObject):
            line = item.get("line")
            pairs.append((str(item.get("rule")), line if isinstance(line, int) else None))
    return pairs
