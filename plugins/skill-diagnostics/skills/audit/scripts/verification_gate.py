#!/usr/bin/env python3
"""Stop hook of the audit skill: an audit turn does not end before step 5 ran.

Registered by the skill's own frontmatter, so it exists only in sessions where
the audit was invoked. At the end of a turn that invoked the audit and produced
a verdict, it checks the session transcript for an attempt to fetch each required
change source (with any tool: WebFetch, a docs MCP server, curl), and the report for its Verification line.
When something is missing it tells Claude what, once per turn (stop_hook_active).
A fetch that failed counts as attempted: unreachable sources are the report's
business, never a reason to keep the turn going.

Never blocks on its own failure: any problem ends the hook silently with exit 0.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

Entry = dict[str, Any]

AUDIT_SKILL = "skill-diagnostics:audit"
# Change sources step 5 must try (references/verification.md, Recent official changes).
SOURCES = {
    "the Claude Code changelog (https://code.claude.com/docs/en/changelog)": "code.claude.com/docs/en/changelog",
    "the Claude apps release notes (https://support.claude.com/en/articles/12138966-release-notes)": (
        "support.claude.com/en/articles/12138966"
    ),
    "the Agent Skills specification (https://agentskills.io/specification)": "agentskills.io/specification",
}


def is_prompt(entry: Entry) -> bool:
    """A message the user typed: not a tool result, not text Claude Code injected."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    return isinstance(content, list) and all(isinstance(part, dict) and part.get("type") == "text" for part in content)


def tool_uses(entry: Entry) -> list[Entry]:
    if entry.get("type") != "assistant" or entry.get("isSidechain"):
        return []
    content = (entry.get("message") or {}).get("content")
    if not isinstance(content, list):
        return []
    return [part for part in content if isinstance(part, dict) and part.get("type") == "tool_use"]


def current_turn(transcript: Path) -> list[Entry]:
    """Transcript entries from the last typed prompt on."""
    entries = []
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    start = max((i for i, entry in enumerate(entries) if is_prompt(entry)), default=0)
    return entries[start:]


def audit_ran(turn: list[Entry]) -> bool:
    if turn and AUDIT_SKILL in json.dumps((turn[0].get("message") or {}).get("content", "")):
        return True  # typed as /skill-diagnostics:audit
    return any(
        use.get("name") == "Skill" and str((use.get("input") or {}).get("skill", "")) == AUDIT_SKILL
        for entry in turn
        for use in tool_uses(entry)
    )


def fetched(turn: list[Entry]) -> list[str]:
    """The input of every tool call the main thread made, as text: any tool that names a source counts."""
    return [json.dumps(use.get("input") or {}) for entry in turn for use in tool_uses(entry)]


def gaps(event: Entry) -> list[str]:
    if event.get("stop_hook_active"):
        return []
    reply = str(event.get("last_assistant_message") or "")
    if "Verdict" not in reply:
        return []  # no report yet, for example a question to the user
    turn = current_turn(Path(str(event.get("transcript_path", ""))))
    if not audit_ran(turn):
        return []
    urls = fetched(turn)
    missing = [f"fetch {name}" for name, marker in SOURCES.items() if not any(marker in url for url in urls)]
    if "Verification:" not in reply:
        missing.append("end the Coverage section with the template's `- Verification:` line")
    return missing


def main() -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}")
        todo = gaps(event)
    except Exception:  # never stop the user's work over the gate itself
        return 0
    if todo:
        context = (
            "skill-diagnostics: step 5 of the audit is not complete. Before you finish: "
            + "; ".join(todo)
            + ". Follow references/verification.md: check what changed in the last 15 days, record each source"
            " as checked with its date range or as unreachable (a fetch you tried that failed), update findings"
            " and the verdict, then reply with the full report again."
        )
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
