#!/usr/bin/env python3
"""PostToolUse hook: after a SKILL.md is written, ask Claude to offer (or run) a skill audit.

Reads the hook event on stdin. Mode comes from the plugin option on_skill_write
(environment variable CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE): suggest (default), run or off.
Notifies once per skill directory per session; state lives in CLAUDE_PLUGIN_DATA.
Never blocks: any problem ends the hook silently with exit 0.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

MODES = ("suggest", "run", "off")
DEFAULT_MODE = "suggest"
STATE_MAX_AGE = 30 * 24 * 3600  # seconds; older per-session state files are removed


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def text_at(value: object, *keys: str) -> str:
    """Return the string under keys in nested JSON objects, or "" when absent or not a string."""
    for key in keys:
        if not isinstance(value, JsonObject):
            return ""
        value = value.get(key)
    return value if isinstance(value, str) else ""


def message(mode: str, skill_dir: str) -> str:
    """Return the context Claude gets for a written skill, by mode (run or suggest)."""
    command = f'/skill-diagnostics:audit "{skill_dir}"'
    if mode == "run":
        return (
            f"skill-diagnostics: the skill at {skill_dir} was created or changed. "
            f"When the skill is finished, run {command} and include its verdict in your reply."
        )
    return (
        f"skill-diagnostics: the skill at {skill_dir} was created or changed. "
        f"When the skill is finished, offer the user an audit with {command}. "
        "Run it only if the user agrees, and offer it once."
    )


def prune(folder: Path) -> None:
    """Remove state files of sessions older than STATE_MAX_AGE."""
    cutoff = time.time() - STATE_MAX_AGE
    for old in folder.glob("*.txt"):
        try:
            if old.stat().st_mtime < cutoff:
                old.unlink()
        except OSError:
            pass


def inside(path: str, root: str) -> bool:
    """True when path is root or below it, on whole path segments."""
    root = root.rstrip("/")
    return bool(root) and (path == root or path.startswith(root + "/"))


def already_notified(data_dir: str, session: str, skill_dir: str) -> bool:
    """Record the skill for this session; True when it was recorded before."""
    if not data_dir:
        return False
    folder = Path(data_dir) / "notified"
    folder.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(session.encode("utf-8")).hexdigest()[:32]
    log = folder / f"{key}.txt"
    if not log.exists():
        prune(folder)  # once per session, when its state file is created
    seen = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    if skill_dir in seen:
        return True
    with log.open("a", encoding="utf-8") as handle:
        _ = handle.write(skill_dir + "\n")
    return False


def main() -> int:
    """Handle one PostToolUse event from stdin; always returns 0."""
    mode = os.environ.get("CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE", DEFAULT_MODE).strip().lower()
    if mode not in MODES:
        mode = DEFAULT_MODE
    if mode == "off":
        return 0
    event = _decode(sys.stdin.read())
    path = Path(text_at(event, "tool_input", "file_path"))
    if path.name != "SKILL.md":
        return 0
    skill_dir = str(Path(os.path.normpath(path.absolute())).parent)
    normalized = skill_dir.replace("\\", "/")
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").replace("\\", "/")
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path("~").expanduser() / ".claude")
    managed = [
        str(Path(config_dir).joinpath(*parts)).replace("\\", "/")
        for parts in (("plugins",), ("skills", "synced"))
    ]
    # Claude Code overwrites files in these folders, so an audit offer there is useless.
    if any(inside(normalized, folder) for folder in managed) or inside(normalized, plugin_root):
        return 0
    if already_notified(
        os.environ.get("CLAUDE_PLUGIN_DATA", ""), text_at(event, "session_id"), skill_dir
    ):
        return 0
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message(mode, skill_dir),
        }
    }
    _ = sys.stdout.write(json.dumps(output) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    # Never block the user's work: bad input (ValueError covers JSON and Unicode errors),
    # an unexpected event shape, file system errors and an unknown home directory all end here.
    except (OSError, ValueError, LookupError, TypeError, AttributeError, RuntimeError):
        sys.exit(0)
