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
import sys
from pathlib import Path

MODES = ("suggest", "run", "off")
DEFAULT_MODE = "suggest"


def message(mode: str, skill_dir: str) -> str:
    command = f"/skill-diagnostics:audit {skill_dir}"
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


def already_notified(data_dir: str, session: str, skill_dir: str) -> bool:
    """Record the skill for this session; True when it was recorded before."""
    if not data_dir:
        return False
    folder = Path(data_dir) / "notified"
    folder.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(session.encode("utf-8")).hexdigest()[:32]
    log = folder / f"{key}.txt"
    seen = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    if skill_dir in seen:
        return True
    with log.open("a", encoding="utf-8") as handle:
        handle.write(skill_dir + "\n")
    return False


def main() -> int:
    mode = os.environ.get("CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE", DEFAULT_MODE).strip().lower()
    if mode not in MODES:
        mode = DEFAULT_MODE
    if mode == "off":
        return 0
    event = json.load(sys.stdin)
    file_path = str(event.get("tool_input", {}).get("file_path", ""))
    if os.path.basename(file_path) != "SKILL.md":
        return 0
    skill_dir = os.path.dirname(file_path)
    normalized = skill_dir.replace("\\", "/")
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").replace("\\", "/")
    if "/plugins/cache/" in normalized or (plugin_root and normalized.startswith(plugin_root)):
        return 0
    if already_notified(os.environ.get("CLAUDE_PLUGIN_DATA", ""), str(event.get("session_id", "")), skill_dir):
        return 0
    output = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": message(mode, skill_dir)}}
    sys.stdout.write(json.dumps(output) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # never block the user's work
        sys.exit(0)
